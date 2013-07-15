import os, sys
import xml.dom.minidom
from shimstar.bdd.dbconnector import *
from shimstar.user.character.character import *
from direct.stdpy import threading

class User(threading.Thread):
	listOfUser={}
	lock=threading.Lock()

	def __init__(self,name="",id=0,new=False):
		#~ print "user::init " + str(usr)
		threading.Thread.__init__(self)
		self.id=id
		self.name=name
		self.password=""
		self.ip=""
		self.newToZone=1
		self.listOfCharacter=[]
		self.connexion=None
		if new==False:
			self.loadFromBdd()			
		User.listOfUser[self.id]=self
		
	def isNewToZone(self):
		return self.newToZone
		
	def setNewToZone(self,val):
		self.newToZone=val
		
	def setIp(self,ip):
		self.ip=ip
		
	def getIp(self):
		return self.ip
		
	def setConnexion(self,connexion):
		self.connexion=connexion
		
	def getConnexion(self):
		return self.connexion
	
	def getPwd(self):
		return self.password
		
	def getName(self):
		return self.name
		
	def setCurrentCharacter(self,idchar):
		for ch in self.listOfCharacter:
			if ch.getId()==idchar:
				ch.setCurrent(True)
			else:
				ch.setCurrent(False)
				
	def getCurrentCharacter(self):
		for ch in self.listOfCharacter:
			if ch.getIsCurrent()==True:
				return ch
		return None
		
	def destroy(self):
		User.lock.acquire()
		if User.listOfUser.has_key(self.id):
			del User.listOfUser[self.id]
			
		User.lock.release()
		
	def getXml(self):
		doc = xml.dom.minidom.Document()
		usr=doc.createElement("user")
		uname=doc.createElement("name")
		uname.appendChild(doc.createTextNode(self.name))
		idUser=doc.createElement("iduser")
		idUser.appendChild(doc.createTextNode(str(self.id)))
		usr.appendChild(uname)
		usr.appendChild(idUser)
		if len(self.listOfCharacter)>0:
			chars=doc.createElement("characters")
			for chr in self.listOfCharacter:
				chars.appendChild(chr.getXml())
			usr.appendChild(chars)
				
		doc.appendChild(usr)
		
		return doc
	
	@staticmethod
	def getUserById(id):
		for usr in User.listOfUser:
			if User.listOfUser[usr].getId()==id:
				return User.listOfUser[usr]
		return None
	
	
	@staticmethod
	def getUserInstantiatedByName(name):
		for usr in User.listOfUser:
			if User.listOfUser[usr].getName()==name:
				return True
		return False
		
	def getId(self):
		return self.id
	
	def loadFromBdd(self):
		if self.id==0:
			query="SELECT star001_passwd,star001_id,star001_name FROM star001_user WHERE star001_name = '" + str(self.name) + "'"
		else:
			query="SELECT star001_passwd,star001_id,star001_name FROM star001_user WHERE star001_id = '" + str(self.name) + "'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.name=row[2]
			self.id=int(row[1])
			self.password=row[0]
		cursor.close()
		
		query="SELECT star002_id FROM star002_character WHERE star002_iduser_star001='" + str(self.id) + "'"
		#~ print "user::loadFromBdd " + str(query)
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			tempChar=character(row[0])
			tempChar.setUserId(self.id)
			self.listOfCharacter.append(tempChar)
		cursor.close()
		
	@staticmethod
	def userExists(name):
		"""
		return False if user doesn't exist for the moment
		return True if user exists already
		"""
		id=0
		query="SELECT star001_id FROM star001_user WHERE star001_name = '" + name + "'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			id=int(row[0])
		cursor.close()
		if id>0:
			return True
		return False