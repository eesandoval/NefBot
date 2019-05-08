import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from controller import *


def test_query_adventurers():
    criteria = {"type": "adv", "element": "Flame", "weapon": "Axe",
                "rarity": "4", "ability": "Stun Res +100%",
                "skill": "Scarlet Geyser"}
    assert len(query_adventurers(criteria)) > 0
    criteria = {"type": "adv", "element": "Water", "weapon": "Wand",
                "rarity": "5", "ability": "Burn Res +100%",
                "skill": "Glacial Blossom"}
    assert len(query_adventurers(criteria)) > 0


def test_query_wyrmprints():
    criteria = {"type": "wyr", "rarity": "5", "ability": "Curse Res +60%"}
    assert len(query_wyrmprints(criteria)) > 0
    criteria = {"type": "wyr", "rarity": "4", "ability": "Force Strike"}
    assert len(query_wyrmprints(criteria)) > 0


def test_query_dragons():
    criteria = {"type": "dra", "element": "Flame", "rarity": "5",
                "ability": "(Flame) Strength +60%",
                "skill": "Infernal Damnation"}
    assert len(query_dragons(criteria)) > 0


def test_weapons():
    # Test aliases
    elements = ["flame", "water", "wind", "light", "shadow"]
    weapons = ["sword", "blade", "axe", "lance",
               "dagger", "bow", "staff", "wand"]
    rarities = [3, 4, 5]
    for rarity in rarities:
        for weapon in weapons:
            for element in elements:
                name = "{0}*t3 {1} {2}".format(str(rarity), element, weapon)
                result_wep = process_weapon(name)
                assert result_wep.rarity == rarity
                assert result_wep.elementtype == element
                assert result_wep.weapontype == weapon
