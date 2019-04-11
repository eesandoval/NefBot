A Dragalia Lost bot that gives information on Adventurers, Dragons, and Wyrmprints

## Requirements
- [Python 3.6 or higher](https://www.python.org/)
- [discord.py 0.16.12](https://github.com/Rapptz/discord.py). You can install this by opening a command prompt or terminal window and typing the following:
```
python -m pip install discord.py==0.16.12
```

## Installation 
1. Go to the [DiscordApp developers application site](https://discordapp.com/developers/applications) and create a New Application
![Creating the application](https://i.imgur.com/fqe68Zn.gif)
2. Name the application anything you'd like
![Naming the application](https://i.imgur.com/lV71FFb.gif)
3. Note down the Client ID, you can copy this and save it for now
![Saving the client id](https://i.imgur.com/vyebJAi.gif)
4. Select Bot on the left hand side, and create a new bot
![Creating a new bot for the application](https://i.imgur.com/lSAMUAo.gif)
5. Visit the following URL, replacing the CLIENT_ID in it with the client id you copied down in step 3: https://discordapp.com/oauth2/authorize?client_id=CLIENT_IDscope=bot
6. Select the server you want the bot to appear in
![Selecting the server for the bot to appear in](https://i.imgur.com/9zE2CtP.gif)
7. Copy the token from the bot page
![Copying the bot token](https://i.imgur.com/KxaJykR.gif)
8. Set the TOKEN parameter in the config_example.py file that you copied from step 7 in the file
![Setting the bot token](https://imgur.com/M3hS1k5.gif)
9. Change the name of the config_example.py -> config.py
10. Install d
10. Run the bot using the following command in the command prompt or terminal 
```
python main.py
```

## Features
Searching for adventurers, dragons, and wyrmprints with the following command:
```
^(adv|wyr|dra) [name] [level]
```
Names are not case sensitive. Additionally, if multiple results would be found, they are sorted by release date in descending order. Level is an optional attribute that will list the abilities/skills of the search result. If level=1, then this gives a 0 unbind wyrmprint or dragon. If level=2, then this gives a max unbound wyrmprint or dragon. This only works with wyrmprints and dragons currently. By default the level is set to 2.

There exists additionally a query function to find adventurers, dragons, or wyrmprints with specific skills, abilities, rarities, element, weapon, etc.
```
^query type=(adv|wyr|dra) key=value
```
Key is defined as an attribute (such as element or weapon) where value is the value of the key. Multiple key value pairs can be given. If the value has spaces, surround it with quotes. Below is an example searching for water axe adventurers with the Freeze Res ability.
```
^query type=adv element=Water ability="Freeze Res" weapon=Axe
```
Be warned this will return ALL results, and may spam the chat log. Use at your own discretion.

## LICENSE
This project is licensed under the [MIT License](https://github.com/eesandoval/NefBot/blob/master/LICENSE).