# Need to install pip dependency via the code
# Replit seems to uninstall them after 24 hours
import os

os.system("pip install flagpy discord-components")

import discord
import flagpy as fp
import random

from discord_components import DiscordComponents, Button, ButtonStyle
from discord.ext import commands
from replit import db
from keep_alive import keep_alive

### VARIABLES ###
DEBUG = False
CREATE_CHANNEL_ID = 903671826251677727 if DEBUG else 914219697162043442
CREATE_PRIVATE_CHANNEL_ID = 908857680863559710 if DEBUG else 914219736135524403
CATEGORY_ID = 913817330449014844 if DEBUG else 913815132600172575
VOICE_CHANNEL_NAME = '{} cabin'
TEXT_CHANNEL_NAME = '{} logbook'

### RUNNER ###
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)

### CHANNEL HANDLING ###
# HELPERS
ALLOWED_PERMISSIONS = {
    "read_messages": True,
    "send_messages": True,
    "connect": True,
    "speak": True,
    "view_channel": True,
    "manage_permissions": True
}
RESTRICTED_PERMISSIONS = {
    "read_messages": False,
    "send_messages": False,
    "connect": False,
    "speak": False,
    "view_channel": False,
    "manage_permissions": False
}


@client.event
async def on_guild_channel_update(before, after):
    text_channels_ids = [
        int(db[key]) if type(db[key]) == str else None for key in db.keys()
    ]

    if before.id not in text_channels_ids:
        return

    voice_channels_ids = [int(key) for key in db.keys()]
    index = text_channels_ids.index(before.id)
    voice_channel = discord.utils.get(before.guild.channels,
                                      id=voice_channels_ids[index])

    added_members = [
        member for member in after.members if member not in before.members
    ]
    removed_members = [
        member for member in before.members if member not in after.members
    ]

    for member in removed_members:
        await voice_channel.set_permissions(member, **RESTRICTED_PERMISSIONS)

    for member in added_members:
        await voice_channel.set_permissions(member, **ALLOWED_PERMISSIONS)
        await after.set_permissions(member, **ALLOWED_PERMISSIONS)
        try:
            await member.move_to(voice_channel)
        except Exception:
            continue


async def create_channel(member, position, private=False):
    voice_channel_name = VOICE_CHANNEL_NAME.format(member.name)
    text_channel_name = TEXT_CHANNEL_NAME.format(member.name)

    category = client.get_channel(CATEGORY_ID)
    overwrites = None if not private else {
        member.guild.default_role:
        discord.PermissionOverwrite(**RESTRICTED_PERMISSIONS),
        member:
        discord.PermissionOverwrite(**ALLOWED_PERMISSIONS)
    }

    # Create voice channel
    voice_channel = await member.guild.create_voice_channel(
        voice_channel_name,
        category=category,
        overwrites=overwrites,
        video_quality_mode=2,
        bitrate=96000)

    # Create text channel
    text_channel = await member.guild.create_text_channel(
        text_channel_name, category=category, overwrites=overwrites)

    db[str(voice_channel.id)] = str(text_channel.id)
    await member.move_to(voice_channel)


@client.event
async def on_voice_state_update(member, before, after):
    if before.channel:
        id = str(before.channel.id)

        if id in db and not before.channel.members:
            text_channel = discord.utils.get(member.guild.channels,
                                             id=int(db[id]))
            del db[id]
            await text_channel.delete()
            await before.channel.delete()

    if after.channel:
        if after.channel.id == CREATE_CHANNEL_ID:
            await create_channel(member, after.channel.category.position)
        elif after.channel.id == CREATE_PRIVATE_CHANNEL_ID:
            await create_channel(member,
                                 after.channel.category.position,
                                 private=True)


### RANDOM COMMANDS ###


@client.command(help='You can pass any number of choices to the command !',
                brief='Choose a random value among all the given choices.')
async def choice(ctx, *args):
    if not args:
        await ctx.reply('```You need to give at least one choice !```')
        return
    choice = random.choice(args)
    await ctx.reply(f'```I choose \'{choice}\' ^^ !```')


@client.command(brief='Give the result of a coinflip.')
async def coinflip(ctx):
    choice = random.choice(['head', 'tail'])
    await ctx.reply(f'```It\'s {choice} !```')


@client.command(help='You must pass two number to the command !',
                brief='Choose a random number in a range.')
async def rnd(ctx, min, max):
    if not min or not max:
        await ctx.reply('```You need to give two args fucker !```')
    try:
        min = int(min)
        max = int(max)
    except Exception:
        await ctx.reply('```You must give two numbers !```')
    if min >= max:
        await ctx.reply('```First number must be lower that the second !```')
    else:
        choice = random.randint(min, max)
        await ctx.reply(f'```You got \'{choice}\' !```')


### FLAGS GAME ###

# HELPERS
COMPONENTS = [[Button(label="Reroll"),
               Button(label="Verify")],
              Button(style=ButtonStyle.red, label="Done")]
COMPONENTS_VERIFY = [[
    Button(label="Reroll"),
    Button(label="Verify", disabled=True),
    Button(style=ButtonStyle.green, label="True"),
    Button(style=ButtonStyle.blue, label="False")
],
                     Button(style=ButtonStyle.red, label="Done")]
COMPONENTS_LAST = [[
    Button(style=ButtonStyle.red, label="Done"),
    Button(label="Verify")
]]
COMPONENTS_LAST_VERIFY = [[
    Button(style=ButtonStyle.red, label="Done"),
    Button(label="Verify", disabled=True),
    Button(style=ButtonStyle.green, label="True"),
    Button(style=ButtonStyle.blue, label="False")
]]


# Send Flag message
async def get_random_flag(channel):
    # Flags random selection
    values = db[str(channel.id)]
    country = random.choice(values['LIST'])
    fp.get_flag_img(country).save('tmp.png', format='PNG')
    values['LIST'].remove(country)

    # Response handling
    size = len(values['LIST']) + 1
    NB_COUNTRY = values['NB_COUNTRY']
    content = f'```What is this flag ? ({size} / {NB_COUNTRY})```'
    components = COMPONENTS if size > 1 else COMPONENTS_LAST
    components[0][1].custom_id = country
    await channel.send(content=content,
                       file=discord.File('tmp.png'),
                       components=components)


# Button handling
@client.event
async def on_button_click(interaction):
    id = str(interaction.channel.id)
    values = db[id] if id in db else None

    if interaction.component.label == 'Verify':
        content = f'```The Answer is \'{interaction.component.id}\' !```'
        components = COMPONENTS_VERIFY if values[
            'LIST'] else COMPONENTS_LAST_VERIFY
        components[0][2].disabled = True
        components[0][3].disabled = False
        values['NB_POINT'] += 1
        await interaction.edit_origin(content=content, components=components)

    elif interaction.component.label == 'True':
        components = COMPONENTS_VERIFY if values[
            'LIST'] else COMPONENTS_LAST_VERIFY
        if components[0][3].disabled:
            values['NB_POINT'] += 1
        components[0][2].disabled = True
        components[0][3].disabled = False
        await interaction.edit_origin(content=interaction.message.content,
                                      components=components)

    elif interaction.component.label == 'False':
        components = COMPONENTS_VERIFY if values[
            'LIST'] else COMPONENTS_LAST_VERIFY
        if components[0][2].disabled:
            values['NB_POINT'] -= 1
        components[0][2].disabled = False
        components[0][3].disabled = True
        await interaction.edit_origin(content=interaction.message.content,
                                      components=components)

    elif interaction.component.label == 'Replay':
        await interaction.message.delete()
        await flags(interaction)

    elif interaction.component.label == 'Done' or not values['LIST']:
        await interaction.message.delete()
        NB_POINT = values['NB_POINT']
        content = f'```Congrats, you got {NB_POINT} flags right !```'
        await interaction.channel.send(
            content=content,
            components=[Button(label="Replay", style=ButtonStyle.blue)])
        del db[str(interaction.channel.id)]

    elif interaction.component.label == 'Reroll':
        await interaction.message.delete()
        if values['LIST']:
            await get_random_flag(interaction.channel)


# Command
@client.command(
    help=
    'Display a flag, you must guess which one it is ! (Maybe with a score system one day)',
    brief='Play a game of \'Guess the flag\'.')
async def flags(ctx):
    id = str(ctx.channel.id)
    if id in db:
        await ctx.reply(
            content='```You can\'t start another game in this channel !```')
        return

    country_list = fp.get_country_list()
    db[id] = {
        'NB_POINT': 0,
        'LIST': country_list,
        'NB_COUNTRY': len(country_list)
    }
    await get_random_flag(ctx.channel)


### BOT CONNECTICITY CONTENT ###


@client.event
async def on_ready():
    DiscordComponents(client)
    await client.change_presence(activity=discord.Game(name=f"!help"))
    print("Bot has successfully logged in as: {}".format(client.user))
    print("Bot ID: {}".format(client.user.id))


keep_alive()
client.run(os.environ['TOKEN'])
