import view
from model import Adventurer
from model import Wyrmprint

async def processAdventurer(name):
    try:
        if name == None or name == "":
            await view.showInvalidName()
        adventurer = Adventurer(name)
        if adventurer == None:
            await view.showAdventurerNotFound(name)
        else:
            await view.showAdventurer(adventurer)
    except:
        await view.showException()

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
    except:
        await view.showException()

def queryAdventurers(criteria):
    element = None
    weapon = None
    skill = None 
    ability = None 
    if "element" in criteria:
        element = criteria["element"]
    if "weapon" in criteria:
        weapon = criteria["weapon"]
    if "skill" in criteria:
        skill = criteria["skill"]
    if "ability" in criteria:
        ability = criteria["ability"]
    if element == None and skill == None and weapon == None and ability == None:
        return []
    return Adventurer.findAdventurers(element, weapon, skill, ability)

async def processWyrmprint(name):
    try:
        if name == None or name == "":
            await view.showInvalidName()
        name = name.strip()
        level = 2
        if name[-1].isdigit():
            level = int(name[-1])
            name = name[0:len(name) - 1].strip()
        wyrmprint = Wyrmprint(name)
        if wyrmprint == None:
            await view.showWyrmprintNotFound(name)
        else:
            await view.showWyrmprint(wyrmprint, level)
    except:
        await view.showException()

def start():
    view.startDiscordBot()