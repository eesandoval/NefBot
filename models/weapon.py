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
from models.skill import Skill
from models.ability import Ability


class Weapon:
    @staticmethod
    def find_weapons(element=None, weapon=None, skill=None, ability=None,
                     rarity=None, lookback=None):
        weapons = []
        params = ()
        full_query = Weapon.weapon_search_query_text
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
            full_query += "AND A.name LIKE '%' || ? || '%' COLLATE NOCASE "
            params += (ability,)
        if rarity is not None:
            full_query += "AND W.rarity >= ? "
            params += (rarity,)
        if lookback is not None:
            full_query += "AND W.ReleaseDate >= ? "
            params += (lookback,)
        if len(params) == 0:
            return weapons
        with Database("master.db") as db:
            result = db.query(full_query, params)
        if result is None:
            return weapons
        for weapon in result:
            weapons.append(Weapon(weapon[0], 2))
        return weapons

    @staticmethod
    def get_weapon_id(name):
        with Database("master.db") as db:
            result = db.query(Weapon.id_query_text, (name,))
        if result is None or result == []:
            return (0, "")
        return (int(result[0][0]), result[0][1])

    def __init__(self, name, level):
        self.name = name
        with Database("master.db") as db:
            if not(self._get_weapon(db)):
                raise KeyError("Weapon with name {0} was not found"
                               .format(name))
            else:
                self._get_skills(db, level)
                self._get_abilities(db, level)
                self._get_upgrades_from(db)
                self._get_upgrades_to(db)
                self.level = level

    def _get_weapon(self, db):
        result = db.query(Weapon.weapon_query_exact_text, (self.name,))
        if result is None or result == []:
            result = db.query(Weapon.weapon_query_text, (self.name,))
        if result is None or result == []:
            result = db.query(Weapon.alias_query_text, (self.name,))
        if result is None or result == []:
            return False
        result = result[0]
        self.weaponid = result[0]
        self.elementtype = result[1]
        self.weapontype = result[2].lower()
        self.rarity = result[3]
        self.maxhp = result[4]
        self.maxstr = result[5]
        self.releasedate = result[6]
        self.name = result[7]
        self.limited = result[8]
        return True

    def _get_skills(self, db, level):
        self.skills = []
        result = db.query(Weapon.skills_query_text,
                          (level, self.weaponid,))
        for skill in map(Skill._make, result):
            self.skills.append(skill)

    def _get_abilities(self, db, level):
        self.abilities = []
        level = 1  # No abilities are greater than 1 right now
        result = db.query(Weapon.abilities_query_text,
                          (self.weaponid, level,))
        for ability in map(Ability._make, result):
            self.abilities.append(ability)

    def _get_upgrades_to(self, db):
        self.upgrades_to = []
        self.upgrades_to_materials = []
        result = db.query(Weapon.upgrades_to_query_text,
                          (self.weaponid,))
        for upgrade_to in result or []:
            self.upgrades_to.append(upgrade_to[0])
            self.upgrades_to_materials.append(self._get_materials(
                                              upgrade_to[1], db))

    def _get_upgrades_from(self, db):
        self.upgrades_from = []
        self.upgrades_from_materials = []
        result = db.query(Weapon.upgrades_from_query_text,
                          (self.weaponid,))
        for upgrade_from in result or []:
            self.upgrades_from.append(upgrade_from[0])
            self.upgrades_from_materials.append(self._get_materials(
                                                upgrade_from[1], db))

    def _get_materials(self, weaponid, db):
        result = db.query(Weapon.materials_query_text, (weaponid,))
        materials = {}
        for material in result or []:
            materials[material[0]] = material[1]
        return materials

    weapon_query_exact_text = '''
    SELECT D.WeaponID
        , lower(ET.Name) AS "ElementTypeName"
        , WT.Name AS "WeaponTypeName"
        , D.Rarity
        , D.MaxHP
        , D.MaxSTR
        , D.ReleaseDate
        , D.Name
        , D.Limited
    FROM Weapons D
        LEFT JOIN ElementTypes ET ON ET.ElementTypeID = D.ElementTypeID
        INNER JOIN WeaponTypes WT ON WT.WeaponTypeID = D.WeaponTypeID
    WHERE D.Name LIKE '%' || ? || '%' COLLATE NOCASE
    ORDER BY D.ReleaseDate ASC
    LIMIT 1
    '''
    weapon_query_text = '''
    SELECT D.WeaponID
        , lower(ET.Name) AS "ElementTypeName"
        , WT.Name AS "WeaponTypeName"
        , D.Rarity
        , D.MaxHP
        , D.MaxSTR
        , D.ReleaseDate
        , D.Name
        , D.Limited
    FROM Weapons D
        LEFT JOIN ElementTypes ET ON ET.ElementTypeID = D.ElementTypeID
        INNER JOIN WeaponTypes WT ON WT.WeaponTypeID = D.WeaponTypeID
    WHERE D.Name LIKE '%' || ? || '%' COLLATE NOCASE
    ORDER BY D.ReleaseDate ASC
    LIMIT 1
    '''
    abilities_query_text = '''
    SELECT A.Name
        , A.Description
        , DA.Level
        , A.Limited
        , A.WyrmprintAbilityCap
    FROM WeaponAbilities DA
        INNER JOIN Abilities A ON A.AbilityID = DA.AbilityID
    WHERE DA.WeaponID = ?
        AND DA.Level = ?
    ORDER BY DA.Slot ASC, DA.Level ASC
    '''
    skills_query_text = '''
    SELECT S.Name
        , CASE ?
        WHEN 1 THEN S.DescriptionLevel1
        ELSE S.DescriptionLevel2
        END AS Description
        , S.SPCost
        , S.FrameTime
        , S.Regen
    FROM WeaponSkills DS
        INNER JOIN Skills S ON S.SkillID = DS.SkillID
    WHERE DS.WeaponID = ?
    '''
    upgrades_to_query_text = '''
    SELECT WTo.Name
        , WTo.WeaponID
    FROM  WeaponUpgrades WU
        INNER JOIN Weapons WTo ON WTo.WeaponID = WU.WeaponToID
    WHERE WU.WeaponFromID = ?
    '''
    upgrades_from_query_text = '''
    SELECT WFrom.Name
        , WFrom.WeaponID
    FROM WeaponUpgrades WU
        INNER JOIN Weapons WFrom ON WFrom.WeaponID = WU.WeaponFromID
    WHERE WU.WeaponToID = ?
    '''
    materials_query_text = '''
    SELECT M.Name
        , WM.Quantity
    FROM WeaponMaterials WM
        INNER JOIN Materials M ON M.MaterialID = WM.MaterialID
    WHERE WM.WeaponID = ?
    '''
    weapon_search_query_text = '''
    SELECT DISTINCT W.Name
    FROM Weapons W
        INNER JOIN WeaponTypes WT ON WT.WeaponTypeID = W.WeaponTypeID
        LEFT JOIN ElementTypes ET ON ET.ElementTypeID = W.ElementTypeID
        LEFT JOIN WeaponSkills DS ON DS.WeaponID = W.WeaponID
        LEFT JOIN Skills S ON S.SkillID = DS.SkillID
        LEFT JOIN WeaponAbilities DA ON DA.WeaponID = W.WeaponID
        LEFT JOIN Abilities A ON A.AbilityID = DA.AbilityID
    WHERE 1=1
    '''
    alias_query_text = '''
    SELECT W.WeaponID
        , lower(ET.Name) AS "ElementTypeName"
        , WT.Name AS "WeaponTypeName"
        , W.Rarity
        , W.MaxHP
        , W.MaxSTR
        , W.ReleaseDate
        , W.Name
        , W.Limited
    FROM Weapons W
        LEFT JOIN ElementTypes ET ON ET.ElementTypeID = W.ElementTypeID
        INNER JOIN Aliases AL ON AL.WeaponID = W.WeaponID
            AND AL.WeaponID IS NOT NULL
        INNER JOIN WeaponTypes WT ON WT.WeaponTypeID = W.WeaponTypeID
    WHERE AL.AliasText LIKE '%' || ? || '%' COLLATE NOCASE
    ORDER BY W.ReleaseDate ASC
    LIMIT 1
    '''
    id_query_text = '''
    SELECT WeaponID, Name
    FROM Weapons
    WHERE Name LIKE '%' || ? || '%' COLLATE NOCASE
    LIMIT 1
    '''
