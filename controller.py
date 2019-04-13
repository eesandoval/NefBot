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
import view
from models.adventurer import Adventurer
from models.wyrmprint import Wyrmprint
from models.dragon import Dragon
import traceback 

async def query(criteria):
    try:
        if "type" not in criteria:
            await view.showMissingCriteria("type")
        if criteria["type"].startswith("adv"):
            adventurers = queryAdventurers(criteria)
            if adventurers == None or adventurers == []:
                await view.showNoResultsFound()
            for adventurer in adventurers:
                await view.showAdventurer(adventurer)
        elif criteria["type"].startswith("wyr"):
            wyrmprints = queryWyrmprints(criteria)
            if wyrmprints == None or wyrmprints == []:
                await view.showNoResultsFound()
            for wyrmprint in wyrmprints:
                await view.showWyrmprint(wyrmprint)
        elif criteria["type"].startswith("dra"):
            dragons = queryDragons(criteria)
            if dragons == None or dragons == []:
                await view.showNoResultsFound()
            for dragon in dragons:
                await view.showDragon(dragon)
        else:
            await view.showUnknownCriteria("type", criteria["type"])
    except Exception as e:
        await view.showException("Failed to process query with the following error:{0}".format(str(e)), traceback.format_exc())

def queryAdventurers(criteria):
    element = None
    weapon = None
    skill = None 
    ability = None 
    rarity = None 
    if "element" in criteria:
        element = criteria["element"]
    if "weapon" in criteria:
        weapon = criteria["weapon"]
    if "skill" in criteria:
        skill = criteria["skill"]
    if "ability" in criteria:
        ability = criteria["ability"]
    if "rarity" in criteria:
        rarity = criteria["rarity"]
    if element == None and skill == None and weapon == None and ability == None and rarity == None:
        return []
    return Adventurer.findAdventurers(element, weapon, skill, ability, rarity)

def queryWyrmprints(criteria):
    ability = None
    rarity = None
    level = 2
    if "ability" in criteria:
        ability = criteria["ability"]
    if "rarity" in criteria:
        rarity = criteria["rarity"]
    if "level" in criteria:
        level = criteria["level"]
    if ability == None and rarity == None:
        return []
    return Wyrmprint.findWyrmprints(ability, rarity, level)

def queryDragons(criteria):
    element = None
    skill = None 
    ability = None 
    rarity = None 
    level = 2
    if "element" in criteria:
        element = criteria["element"]
    if "skill" in criteria:
        skill = criteria["skill"]
    if "ability" in criteria:
        ability = criteria["ability"]
    if "rarity" in criteria:
        rarity = criteria["rarity"]
    if "level" in criteria:
        level = criteria["level"]
    if element == None and skill == None and ability == None and rarity == None:
        return []
    return Dragon.findDragons(element, skill, ability, rarity, level)

async def processAdventurer(name, level=None, message=None):
    try:
        if name == None or name == "":
            await view.showInvalidName()
        adventurer = Adventurer(name, level)
        if adventurer == None:
            await view.showAdventurerNotFound(name)
        else:
            await view.showAdventurer(adventurer, message)
    except Exception as e:
        await view.showException("Failed to process adventurer with the following error:{0}".format(str(e)), traceback.format_exc())

async def processWyrmprint(name, level=None, message=None):
    try:
        if name == None or name == "":
            await view.showInvalidName()
        wyrmprint = Wyrmprint(name, level or 2)
        if wyrmprint == None:
            await view.showWyrmprintNotFound(name)
        else:
            await view.showWyrmprint(wyrmprint, message)
    except Exception as e:
        await view.showException("Failed to process wyrmprint with the following error:{0}".format(str(e)), traceback.format_exc())

async def processDragon(name, level=None, message=None):
    try:
        if name == None or name == "":
            await view.showInvalidName()
        dragon = Dragon(name, level or 2)
        if dragon == None:
            await view.showDragonNotFound(name)
        else:
            await view.showDragon(dragon, message)
    except Exception as e:
        await view.showException("Failed to process dragon with the following error:{0}".format(str(e)), traceback.format_exc())

async def processAdventurerReaction(emoji, adventurer, message):
    if emoji == "\U0001F5BC": # Full picture
        await view.showAdventurerFull(adventurer, message)
    elif emoji == "\U0001F508": # 1 unbind
        await processAdventurer(adventurer.name, 1, message)
    elif emoji == "\U0001F509": # 2 unbinds
        await processAdventurer(adventurer.name, 2, message)
    elif emoji == "\U0001F50A": # 3 unbinds 
        await processAdventurer(adventurer.name, 3, message)

async def processWyrmprintReaction(emoji, wyrmprint, message):
    if emoji == "\U0001F5BC": # Full picture
        await view.showWyrmprintFull(wyrmprint, message)
    elif emoji == "\U0001F508": # 1 unbind
        await processWyrmprint(wyrmprint.name, 1, message)
    elif emoji == "\U0001F509": # 2 unbinds
        await processWyrmprint(wyrmprint.name, 2, message)

async def processDragonReaction(emoji, dragon, message):
    if emoji == "\U0001F5BC": # Full picture
        await view.showDragonFull(dragon, message)
    elif emoji == "\U0001F508": # 1 unbind
        await processDragon(dragon.name, 1, message)
    elif emoji == "\U0001F509": # 2 unbinds
        await processDragon(dragon.name, 2, message)

async def update():
    view.setViewConfig()
    await view.showCompletedUpdate()

def start():
    view.setViewConfig()
    view.startDiscordBot()