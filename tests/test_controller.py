import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__),os.pardir))
from controller import queryAdventurers, queryWyrmprints, queryDragons

def test_queryAdventurers():
    criteria = {"type":"adv", "element":"Flame", "weapon":"Axe", "rarity":"4", "ability":"Stun Res +100%", "skill":"Scarlet Geyser"}
    assert len(queryAdventurers(criteria)) > 0
    criteria = {"type":"adv", "element":"Water", "weapon":"Wand", "rarity":"5", "ability":"Burn Res +100%", "skill":"Glacial Blossom"}
    assert len(queryAdventurers(criteria)) > 0

def test_queryWyrmprints():
    criteria = {"type":"wyr", "rarity":"5", "ability":"Curse Res +60%"}
    assert len(queryWyrmprints(criteria)) > 0
    criteria = {"type":"wyr", "rarity":"4", "ability":"Force Strike"}
    assert len(queryWyrmprints(criteria)) > 0

def test_queryDragons():
    criteria = {"type":"dra", "element":"Flame", "rarity":"5", "ability":"(Flame) Strength +60%", "skill":"Infernal Damnation"}
    assert len(queryDragons(criteria)) > 0