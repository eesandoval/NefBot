import sqlite3 

class Database:
	def __init__(self, name):
		self.connection = sqlite3.connect(name)
		self.cursor = self.connection.cursor()
	
	def __enter__(self):
		return self 
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		self.commit()
		self.connection.close()

	def commit(self):
		self.connection.commit()

	def execute(self, sql, params=None):
		self.cursor.execute(sql, params or ())

	def fetchall(self):
		return self.cursor.fetchall()

	def fetfchone(self):
		return self.cursor.fetchone()

	def query(self, sql, params=None):
		self.cursor.execute(sql, params or ())
		return self.fetchall()