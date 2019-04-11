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
	def findDragons(element=None, skill=None, ability=None, rarity=None, level=2):
		dragons = []
		params = ()
		fullQuery = Dragon.dragonSearchQueryText
		if element != None:
			fullQuery += "AND ET.name = ? COLLATE NOCASE "
			params += (element,)
		if skill != None:
			fullQuery += "AND S.name LIKE '%' || ? || '%' COLLATE NOCASE "
			params += (skill,)
		if ability != None:
			fullQuery += "AND A.name LIKE '%' || ? || '%' COLLATE NOCASE "
			params += (ability,)
		if rarity != None:
			fullQuery += "AND D.rarity >= ? "
			params += (rarity,)
		if level != None:
			fullQuery += "AND DA.level = ? "
			params += (level,)
		if len(params) == 0:
			return dragons 
		with Database("master.db") as db:
			result = db.query(fullQuery, params)
		if result == None:
			return dragons 
		for dragon in result:
			dragons.append(Dragon(dragon[0], level))
		return dragons
	
	def __init__(self, name, level):
		self.name = name 
		with Database("master.db") as db:
			if not(self._getDragon(db)):
				self = None
			else:
				self._getSkills(db, level)
				self._getAbilities(db, level)
				self.level = level

	def _getDragon(self, db):
		result = db.query(Dragon.dragonQueryText, (self.name,))
		if result == None or result == []:
			return False
		result = result[0]
		self.dragonid = result[0]
		self.elementtype = result[1]
		self.rarity = result[2]
		self.maxhp = result[3]
		self.maxstr = result[4]
		self.releasedate = result[5]
		self.name = result[6]
		return True

	def _getSkills(self, db, level):
		self.skills = []
		result = db.query(Dragon.skillsQueryText, (self.dragonid,))
		for skill in map(Skill._make, result):
			self.skills.append(skill)

	def _getAbilities(self, db, level):
		self.abilities = []
		result = db.query(Dragon.abilitiesQueryText, (self.dragonid,level,))
		for ability in map(Ability._make, result):
			self.abilities.append(ability)

	dragonQueryText = '''
	SELECT D.DragonID
		, ET.Name AS "ElementTypeName"
		, D.Rarity
		, D.HP
		, D.STR
		, D.ReleaseDate
		, D.Name 
	FROM Dragons D
		INNER JOIN ElementTypes ET ON ET.ElementTypeID = D.ElementTypeID 
	WHERE D.Name LIKE '%' || ? || '%' COLLATE NOCASE 
	ORDER BY D.ReleaseDate DESC
	LIMIT 1 
	'''

	abilitiesQueryText = '''
	SELECT A.Name
		, A.Description
		, DA.Level
	FROM DragonAbilities DA
		INNER JOIN Abilities A ON A.AbilityID = DA.AbilityID
	WHERE DA.DragonID = ?
		AND DA.Level = ?
	ORDER BY DA.Slot ASC, DA.Level ASC
	'''

	skillsQueryText = '''
	SELECT S.Name
		, S.SPCost
		, S.FrameTime
		, S.DescriptionLevel1
		, S.DescriptionLevel2
		, S.DescriptionLevel3
	FROM DragonSkills DS
		INNER JOIN Skills S ON S.SkillID = DS.SkillID 
	WHERE DS.DragonID = ?
	'''

	dragonSearchQueryText = '''
	SELECT DISTINCT D.Name 
	FROM Dragons D
		INNER JOIN ElementTypes ET ON ET.ElementTypeID = D.ElementTypeID
		INNER JOIN DragonSkills DS ON DS.DragonID = D.DragonID
		INNER JOIN Skills S ON S.SkillID = DS.SkillID
		INNER JOIN DragonAbilities DA ON DA.DragonID = D.DragonID
		INNER JOIN Abilities A ON A.AbilityID = DA.AbilityID
	WHERE 1=1 
	'''