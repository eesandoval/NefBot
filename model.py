from database import Database
from collections import namedtuple

class Skill(namedtuple("Skill", "name, spcost, frametime, descriptionlevel1, descriptionlevel2, descriptionlevel3")):
	pass

class Ability(namedtuple("Skill", "name, description, level")):
	pass
	
class Adventurer:
	@staticmethod
	def findAdventurers(element=None, weapon=None, skill=None, ability=None):
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
			fullQuery += "AND S.name = ? COLLATE NOCASE "
			params += (skill,)
		if ability != None:
			fullQuery += "AND Ab.name = ? COLLATE NOCASE "
			params += (ability,)
		if len(params) == 0:
			return adventurers
		with Database("master.db") as db:
			result = db.query(fullQuery, params)
		if result == None:
			return adventurers
		for adventurer in result:
			adventurers.append(Adventurer(adventurer[0]))
		return adventurers

	def __init__(self, name):
		self.name = name
		with Database("master.db") as db: 
			if not(self._getAdventurer(db)):
				self = None
			else:
				self._getSkills(db)
				self._getAbilities(db)

	def _getAdventurer(self, db):
		result = db.query(Adventurer.adventurerQueryText, (self.name,))
		if result == None:
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

	def _getSkills(self, db):
		self.skills = []
		result = db.query(Adventurer.skillsQueryText, (self.adventurerid,))
		for skill in map(Skill._make, result):
			self.skills.append(skill)

	def _getAbilities(self, db):
		self.abilities = []
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
	WHERE A.Name = ? COLLATE NOCASE
	'''
	skillsQueryText = '''
	SELECT S.Name 
		, S.SPCost 
		, S.FrameTime 
		, S.DescriptionLevel1
		, S.DescriptionLevel2
		, S.DescriptionLevel3
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

class Wyrmprint:
	def __init__(self, name):
		self.name = name
		with Database("master.db") as db: 
			if not(self._getWyrmprint(db)):
				self = None
			else:
				self._getAbilities(db)

	def _getWyrmprint(self, db):
		result = db.query(Wyrmprint.wyrmprintQueryText, (self.name,))
		if result == None:
			return False
		result = result[0]
		self.wyrmprintid = result[0]
		self.rarity = result[1]
		self.maxhp = result[2]
		self.maxstr = result[3]
		self.releasedate = result[4]
		self.name = result[5]
		return True
	
	def _getAbilities(self, db):
		self.abilities = []
		result = db.query(Wyrmprint.abilitiesQueryText, (self.wyrmprintid,))
		for ability in map(Ability._make, result):
			self.abilities.append(ability)

	wyrmprintQueryText = '''
	SELECT W.WyrmprintID 
		, W.Rarity
		, W.MaxHP
		, W.MaxSTR
		, W.ReleaseDate 
		, W.Name
	FROM Wyrmprints W
	WHERE W.Name = ? COLLATE NOCASE
	'''
	abilitiesQueryText = '''
	SELECT A.Name 
		, A.Description 
		, WA.Level
	FROM WyrmprintAbilities WA
		INNER JOIN Abilities A ON A.AbilityID = WA.AbilityID 
	WHERE WA.WyrmprintID = ?
	ORDER BY WA.Slot ASC, WA.Level ASC
	'''