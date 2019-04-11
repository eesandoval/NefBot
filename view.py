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
from config import *

client = discord.Client()
channel = None 

def startDiscordBot():
	client.run(TOKEN)

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
		await client.send_message(channel, "Shutting down")
		await client.close()
	elif messageCommand.startswith(COMMAND_START + "exit"):
		await client.send_message(channel, "User {0} is not authorized to shut down this bot.".format(message.author.name))
	elif messageCommand.startswith(COMMAND_START + "help"):
		await client.send_message(channel, HELP_TEXT)
	else:
		await client.send_message(channel, "Command not understood. Type {0}help for options".format(COMMAND_START))

@client.event 
async def on_ready():
	await client.change_presence(game=discord.Game(name=CURRENT_EVENT, url=STREAM_URL, type=1))

@client.event 
async def showAdventurer(adventurer):
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
		if skill.descriptionlevel3 != None:
			e.add_field(name="Skill: " + skill.name + " [SP Cost: {0}] ".format(skill.spcost) + "[Frame Time: {0}]".format(skill.frametime), value=skill.descriptionlevel3, inline=False)
		else:
	 		e.add_field(name="Skill: " + skill.name + " [SP Cost: {0}] ".format(skill.spcost) + "[Frame Time: {0}]".format(skill.frametime), value=skill.descriptionlevel2, inline=False)
	for ability in adventurer.abilities:
		e.add_field(name="Ability: " + ability.name, value=ability.description, inline=False)
	await client.send_message(channel, embed=e)

@client.event 
async def showAdventurerNotFound(name):
	await client.send_message(channel, "Adventurer {0} not found".format(name))

@client.event 
async def showWyrmprint(wyrmprint):
	e = discord.Embed(title=wyrmprint.name, desc=wyrmprint.name)
	portraitURL = PICTURE_SERVER + "wyrmprints/portraits/{0}.png".format("%20".join(wyrmprint.name.split()))
	e.set_thumbnail(url=portraitURL)
	e.add_field(name="Rarity", value=getEmojiRarity(wyrmprint.rarity), inline=True)
	e.add_field(name="Max HP/Max STR", value="{0}/{1}".format(wyrmprint.maxhp, wyrmprint.maxstr), inline=True)
	e.add_field(name="Release Date", value=getHumanStringDate(wyrmprint.releasedate), inline=True)
	for ability in wyrmprint.abilities:
		e.add_field(name="Ability: " + ability.name, value=ability.description, inline=False)
	await client.send_message(channel, embed=e)

@client.event 
async def showWyrmprintNotFound(name):
	await client.send_message(channel, "Wyrmprint {0} not found".format(name))

@client.event 
async def showDragon(dragon):
	e = discord.Embed(title=dragon.name, desc=dragon.name)
	portraitURL = PICTURE_SERVER + "dragons/portraits/{0}.png".format("%20".join(dragon.name))
	e.set_thumbnail(url=portraitURL)
	e.add_field(name="Element", value=getEmojiElement(dragon.elementtype), inline=True)
	e.add_field(name="Rarity", value=getEmojiRarity(dragon.rarity), inline=True)
	e.add_field(name="Max HP/Max STR", value="{0}/{1}".format(dragon.maxhp, dragon.maxstr), inline=True)
	e.add_field(name="Release Date", value=getHumanStringDate(dragon.releasedate), inline=True)
	for skill in dragon.skills:
		if dragon.level == 1:
			e.add_field(name="Skill: " + skill.name, value=skill.descriptionlevel1, inline=False)
		else: 
			e.add_field(name="Skill: " + skill.name, value=skill.descriptionlevel2, inline=False)
	for ability in dragon.abilities:	
		e.add_field(name="Ability: " + ability.name, value=ability.description, inline=False)
	await client.send_message(channel, embed=e)
	
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
async def showException(message):
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