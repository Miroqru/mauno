# UNO Bot

![](./logo.png)

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](./LICENSE)

This repository is a **fork** for: [Mau Mau bot](https://github.com/jh0ker/mau_mau_bot).

Telegram Bot that allows you to play the popular card game UNO via inline queries.
The bot currently runs as [@unobot](https://t.me/mili_maubot).

To run the bot yourself, you will need:
- Python (tested with 3.4+).
- The [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) module.
- [Pony ORM](https://ponyorm.com/).

## Setup
- Get a bot token from [@BotFather](http://telegram.me/BotFather) and change configurations in `config.json`.
- Use `/setinline` and `/setinlinefeedback` with BotFather for your bot.
- Use `/setcommands` and submit the list of commands in commandlist.txt
- Install requirements (using a `virtualenv` is recommended): `pip install -r requirements.txt`

You can change some gameplay parameters like turn times, minimum amount of players and default gamemode in `config.json`.
Current gamemodes available: classic, fast and wild. Check the details with the `/modes` command.

Then run the bot with `python bot.py`.

## Changes
What has been changed compared to the original:

- Remove Cuber, Docker, Renovate, Github workflow.
