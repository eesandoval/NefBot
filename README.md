# NefBot - A Discord Bot for Dragalia Lost
[![Build Status](https://travis-ci.org/eesandoval/NefBot.svg?branch=master)](https://travis-ci.org/eesandoval/NefBot)
1. [About](#about)
2. [Features](#features)
3. [Installation](#installation)
4. [Issues](#issues)
5. [License](#license)

# About
## Summary
A simple discord bot used to gather information from the Dragalia Lost mobile game. It is able to pull up information from the game including adventurers, dragons, wyrmprints, and weapons. It can also query the database it uses to find any of the three with a combination of elements (weapon, element, abilities, etc).

# Features
## Searching By Name
<img src="https://i.imgur.com/nZZtcls.png" width="400">

You can search for adventurers, dragons, and wyrmprints with the following command
```
^(a|d|w|wep) [name]
```
Where a = adventurers, d = dragons, w = wyrmprints, and wep = weapons. Names are not case sensitive and you can use incomplete names as well. Additionally, if multiple results would be found, the earliest one released in game will be pulled. 

## Searching By Alias
<img src="https://i.imgur.com/FIsel3B.png" width="400">

Searching for aliases allows for an easy way to search for items without remembering the full name. Out of the box the bot comes with pre-defined names (such as HElly -> Halloween Elisanne)

## Setting Aliases
<img src="https://i.imgur.com/JsDwifI.png" width="400">

In addition to searching using an alias, you can also set your own aliases. The command to do so is

```
^alias [alias_text] [alias_name]
```
Where the first parameter will be the text you use to search for, and the second parameter will be the object it refers to. Use quotations around text that has spaces. Repeating this command will edit the alias.

You can also delete an alias using the same command but omitting the second parameter:
```
^alias [alias_text]
```

## Reactions as Buttons
### Bind Levels
<img src="https://i.imgur.com/vw0uDiB.png" width="400">

Bind levels can now be adjusted using the speaker reactions. The first speaker (with no noise) will denote 0 unbinds

<img src="https://i.imgur.com/GVD1jwN.png" width="400">

The next speaker will denote 2 unbinds for Adventurers and Wyrmprints. For Dragons and Weapons, this is their max unbind as they only change once when unbinding currently

<img src="https://i.imgur.com/2VUqozO.png" width="400">

The final speaker denotes a max unbind for Adventurers and Wyrmprints. Note that when speaking of unbind levels on Adventurers, it refers to their skill and ability levels (where MUB = max skills and max abilities, 2UB = level 2 skills and max abilites, and 0UB = level 1 skills and level 1 abilities)

### Full Images
<img src="https://i.imgur.com/uVHnuFG.png" width="400">

You can also view the full image of these characters and items using the portrait reaction button. 

<img src="https://i.imgur.com/dTdCdGn.png" width="400">

Wyrmprints include an additional reaction to view the refined version as well.

### Upgrade Paths
<img src="https://i.imgur.com/CETElXn.png" width="400">

When pulling up weapons, using the fast foward reaction button you can view the upgrade path this weapon can take, as well as the materials needed. 

<img src="https://i.imgur.com/It9KUj3.png" width="400">

Additionally, as seen above, there exists a rewind reaction to view where this weapon comes from and the materials needed.

## Querying
<img src="https://i.imgur.com/mAN92XY.png" width="400">

You can use a query function to find adventurers, dragons, wyrmprints, or weapons with specific skills, abilities, rarities, element, weapon, etc.
```
^query key=value
```
Key is defined as an attribute (such as element or weapon) where value is the value of the key. Multiple key value pairs can be given. If the value has spaces, surround it with quotes. Below is an example searching for anything with the Bog Res ability at 100% and with an element of wind.
```
^query ability="Bog Res +100%" element=Wind
```
A list of items will appear, and the user can specify the number to select the option they want.

## Additional Commands

For help with any additional commands, please see the help menu using the below command
```
^help
```

# Installation
## Requirements
- [Python 3.6 or higher](https://www.python.org/)
- [discord.py (rewrite branch)](https://github.com/Rapptz/discord.py)

## Instructions 
1. If not installed, download [Python 3.6 or higher](https://www.python.org) 
2. Once installed, open a command prompt window or terminal window and type the following to install [discord.py](https://github.com/Rapptz/discord.py):
```
python -m pip install -U discord.py
```
3. Go to the [DiscordApp developers application site](https://discordapp.com/developers/applications) and create a New Application
4. Name the application anything you'd like
5. Note down the Client ID, you can copy this and save it for now
6. Select Bot on the left hand side, and create a new bot
7. Visit the following URL, replacing the CLIENT_ID in it with the client id you copied down: https://discordapp.com/oauth2/authorize?client_id=CLIENT_IDscope=bot
8. Select the server you want the bot to appear in
9. Copy the token from the bot page
10. Copy the example config file and rename it: config_example.ini -> config.ini
11. Set the TOKEN parameter in the config.ini file 
12. Optional: Set additional parameters in the config.ini as desired
13. Run the bot using the following command in the command prompt or terminal 
```
python main.py
```

# Issues
For any issues please submit the <b>command entered along with the output from the command prompt or terminal</b>. This will give the full stack trace exception and the command will allow for debugging any particular issues.

# LICENSE
This project is licensed under the [MIT License](https://github.com/eesandoval/NefBot/blob/master/LICENSE).