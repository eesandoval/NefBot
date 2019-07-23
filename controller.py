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
import urllib.request
import threading
from models.adventurer import Adventurer
from models.wyrmprint import Wyrmprint
from models.dragon import Dragon
from models.weapon import Weapon
from models.alias import create_update_alias, delete_alias
from models.events import Event
from models.database import Database
from utils.config import Config
from view import start_discord_bot

config = Config("config.ini")


def query(criteria):
    unit_list = []

    adventurers = query_adventurers(criteria)
    for adventurer in adventurers or []:
        unit_list.append((adventurer.name, "Adventurer"))

    wyrmprints = query_wyrmprints(criteria)
    for wyrmprint in wyrmprints or []:
        unit_list.append((wyrmprint.name, "Wyrmprint"))

    dragons = query_dragons(criteria)
    for dragon in dragons or []:
        unit_list.append((dragon.name, "Dragon"))

    weapons = query_weapons(criteria)
    for weapon in weapons or []:
        unit_list.append((weapon.name, "Weapon"))

    if unit_list == []:
        raise KeyError("No results found")
    return unit_list


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


def query_weapons(criteria):
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
    return Weapon.find_weapons(element, weapon, skill, ability, rarity)


def process_adventurer(name, level=None):
    if name is None or name == "":
        raise KeyError("Name not specified")
    return Adventurer(name, level)


def process_wyrmprint(name, level=None):
    if name is None or name == "":
        raise KeyError("Name not specified")
    return Wyrmprint(name, level or 3)


def process_dragon(name, level=None):
    if name is None or name == "":
        raise KeyError("Name not specified")
    return Dragon(name, level or 2)


def process_weapon(name, level=None):
    if name is None or name == "":
        raise KeyError("Name not specified")
    return Weapon(name, level or 2)


def handle_alias(alias_text, aliased_name):
    if aliased_name is None:
        return delete_alias(alias_text)
    alias_type = 0
    lst = [Adventurer.get_adventurer_id, Wyrmprint.get_wyrmprint_id,
           Dragon.get_dragon_id, Weapon.get_weapon_id]
    id_name = (0, "")
    alias_type = -1
    while id_name[0] == 0 and alias_type + 1 < len(lst):
        alias_type += 1
        id_name = lst[alias_type](aliased_name)
    if id_name[0] == 0:
        raise KeyError("Could not find {0}".format(aliased_name))
    return create_update_alias(id_name[0], alias_text, alias_type, id_name[1])


def handle_current_events():
    return Event.get_current_events()


def handle_update(remote_url):
    url = remote_url + "database/master.db"
    urllib.request.urlretrieve(url, "master.db")


def continous_updates(event_thread):
    handle_update(config.picture_server)
    thread = threading.Timer(86400, continous_updates, [event_thread])
    if not event_thread.is_set():
        thread.start()
    else:
        thread.cancel()


def start():
    event_thread = threading.Event()
    continous_updates(event_thread)
    start_discord_bot()
    event_thread.set()
