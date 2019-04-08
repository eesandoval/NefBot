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
    except Exception as e:
        await view.showException("Failed to process adventurer with the following error:{0}".format(str(e)))

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
    except Exception as e:
        await view.showException("Failed to process query with the following error:{0}".format(str(e)))

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
    except Exception as e:
        await view.showException("Failed to process wyrmprint with the following error:{0}".format(str(e)))

def start():
    view.startDiscordBot()