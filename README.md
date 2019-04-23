# NefBot - A Discord Bot for Dragalia Lost
[![Build Status](https://travis-ci.org/eesandoval/NefBot.svg?branch=master)](https://travis-ci.org/eesandoval/NefBot)
1. [About](#about)
2. [Installation](#installation)
3. [Issues](#issues)
4. [License](#license)

# About
## Summary
A simple discord bot used to gather information from the Dragalia Lost mobile game. It is able to pull up information regarding adventurers, dragons, and wyrmprints as well as querying the database it uses to find any of the three with a combination of elements (weapon, element, abilities, etc).
## Searching By Name
<img src="https://i.imgur.com/AAhkUcC.png" width="400">

You can search for adventurers, dragons, and wyrmprints with the following command
```
^(a|d|w) [name]
```
Where a = adventurers, d = dragons, and w = wyrmprints. Names are not case sensitive and you can use incomplete names as well. Additionally, if multiple results would be found, the earliest one released in game will be pulled. 

## Adjusting Bind Level
### 0UB
<img src="https://i.imgur.com/Of9H1xD.png" width="400">

### MUB
<img src="https://i.imgur.com/sByB0kt.png" width="400">

You can now view the adventurers, dragons, or wyrmprints at different bind levels using the reactions at the bottom of the message. Ticking the sound button that is lower will show the item at 0UB, while ticking the sound button at max will show the item at MUB. For adventurers, this bind level is determined by their skills and abilities with three different reactions to view them from level 1, 2, and 3. 

## Full Image View
<img src="https://i.imgur.com/90Lut8Y.png" width="400">

You can also view the full image of these characters and items using the portrait reaction button. 

## Querying
<img src="https://i.imgur.com/1rs8lfC.png" width="400">

There exists additionally a query function to find adventurers, dragons, or wyrmprints with specific skills, abilities, rarities, element, weapon, etc.
```
^query type=(a|w|d) key=value
```
Key is defined as an attribute (such as element or weapon) where value is the value of the key. Multiple key value pairs can be given. If the value has spaces, surround it with quotes. Below is an example searching for adventurers with the Bog Res ability at 100%.
```
^query type=adv ability="Bog Res +100%"
```
Be warned this will return ALL results, and may spam the chat log. Use at your own discretion.

## Additional Commands

For help with any additional commands, please see the help menu using the below command
```
^help
```

# Installation
## Requirements
- [Python 3.6 or higher](https://www.python.org/)
- [discord.py 0.16.12](https://github.com/Rapptz/discord.py)

## Instructions 
1. If not installed, download [Python 3.6 or higher](https://www.python.org) 
2. Once installed, open a command prompt window or terminal window and type the following to install [discord.py 0.16.12](https://github.com/Rapptz/discord.py):
```
python -m pip install discord.py==0.16.12
```
3. Go to the [DiscordApp developers application site](https://discordapp.com/developers/applications) and create a New Application
4. Name the application anything you'd like
5. Note down the Client ID, you can copy this and save it for now
6. Select Bot on the left hand side, and create a new bot
7. Visit the following URL, replacing the CLIENT_ID in it with the client id you copied down: https://discordapp.com/oauth2/authorize?client_id=CLIENT_IDscope=bot
8. Select the server you want the bot to appear in
9. Copy the token from the bot page
10. Set the TOKEN parameter in the config_example.py file that you copied from the previous stip into the file
11. Change the name of the config_example.py -> config.py
12. Run the bot using the following command in the command prompt or terminal 
```
python main.py
```

# Issues
For any issues please submit the <b>command entered along with the output from the command prompt or terminal</b>. This will give the full stack trace exception and the command will allow for debugging any particular issues.

# LICENSE
This project is licensed under the [MIT License](https://github.com/eesandoval/NefBot/blob/master/LICENSE).