A Dragalia Lost bot that gives information on Adventurers and Wyrmprints (Dragons coming soon)

## Requirements
- [Python 3.6 or higher](https://www.python.org/)

## Installation 
1. Go to the [DiscordApp developers application site](https://discordapp.com/developers/applications) and create a New Application, naming it whatever you wish, noting down the client ID
2. Select Bot on the left hand side, and create a new bot
3. Copy the token of this bot and paste it into the config_example.py for the TOKEN string
4. Visit the URL https://discordapp.com/oauth2/authorize?client_id=CLIENT_IDscope=bot, replacing the CLIENT_ID in the URL to what you noted down in step 1
5. Choose the server you want to add the bot to and select authorize
6. Set the TOKEN in the config_example.py file that you copied from step 3 in the file
7. Optional: Set the other items in the configuration file (such as the current event, a stream, the help text, picture server, etc)
8. Change the name of the config_example.py -> config.py
9. Run the bot in Python3 through the main.py 
```
python3 main.py
```

## LICENSE
This project is licensed under the [MIT License](https://github.com/eesandoval/NefBot/blob/master/LICENSE).