'''
MIT License

Copyright (c) 2019 Enrique Sandoval

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
from models.adventurer import Adventurer
from models.wyrmprint import Wyrmprint
from models.dragon import Dragon
import controller
import discord 
from shlex import shlex
from datetime import datetime
from configparser import ConfigParser

TOKEN = ""
CURRENT_EVENT = ""
PICTURE_SERVER = ""
STREAM_URL = ""
AUTHORIZED_IDs = []
COMMAND_START = ""
HELP_TEXT = ""
ELEMENT_EMOJI = {}
WEAPON_EMOJI = {}
UNIT_EMOJI = {}
RARITY_EMOJI = {}
AUTHORIZED_IDs = []

client = discord.Client()
channel = None 
active_adventurer_messages = {}
active_wyrmprint_messages = {}
active_dragon_messages = {}
adventurer_emojis = ["\U0001F5BC", "\U0001F508", "\U0001F509", "\U0001F50A"]
wyrmprint_emojis = ["\U0001F5BC", "\U0001F508", "\U0001F509"]
dragon_emojis = ["\U0001F5BC", "\U0001F508", "\U0001F509"]

def startDiscordBot():
	client.run(TOKEN)

async def exitDiscordBot():
	await client.send_message(channel, "Shutting down")
	await client.close()

def setViewConfig():
	global TOKEN, STREAM_URL, CURRENT_EVENT, COMMAND_START, ELEMENT_EMOJI, WEAPON_EMOJI, UNIT_EMOJI, RARITY_EMOJI, PICTURE_SERVER, HELP_TEXT, AUTHORIZED_IDs
	config = ConfigParser()
	config.read("config.ini")
	TOKEN = config["Discord"]["Token"]
	STREAM_URL = config["Discord"]["StreamURL"]
	CURRENT_EVENT = config["Discord"]["CurrentEvent"]
	COMMAND_START = config["Discord"]["CommandStart"]
	ELEMENT_EMOJI = dict(config.items("ElementEmojis"))
	WEAPON_EMOJI = dict(config.items("WeaponEmojis"))
	UNIT_EMOJI = dict(config.items("UnitEmojis"))
	RARITY_EMOJI = {int(k):v for k,v in config.items("RarityEmojis")}
	PICTURE_SERVER = config["Other"]["PictureServer"]
	HELP_TEXT = config["Other"]["HelpText"].format(COMMAND_START)
	
@client.event
async def on_message(message):
	if message.author == client.user:
		return 
	if message.content == None or message.content == "" or not(message.content[0] == COMMAND_START):
		return
	global channel
	channel = message.channel 
	receivedMessage = message.content.split()
	messageCommand = receivedMessage[0]
	messageContent = ""
	await client.send_typing(channel)
	if len(receivedMessage) > 1:
		messageContent = (' '.join(receivedMessage[1:])).strip()
	if messageCommand.startswith(COMMAND_START + "adv"):
		await controller.processAdventurer(messageContent)
	elif messageCommand.startswith(COMMAND_START + "wyr"):
		await controller.processWyrmprint(messageContent)
	elif messageCommand.startswith(COMMAND_START + "dra"):
		await controller.processDragon(messageContent)
	elif messageCommand.startswith(COMMAND_START + "query"):
		await controller.query(determineCriteria(messageContent))
	elif messageCommand.startswith(COMMAND_START + "exit") and (AUTHORIZED_IDs == [] or message.author.id in AUTHORIZED_IDs):
		await exitDiscordBot()
	elif messageCommand.startswith(COMMAND_START + "exit"):
		await client.send_message(channel, "User {0} is not authorized to shut down this bot.".format(message.author.name))
	elif messageCommand.startswith(COMMAND_START + "help"):
		await client.send_message(channel, HELP_TEXT)
	elif messageCommand.startswith(COMMAND_START + "update"):
		await controller.update()
	else:
		await client.send_message(channel, "Command not understood. Type {0}help for options".format(COMMAND_START))

@client.event 
async def on_ready():
	await client.change_presence(game=discord.Game(name=CURRENT_EVENT, url=STREAM_URL, type=1))

@client.event 
async def showAdventurer(adventurer, message=None):
	e = discord.Embed(title=adventurer.name + " - " + adventurer.title, desc=adventurer.title)
	portraitURL = PICTURE_SERVER + "adventurers/portraits/{0}.png".format("%20".join(adventurer.name.split()))
	e.set_thumbnail(url=portraitURL)
	e.add_field(name="Unit Type", value=getEmojiElement(adventurer.elementtype) + getEmojiWeapon(adventurer.weapontype) + getEmojiUnit(adventurer.unittype), inline=True)
	e.add_field(name="Rarity", value=getEmojiRarity(adventurer.rarity), inline=True)
	e.add_field(name="Max HP/Max STR", value="{0}/{1}".format(adventurer.maxhp, adventurer.maxstr), inline=True)
	e.add_field(name="Max Co-Op Ability", value=adventurer.maxcoop, inline=True)
	e.add_field(name="Defense", value=adventurer.defense, inline=True)
	e.add_field(name="Release Date", value=getHumanStringDate(adventurer.releasedate), inline=True)
	for skill in adventurer.skills:
		e.add_field(name="Skill: {0} [SP Cost: {1}] [Frame Time: {2}]".format(skill.name, skill.spcost, skill.frametime), value=skill.description, inline=False)
	for ability in adventurer.abilities:
		e.add_field(name="Ability: " + ability.name, value=ability.description, inline=False)
	await showOrEditAdventurer(e, adventurer, message)

@client.event 
async def showAdventurerNotFound(name):
	await client.send_message(channel, "Adventurer {0} not found".format(name))

@client.event 
async def showWyrmprint(wyrmprint, message=None):
	e = discord.Embed(title=wyrmprint.name, desc=wyrmprint.name)
	portraitURL = PICTURE_SERVER + "wyrmprints/portraits/{0}.png".format("%20".join(wyrmprint.name.split()))
	e.set_thumbnail(url=portraitURL)
	e.add_field(name="Rarity", value=getEmojiRarity(wyrmprint.rarity), inline=True)
	e.add_field(name="Max HP/Max STR", value="{0}/{1}".format(wyrmprint.maxhp, wyrmprint.maxstr), inline=True)
	e.add_field(name="Release Date", value=getHumanStringDate(wyrmprint.releasedate), inline=True)
	for ability in wyrmprint.abilities:
		e.add_field(name="Ability: " + ability.name, value=ability.description, inline=False)
	await showOrEditWyrmprint(e, wyrmprint, message)

@client.event 
async def showWyrmprintNotFound(name):
	await client.send_message(channel, "Wyrmprint {0} not found".format(name))

@client.event 
async def showDragon(dragon, message=None):
	e = discord.Embed(title=dragon.name, desc=dragon.name)
	portraitURL = PICTURE_SERVER + "dragons/portraits/{0}.png".format("%20".join(dragon.name.split()))
	e.set_thumbnail(url=portraitURL)
	e.add_field(name="Element", value=getEmojiElement(dragon.elementtype), inline=True)
	e.add_field(name="Rarity", value=getEmojiRarity(dragon.rarity), inline=True)
	e.add_field(name="Max HP/Max STR", value="{0}/{1}".format(dragon.maxhp, dragon.maxstr), inline=True)
	e.add_field(name="Release Date", value=getHumanStringDate(dragon.releasedate), inline=True)
	for skill in dragon.skills:
		e.add_field(name="Skill: " + skill.name, value=skill.description, inline=False)
	for ability in dragon.abilities:	
		e.add_field(name="Ability: " + ability.name, value=ability.description, inline=False)
	await showOrEditDragon(e, dragon, message)
	
@client.event 
async def showDragonNotFound(name):
	await client.send_message(channel, "Dragon {0} not found".format(name))

@client.event
async def showInvalidName():
	await client.send_message(channel, "Invalid/no name given")

@client.event 
async def showMissingCriteria(missingCriteria):
	await client.send_message(channel, "Missing criteria {0}".format(missingCriteria))

@client.event 
async def showNoResultsFound():
	await client.send_message(channel, "No results found for the given criteria")

@client.event 
async def showUnknownCriteria(criteriaName, criteria):
	await client.send_message(channel, "Unknown criteria: name '{0}', value '{1}'".format(criteriaName, criteria))

@client.event 
async def showException(message, traceMessage):
	print(traceMessage)
	await client.send_message(channel, message)

def determineCriteria(message):
	lexer = shlex(message, posix=True)
	lexer.whitespace = ' '
	lexer.wordchars += '='
	return dict(word.split('=', maxsplit=1) for word in lexer)

def getEmojiElement(elementtype):
	return ELEMENT_EMOJI[elementtype]

def getEmojiWeapon(weapontype):
	return WEAPON_EMOJI[weapontype]

def getEmojiUnit(unittype):
	return UNIT_EMOJI[unittype]

def getEmojiRarity(rarity):
	return RARITY_EMOJI[rarity] * rarity

def getHumanStringDate(date):
	return datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f").strftime("%B %d, %Y")

@client.event
async def on_reaction_add(reaction, user):
	if reaction.message.id in active_adventurer_messages and reaction.emoji in adventurer_emojis and user != client.user:
		await client.remove_reaction(reaction.message, reaction.emoji, user)
		await controller.processAdventurerReaction(reaction.emoji, active_adventurer_messages[reaction.message.id], reaction.message)
	
	elif reaction.message.id in active_wyrmprint_messages and reaction.emoji in wyrmprint_emojis and user != client.user:
		await client.remove_reaction(reaction.message, reaction.emoji, user)
		await controller.processWyrmprintReaction(reaction.emoji, active_wyrmprint_messages[reaction.message.id], reaction.message)
	
	elif reaction.message.id in active_dragon_messages and reaction.emoji in dragon_emojis and user != client.user:
		await client.remove_reaction(reaction.message, reaction.emoji, user)
		await controller.processDragonReaction(reaction.emoji, active_dragon_messages[reaction.message.id], reaction.message)

@client.event 
async def showAdventurerFull(adventurer, message=None):
	e = discord.Embed(title=adventurer.name + " - " + adventurer.title, desc=adventurer.title)
	e.set_image(url="https://gamepedia.cursecdn.com/dragalialost_gamepedia_en/f/f9/100001_01_r04_portrait.png")
	await showOrEditAdventurer(e, adventurer, message)

@client.event 
async def showWyrmprintFull(wyrmprint, message=None):
	e = discord.Embed(title=wyrmprint.name, desc=wyrmprint.name)
	e.set_image(url="https://gamepedia.cursecdn.com/dragalialost_gamepedia_en/f/f9/100001_01_r04_portrait.png")
	await showOrEditWyrmprint(e, wyrmprint, message)

@client.event 
async def showDragonFull(dragon, message=None):
	e = discord.Embed(title=dragon.name, desc=dragon.name)
	e.set_image(url="https://gamepedia.cursecdn.com/dragalialost_gamepedia_en/f/f9/100001_01_r04_portrait.png")
	await showOrEditDragon(e, dragon, message)

@client.event 
async def showOrEditAdventurer(e, adventurer, message=None):
	if message == None:
		global active_adventurer_messages
		active_adventurer_messages = {}
		msg = await client.send_message(channel, embed=e)
		active_adventurer_messages[msg.id] = adventurer
		for emoji in adventurer_emojis:
			await client.add_reaction(msg, emoji)
	else:
		msg = await client.edit_message(message, embed=e)

@client.event 
async def showOrEditWyrmprint(e, wyrmprint, message=None):
	if message == None:
		global active_wyrmprint_messages
		active_wyrmprint_messages = {}
		msg = await client.send_message(channel, embed=e)
		active_wyrmprint_messages[msg.id] = wyrmprint
		for emoji in wyrmprint_emojis:
			await client.add_reaction(msg, emoji)
	else:
		msg = await client.edit_message(message, embed=e)

@client.event 
async def showOrEditDragon(e, dragon, message=None):
	if message == None:
		global active_dragon_messages
		active_dragon_messages = {}
		msg = await client.send_message(channel, embed=e)
		active_dragon_messages[msg.id] = dragon
		for emoji in dragon_emojis:
			await client.add_reaction(msg, emoji)
	else:
		msg = await client.edit_message(message, embed=e)

@client.event 
async def showCompletedUpdate():
	await client.send_message(channel, "Update complete")