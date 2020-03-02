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
from models.database import Database
from models.ability import Ability
from models.skill import Skill


class Adventurer:
    @staticmethod
    def find_adventurers(element=None, weapon=None, skill=None, ability=None,
                         rarity=None, lookback=None):
        adventurers = []
        params = ()
        full_query = Adventurer.adventurer_search_query_text
        if element is not None:
            full_query += "AND ET.name = ? COLLATE NOCASE "
            params += (element,)
        if weapon is not None:
            full_query += "AND WT.name = ? COLLATE NOCASE "
            params += (weapon,)
        if skill is not None:
            full_query += "AND S.name LIKE '%' || ? || '%' COLLATE NOCASE "
            params += (skill,)
        if ability is not None:
            full_query += "AND Ab.name LIKE '%' || ? || '%' COLLATE NOCASE "
            params += (ability,)
        if rarity is not None:
            full_query += "AND A.rarity >= ? "
            params += (rarity,)
        if lookback is not None:
            full_query += "AND A.ReleaseDate >= ? "
            params += (lookback,)
        if len(params) == 0:
            return adventurers
        with Database("master.db") as db:
            result = db.query(full_query, params)
        if result is None:
            return adventurers
        for adventurer in result:
            adventurers.append(Adventurer(adventurer[0]))
        return adventurers

    @staticmethod
    def get_adventurer_id(name):
        with Database("master.db") as db:
            result = db.query(Adventurer.id_query_text, (name,))
        if result is None or result == []:
            return (0, "")
        return (int(result[0][0]), result[0][1])

    def __init__(self, name, level=None):
        self.name = name
        with Database("master.db") as db:
            if not(self._get_adventurer(db)):
                raise KeyError("Adventurer with name {0} was not found"
                               .format(name))
            else:
                self._get_skills(db, level)
                self._get_abilities(db, level)

    def _get_adventurer(self, db):
        result = db.query(Adventurer.adventurer_query_exact_text, (self.name,))
        if result is None or result == []:
            result = db.query(Adventurer.adventurer_query_text, (self.name,))
        if result is None or result == []:
            result = db.query(Adventurer.alias_query_text, (self.name,))
        if result is None or result == []:
            return False
        result = result[0]
        self.adventurerid = result[0]
        self.title = result[1]
        self.rarity = result[2]
        self.elementtype = result[3].lower()
        self.weapontype = result[4].lower()
        self.maxhp = result[5]
        self.maxstr = result[6]
        self.maxcoop = result[7]
        self.defense = result[8]
        self.releasedate = result[9]
        self.unittype = result[10].lower()
        self.name = result[11]
        self.limited = result[12]
        self.manaspiral = result[13]
        return True

    def _get_skills(self, db, level=None):
        self.skills = []
        if level is None or level > 3:
            level = 3
        if level == -1: # Mana spiral
            result = db.query(Adventurer.mana_spiral_skills_query_text,
                            (self.adventurerid,))
        else:
            result = db.query(Adventurer.skills_query_text,
                            (level, self.adventurerid,))
        for skill in map(Skill._make, result):
            self.skills.append(skill)

    def _get_abilities(self, db, level=None):
        self.abilities = []
        if level is None or level > 2:
            level = 2
        elif level == -1:
            level = 3
        result = db.query(Adventurer.abilities_query_text,
                          (self.adventurerid, level,))
        for ability in map(Ability._make, result):
            self.abilities.append(ability)

    adventurer_query_exact_text = '''
    SELECT A.AdventurerID
        , A.Title
        , A.Rarity
        , ET.Name AS "ElementType"
        , WT.Name AS "WeaponType"
        , A.MaxHP
        , A.MaxSTR
        , A.MaxCoOp
        , A.Defense
        , A.ReleaseDate
        , UT.Name AS "UnitType"
        , A.Name
        , A.Limited
        , A.ManaSpiral
    FROM Adventurers A
        INNER JOIN ElementTypes ET ON ET.ElementTypeID = A.ElementTypeID
        INNER JOIN WeaponTypes WT ON WT.WeaponTypeID = A.WeaponTypeID
        INNER JOIN UnitTypes UT ON UT.UnitTypeID = A.UnitTypeID
    WHERE A.Name = ? COLLATE NOCASE
    ORDER BY A.ReleaseDate ASC
    LIMIT 1
    '''
    adventurer_query_text = '''
    SELECT A.AdventurerID
        , A.Title
        , A.Rarity
        , ET.Name AS "ElementType"
        , WT.Name AS "WeaponType"
        , A.MaxHP
        , A.MaxSTR
        , A.MaxCoOp
        , A.Defense
        , A.ReleaseDate
        , UT.Name AS "UnitType"
        , A.Name
        , A.Limited
        , A.ManaSpiral
    FROM Adventurers A
        INNER JOIN ElementTypes ET ON ET.ElementTypeID = A.ElementTypeID
        INNER JOIN WeaponTypes WT ON WT.WeaponTypeID = A.WeaponTypeID
        INNER JOIN UnitTypes UT ON UT.UnitTypeID = A.UnitTypeID
    WHERE A.Name LIKE '%' || ? || '%' COLLATE NOCASE
    ORDER BY A.ReleaseDate ASC
    LIMIT 1
    '''
    skills_query_text = '''
    SELECT S.Name
        , CASE ?
        WHEN 1 THEN S.DescriptionLevel1
        WHEN 2 THEN S.DescriptionLevel2
        ELSE IFNULL(S.DescriptionLevel3, S.DescriptionLevel2)
        END AS Description
        , S.SPCost
        , S.FrameTime
        , S.Regen
    FROM AdventurerSkillS Ads
        INNER JOIN Skills S ON S.SKillID = Ads.SkillID
    WHERE Ads.AdventurerID = ?
    '''
    mana_spiral_skills_query_text = '''
    SELECT S.Name
        , ManaSpiral AS Description
        , S.SPCost
        , S.FrameTime
        , S.Regen
    FROM AdventurerSkillS Ads
        INNER JOIN Skills S ON S.SKillID = Ads.SkillID
    WHERE Ads.AdventurerID = ?
    '''
    abilities_query_text = '''
    SELECT A.Name
        , A.Description
        , Ads.Level
        , A.Limited
        , A.WyrmprintAbilityCap
    FROM AdventurerAbilities Ads
        INNER JOIN Abilities A ON A.AbilityID = Ads.AbilityID
    WHERE Ads.AdventurerID = ?
        AND Ads.Level = ?
    ORDER BY Ads.Slot ASC
    '''
    adventurer_search_query_text = '''
    SELECT DISTINCT A.Name
    FROM Adventurers A
        INNER JOIN ElementTypes ET ON ET.ElementTypeID = A.ElementTypeID
        INNER JOIN WeaponTypes WT ON WT.WeaponTypeID = A.WeaponTypeID
        INNER JOIN AdventurerSkillS Ads ON Ads.AdventurerID = A.AdventurerID
        INNER JOIN Skills S ON S.SKillID = Ads.SkillID
        INNER JOIN AdventurerAbilities AA ON AA.AdventurerID = A.AdventurerID
        INNER JOIN Abilities Ab ON Ab.AbilityID = AA.AbilityID
    WHERE 1=1
    '''
    alias_query_text = '''
    SELECT A.AdventurerID
        , A.Title
        , A.Rarity
        , ET.Name AS "ElementType"
        , WT.Name AS "WeaponType"
        , A.MaxHP
        , A.MaxSTR
        , A.MaxCoOp
        , A.Defense
        , A.ReleaseDate
        , UT.Name AS "UnitType"
        , A.Name
        , A.Limited
        , A.ManaSpiral
    FROM Adventurers A
        INNER JOIN ElementTypes ET ON ET.ElementTypeID = A.ElementTypeID
        INNER JOIN WeaponTypes WT ON WT.WeaponTypeID = A.WeaponTypeID
        INNER JOIN UnitTypes UT ON UT.UnitTypeID = A.UnitTypeID
        INNER JOIN Aliases AL ON AL.AdventurerID = A.AdventurerID
            AND AL.AdventurerID IS NOT NULL
    WHERE AL.AliasText LIKE '%' || ? || '%' COLLATE NOCASE
    ORDER BY A.ReleaseDate ASC
    LIMIT 1
    '''
    id_query_text = '''
    SELECT AdventurerID, Name
    FROM Adventurers
    WHERE Name LIKE '%' || ? || '%' COLLATE NOCASE
    LIMIT 1
    '''
