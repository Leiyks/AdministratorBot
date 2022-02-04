# Administrator bot

## Overview
This is a quickly custom discord bot that allows the followings features:
- Automatic creation / deletion of text and voice channels.
- Bunch of commands to generate random outcomes.
- The Flags game to learn every flags in the world !

## Installation
This bot runs with Replit, but to make it works without having the replit page open forever or a paid account, we need to use a trick described below.

But first you need to follow the basic installation steps described in the video in the `Ressources` section (5 first minutes).
You also need to follow those steps to use this bot:
* Create an account on Replit and setup a Repl using the `import from github` option.
* Setup the following environment variables:
    - `TOKEN`: Your own bot token
    - `CHANNEL_ID`: The voice channel id used to create custom public channels
    - `PRIVATE_CHANNEL_ID`: The voice channel id used to create custom private channels
    - `CATEGORY_ID`: The channel category id in which you want channels to appear.

The trick mentionned before to make sure the bot do not get killed by Replit is to setup a Flask server and ping it before Replit kill the bot. The Flask part is handled by the code itself, however we still need to use a bot that constantly ping a url.  
To do that you can get the url after running the bot on Replit and just use [UptimeRobot](https://uptimerobot.com/) to setup the pinging bot.  

If you have hard time with this part, please refer to the aforementionned video.

## Ressources
[Original video about bot Installation](https://www.youtube.com/watch?v=SPTfmiYiuok)