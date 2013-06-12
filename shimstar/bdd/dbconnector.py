import os, sys
import MySQLdb

class shimDbConnector:
	instance=None
	def __init__(self):
		self.host="localhost"
		#~ self.host="62.147.217.96"
		#~ self.host="192.168.0.254"
		#~ self.host="thyshimrod.praesepe.net"
		
		self.user="shimstar"
		self.pwd="shimstar"
		self.db="shimstar"
		shimDbConnector.instance=self
		self.connection = MySQLdb.connect (host = self.host,user = self.user,passwd = self.pwd, db = self.db)
		
	@staticmethod
	def getInstance():
		if shimDbConnector.instance==None:
			shimDbConnector()
		return shimDbConnector.instance
		
	def getConnection(self):
		return self.connection
		
	def commit(self):
		self.connection.commit()
		
	def close(self):
		self.connection.close()
		
	