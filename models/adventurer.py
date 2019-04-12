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
	def findAdventurers(element=None, weapon=None, skill=None, ability=None, rarity=None):
		adventurers = []
		params = ()
		fullQuery = Adventurer.adventurerSearchQueryText
		if element != None:
			fullQuery += "AND ET.name = ? COLLATE NOCASE "
			params += (element,)
		if weapon != None:
			fullQuery += "AND WT.name = ? COLLATE NOCASE "
			params += (weapon,)
		if skill != None:
			fullQuery += "AND S.name LIKE '%' || ? || '%' COLLATE NOCASE "
			params += (skill,)
		if ability != None:
			fullQuery += "AND Ab.name LIKE '%' || ? || '%' COLLATE NOCASE "
			params += (ability,)
		if rarity != None:
			fullQuery += "AND A.rarity >= ? "
			params += (rarity,)
		if len(params) == 0:
			return adventurers
		with Database("master.db") as db:
			result = db.query(fullQuery, params)
		if result == None:
			return adventurers
		for adventurer in result:
			adventurers.append(Adventurer(adventurer[0]))
		return adventurers

	def __init__(self, name, level=None):
		self.name = name
		with Database("master.db") as db: 
			if not(self._getAdventurer(db)):
				self = None
			else:
				self._getSkills(db, level)
				self._getAbilities(db, level)

	def _getAdventurer(self, db):
		result = db.query(Adventurer.adventurerQueryText, (self.name,))
		if result == None or result == []:
			return False
		result = result[0]
		self.adventurerid = result[0]
		self.title = result[1]
		self.rarity = result[2]
		self.elementtype = result[3]
		self.weapontype = result[4]
		self.maxhp = result[5]
		self.maxstr = result[6]
		self.maxcoop = result[7]
		self.defense = result[8]
		self.releasedate = result[9]
		self.unittype = result[10]
		self.name = result[11]
		return True

	def _getSkills(self, db, level=None):
		self.skills = []
		if level == None:
			level = 3
		result = db.query(Adventurer.skillsQueryText, (level, self.adventurerid,))
		for skill in map(Skill._make, result):
			self.skills.append(skill)

	def _getAbilities(self, db, level=None):
		self.abilities = []
		if level == None:
			level = 3
		result = db.query(Adventurer.abilitiesQueryText, (self.adventurerid,))
		for ability in map(Ability._make, result):
			self.abilities.append(ability)

	adventurerQueryText = '''
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
	FROM Adventurers A
		INNER JOIN ElementTypes ET ON ET.ElementTypeID = A.ElementTypeID
		INNER JOIN WeaponTypes WT ON WT.WeaponTypeID = A.WeaponTypeID
		INNER JOIN UnitTypes UT ON UT.UnitTypeID = A.UnitTypeID
	WHERE A.Name LIKE '%' || ? || '%' COLLATE NOCASE
	ORDER BY A.ReleaseDate DESC
	LIMIT 1
	'''
	skillsQueryText = '''
	SELECT S.Name 
		, CASE ? WHEN 1 THEN S.DescriptionLevel1 WHEN 2 THEN S.DescriptionLevel2 ELSE IFNULL(S.DescriptionLevel3, S.DescriptionLevel2) END AS Description
		, S.SPCost 
		, S.FrameTime 
	FROM AdventurerSkillS Ads
		INNER JOIN Skills S ON S.SKillID = Ads.SkillID
	WHERE Ads.AdventurerID = ?
	'''
	abilitiesQueryText = '''
	SELECT A.Name 
		, A.Description 
		, 2 AS "Level"
	FROM AdventurerAbilities Ads
		INNER JOIN Abilities A ON A.AbilityID = Ads.AbilityID 
	WHERE Ads.AdventurerID = ?
	'''
	adventurerSearchQueryText = '''
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