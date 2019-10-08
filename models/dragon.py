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


class Dragon:
    @staticmethod
    def find_dragons(element=None, skill=None, ability=None, rarity=None,
                     level=2):
        dragons = []
        params = ()
        full_query = Dragon.dragon_search_query_text
        if element is not None:
            full_query += "AND ET.name = ? COLLATE NOCASE "
            params += (element,)
        if skill is not None:
            full_query += "AND S.name LIKE '%' || ? || '%' COLLATE NOCASE "
            params += (skill,)
        if ability is not None:
            full_query += "AND A.name LIKE '%' || ? || '%' COLLATE NOCASE "
            params += (ability,)
        if rarity is not None:
            full_query += "AND D.rarity >= ? "
            params += (rarity,)
        if level is not None:
            full_query += "AND DA.level = ? "
            params += (level,)
        if len(params) == 0:
            return dragons
        with Database("master.db") as db:
            result = db.query(full_query, params)
        if result is None:
            return dragons
        for dragon in result:
            dragons.append(Dragon(dragon[0], level))
        return dragons

    @staticmethod
    def get_dragon_id(name):
        with Database("master.db") as db:
            result = db.query(Dragon.id_query_text, (name,))
        if result is None or result == []:
            return (0, "")
        return (int(result[0][0]), result[0][1])

    def __init__(self, name, level):
        self.name = name
        with Database("master.db") as db:
            if not(self._get_dragon(db)):
                raise KeyError("Dragon with name {0} was not found"
                               .format(name))
            else:
                self._get_skills(db, level)
                self._get_abilities(db, level)
                self.level = level

    def _get_dragon(self, db):
        result = db.query(Dragon.dragon_query_exact_text, (self.name,))
        if result is None or result == []:
            result = db.query(Dragon.dragon_query_text, (self.name,))
        if result is None or result == []:
            result = db.query(Dragon.alias_query_text, (self.name,))
        if result is None or result == []:
            return False
        result = result[0]
        self.dragonid = result[0]
        self.elementtype = result[1].lower()
        self.rarity = result[2]
        self.maxhp = result[3]
        self.maxstr = result[4]
        self.releasedate = result[5]
        self.name = result[6]
        self.limited = result[7]
        return True

    def _get_skills(self, db, level):
        self.skills = []
        result = db.query(Dragon.skills_query_text,
                          (level, self.dragonid,))
        for skill in map(Skill._make, result):
            self.skills.append(skill)

    def _get_abilities(self, db, level):
        self.abilities = []
        result = db.query(Dragon.abilities_query_text,
                          (self.dragonid, level,))
        for ability in map(Ability._make, result):
            self.abilities.append(ability)

    dragon_query_exact_text = '''
    SELECT D.DragonID
        , ET.Name AS "ElementTypeName"
        , D.Rarity
        , D.HP
        , D.STR
        , D.ReleaseDate
        , D.Name
        , D.Limited
    FROM Dragons D
        INNER JOIN ElementTypes ET ON ET.ElementTypeID = D.ElementTypeID
    WHERE D.Name = ? COLLATE NOCASE
    ORDER BY D.ReleaseDate ASC
    LIMIT 1
    '''
    dragon_query_text = '''
    SELECT D.DragonID
        , ET.Name AS "ElementTypeName"
        , D.Rarity
        , D.HP
        , D.STR
        , D.ReleaseDate
        , D.Name
        , D.Limited
    FROM Dragons D
        INNER JOIN ElementTypes ET ON ET.ElementTypeID = D.ElementTypeID
    WHERE D.Name LIKE '%' || ? || '%' COLLATE NOCASE
    ORDER BY D.ReleaseDate ASC
    LIMIT 1
    '''

    abilities_query_text = '''
    SELECT A.Name
        , A.Description
        , DA.Level
        , A.Limited
    FROM DragonAbilities DA
        INNER JOIN Abilities A ON A.AbilityID = DA.AbilityID
    WHERE DA.DragonID = ?
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
    FROM DragonSkills DS
        INNER JOIN Skills S ON S.SkillID = DS.SkillID
    WHERE DS.DragonID = ?
    '''

    dragon_search_query_text = '''
    SELECT DISTINCT D.Name
    FROM Dragons D
        INNER JOIN ElementTypes ET ON ET.ElementTypeID = D.ElementTypeID
        INNER JOIN DragonSkills DS ON DS.DragonID = D.DragonID
        INNER JOIN Skills S ON S.SkillID = DS.SkillID
        INNER JOIN DragonAbilities DA ON DA.DragonID = D.DragonID
        INNER JOIN Abilities A ON A.AbilityID = DA.AbilityID
    WHERE 1=1
    '''
    alias_query_text = '''
    SELECT D.DragonID
        , ET.Name AS "ElementTypeName"
        , D.Rarity
        , D.HP
        , D.STR
        , D.ReleaseDate
        , D.Name
        , D.Limited
    FROM Dragons D
        INNER JOIN ElementTypes ET ON ET.ElementTypeID = D.ElementTypeID
        INNER JOIN Aliases AL ON AL.DragonID = D.DragonID
            AND AL.DragonID IS NOT NULL
    WHERE AL.AliasText LIKE '%' || ? || '%' COLLATE NOCASE
    ORDER BY D.ReleaseDate ASC
    LIMIT 1
    '''
    id_query_text = '''
    SELECT DragonID, Name
    FROM Dragons
    WHERE Name LIKE '%' || ? || '%' COLLATE NOCASE
    LIMIT 1
    '''
