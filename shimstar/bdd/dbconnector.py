import os, sys
import MySQLdb
from direct.stdpy import threading
class shimDbConnector:
	instance=None
	lock=threading.Lock()
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
		self.connection.autocommit(True)
		
	@staticmethod
	def getInstance():
		if shimDbConnector.instance is None:
			shimDbConnector()
		return shimDbConnector.instance
		
	def getConnection(self):
		return self.connection
		
	def commit(self):
		self.connection.commit()
		
	def close(self):
		self.connection.close()
		
	def resetConnection(self):
		shimDbConnector.lock.acquire()
		self.connection.close()
		self.connection=MySQLdb.connect (host = self.host,user = self.user,passwd = self.pwd, db = self.db)
		shimDbConnector.lock.release()
		
	