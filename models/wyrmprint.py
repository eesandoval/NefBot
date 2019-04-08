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

class Wyrmprint:
	@staticmethod
	def findWyrmprints(ability=None, rarity=None, level=2):
		wyrmprints = []
		params = ()
		fullQuery = Wyrmprint.wyrmprintSearchQueryText
		if ability != None:
			fullQuery += "AND A.name LIKE '%' || ? || '%' COLLATE NOCASE "
			params += (ability,)
		if rarity != None:
			fullQuery += "AND W.rarity >= ? "
			params += (rarity,)
		if level != None:
			fullQuery += "AND WA.level = ? "
			params += (level,)
		if len(params) == 0:
			return wyrmprints 
		with Database("master.db") as db:
			result = db.query(fullQuery, params)
		if result == None:
			return wyrmprints 
		for wyrmprint in result:
			wyrmprints.append(Wyrmprint(wyrmprint[0], wyrmprint[1]))
		return wyrmprints 

	def __init__(self, name, level=2):
		self.name = name
		with Database("master.db") as db: 
			if not(self._getWyrmprint(db)):
				self = None
			else:
				self._getAbilities(db, level)

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
	
	def _getAbilities(self, db, level):
		self.abilities = []
		result = db.query(Wyrmprint.abilitiesQueryText, (self.wyrmprintid,level,))
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
		AND WA.Level = ?
	ORDER BY WA.Slot ASC, WA.Level ASC
	'''
	wyrmprintSearchQueryText = '''
	SELECT DISTINCT W.Name
		, WA.Level
	FROM Wyrmprints W
		INNER JOIN WyrmprintAbilities WA ON WA.WyrmprintID = W.WyrmprintID
		INNER JOIN Abilities A ON A.AbilityID = WA.AbilityID
	WHERE 1=1 
	'''