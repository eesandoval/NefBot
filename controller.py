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
import traceback
import view
from models.adventurer import Adventurer
from models.wyrmprint import Wyrmprint
from models.dragon import Dragon
from models.alias import create_update_alias, delete_alias

async def query(criteria):
    try:
        if "type" not in criteria:
            await view.show_missing_criteria("type")

        if criteria["type"].startswith("a"):
            adventurers = query_adventurers(criteria)
            if adventurers is None or adventurers == []:
                await view.show_no_results_found()
            for adventurer in adventurers:
                await view.show_adventurer(adventurer)

        elif criteria["type"].startswith("w"):
            wyrmprints = query_wyrmprints(criteria)
            if wyrmprints is None or wyrmprints == []:
                await view.show_no_results_found()
            for wyrmprint in wyrmprints:
                await view.show_wyrmprint(wyrmprint)

        elif criteria["type"].startswith("d"):
            dragons = query_dragons(criteria)
            if dragons is None or dragons == []:
                await view.show_no_results_found()
            for dragon in dragons:
                await view.show_dragon(dragon)

        else:
            await view.show_unknown_criteria("type", criteria["type"])

    except Exception as e:
        await view.show_exception(
            "Failed to process query with the following error:{0}"
            .format(str(e)), traceback.format_exc())


def query_adventurers(criteria):
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
    if (element is None and skill is None and weapon is None and
            ability is None and rarity is None):
        return []
    return Adventurer.find_adventurers(element, weapon, skill, ability, rarity)


def query_wyrmprints(criteria):
    ability = None
    rarity = None
    level = 3
    if "ability" in criteria:
        ability = criteria["ability"]
    if "rarity" in criteria:
        rarity = criteria["rarity"]
    if "level" in criteria:
        level = criteria["level"]
    if ability is None and rarity is None:
        return []
    return Wyrmprint.find_wyrmprints(ability, rarity, level)


def query_dragons(criteria):
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
    if (element is None and skill is None and ability is None and
            rarity is None):
        return []
    return Dragon.find_dragons(element, skill, ability, rarity, level)


async def process_adventurers(name, level=None, message=None):
    try:
        if name is None or name == "":
            await view.show_invalid_name()

        adventurer = Adventurer(name, level)
        if adventurer is None:
            await view.show_adventurer_not_found(name)
        else:
            await view.show_adventurer(adventurer, message)
    except Exception as e:
        await view.show_exception(
            "Failed to process adventurer with the following error:{0}"
            .format(str(e)), traceback.format_exc())


async def process_wyrmprint(name, level=None, message=None):
    try:
        if name is None or name == "":
            await view.show_invalid_name()

        wyrmprint = Wyrmprint(name, level or 3)
        if wyrmprint is None:
            await view.show_wyrmprint_not_found(name)
        else:
            await view.show_wyrmprint(wyrmprint, message)
    except Exception as e:
        await view.show_exception(
            "Failed to process wyrmprint with the following error:{0}"
            .format(str(e)), traceback.format_exc())


async def process_dragon(name, level=None, message=None):
    try:
        if name is None or name == "":
            await view.show_invalid_name()

        dragon = Dragon(name, level or 2)
        if dragon is None:
            await view.show_dragon_not_found(name)
        else:
            await view.show_dragon(dragon, message)
    except Exception as e:
        await view.show_exception(
            "Failed to process dragon with the following error:{0}"
            .format(str(e)), traceback.format_exc())

async def process_adventurers_reaction(emoji, adventurer, message):
    if emoji == "\U0001F5BC":  # Full picture
        await view.show_adventurer_full(adventurer, message)
    elif emoji == "\U0001F508":  # 1 unbind
        await process_adventurers(adventurer.name, 1, message)
    elif emoji == "\U0001F509":  # 2 unbinds
        await process_adventurers(adventurer.name, 2, message)
    elif emoji == "\U0001F50A":  # 3 unbinds
        await process_adventurers(adventurer.name, 3, message)

async def process_wyrmprint_reaction(emoji, wyrmprint, message):
    if emoji == "\U0001F5BC":  # Full picture
        await view.show_wyrmprint_full(wyrmprint, message)
    elif emoji == "\U0001F508":  # 1 unbind
        await process_wyrmprint(wyrmprint.name, 1, message)
    elif emoji == "\U0001F509":  # 2 unbinds
        await process_wyrmprint(wyrmprint.name, 2, message)
    elif emoji == "\U0001F50A":  # 3 unbinds
        await process_wyrmprint(wyrmprint.name, 3, message)
    elif emoji == "\U0001F3A8":  # Full base picture
        await view.show_wyrmprint_base_full(wyrmprint, message)

async def process_dragon_reaction(emoji, dragon, message):
    if emoji == "\U0001F5BC":  # Full picture
        await view.show_dragon_full(dragon, message)
    elif emoji == "\U0001F508":  # 1 unbind
        await process_dragon(dragon.name, 1, message)
    elif emoji == "\U0001F509":  # 2 unbinds
        await process_dragon(dragon.name, 2, message)

async def handle_alias(message):
    if ',' not in message or len(message.split(',')) < 1:
        result = delete_alias(message)
        await view.show_completed_alias(result)
        return
    alias = message.split(',')[0].strip()
    name = message.split(',')[1].strip()
    alias_type = 0
    aliased_id = Adventurer.get_adventurer_id(name)
    if aliased_id != 0:
        result = create_update_alias(aliased_id, alias, alias_type)
        await view.show_completed_alias(result)
        return
    alias_type += 1
    aliased_id = Wyrmprint.get_wyrmprint_id(name)
    if aliased_id != 0:
        result = create_update_alias(aliased_id, alias, alias_type)
        await view.show_completed_alias(result)
        return
    alias_type += 1
    aliased_id = Dragon.get_dragon_id(name)
    if aliased_id != 0:
        result = create_update_alias(aliased_id, alias, alias_type)
        await view.show_completed_alias(result)
        return


def start():
    view.start_discord_bot()
