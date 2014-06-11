import os, sys
import xml.dom.minidom
from shimstar.bdd.dbconnector import *
from shimstar.user.character.character import *
from direct.stdpy import threading

class User(threading.Thread):
	listOfUser={}
	lock=threading.Lock()

	def __init__(self,name="",id=0,new=False):
		threading.Thread.__init__(self)
		self.id=id
		self.name=name
		self.password=""
		self.ip=""
		self.portUdp=0
		self.newToZone=1
		self.listOfCharacter=[]
		self.connexion=None
		if new==False:
			self.loadFromBdd()			
		print "user::init " + str(self.id) 
		User.lock.acquire()
		User.listOfUser[self.id]=self
		User.lock.release()
	
	def getPos(self):
		return self.getCurrentCharacter().getPos()
		
	def changeZone(self,idZone):
		self.getCurrentCharacter().setZoneId(idZone)
		
	def getQuat(self):
		return self.getCurrentCharacter().getQuat()
	
	@staticmethod
	def userExists(name):
		"""
		return False if user doesn't exist for the moment
		return True if user exists already
		"""
		id=0
		query="SELECT star001_id FROM star001_user WHERE star001_name = '" + name + "'"
		shimDbConnector.lock.acquire()
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			id=int(row[0])
		cursor.close()
		shimDbConnector.lock.release()
		if id>0:
			return True
		return False
		
	def isNewToZone(self):
		return self.newToZone
		
	def setNewToZone(self,val):
		self.newToZone=val
		
	def setCurrent(self,id,nm):
		for charact in self.listOfCharacter:
			if charact.getId()==id:
				charact.setCurrent(True,nm)
			else:
				charact.setCurrent(False)
		
	def setIp(self,ip):
		self.ip=ip
		
	def setUdpPort(self,port):
		self.portUdp=port
		
	def getUdpPort(self):
		return self.portUdp
		
	def setPwd(self,pwd):
		self.password=pwd
		
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
		print "user::setCurrentCharacter " + str(idchar) + "/" +str(self.listOfCharacter)
		for ch in self.listOfCharacter:
			print "user::setCurrentCharacter " + str(ch.getId())
			if ch.getId()==idchar:
				ch.setCurrent(True)
			else:
				ch.setCurrent(False)
				
	def getCurrentCharacter(self):
		for ch in self.listOfCharacter:
			if ch.getIsCurrent()==True:
				return ch
		return None
		
	@staticmethod
	def destroyUserById(id):
		User.lock.acquire()
		if User.listOfUser.has_key(id):
			User.listOfUser[id].destroy()
		if User.listOfUser.has_key(id):
			del User.listOfUser[id]
		User.lock.release()
		
	def destroy(self):
		#~ print "user::destroy " + str(self.id)
		User.lock.acquire()
		if User.listOfUser.has_key(self.id):
			for ch in self.listOfCharacter:
				ch.destroy()
			del User.listOfUser[self.id]
		User.lock.release()
		
	def sendInfo(self,nm):
		nm.addInt(self.id)
		nm.addString(self.name)
		nm.addInt(len(self.listOfCharacter))
		if len(self.listOfCharacter)>0:
			for chr in self.listOfCharacter:
				chr.sendInfo(nm)
				
	def sendInfoOtherPlayer(self,nm):
		nm.addInt(self.id)
		nm.addString(self.name)
		currentChar=self.getCurrentCharacter()
		currentChar.sendInfo(nm)
		currentChar.sendCompleteInfo(nm)
				
	def sendInfoCharForStation(self,nm):
		currentChar=self.getCurrentCharacter()
		if currentChar!=None:
			currentChar.sendCompleteInfoForStation(nm)
		else:
			print "user::sendInfoChar No currentChar"
				
				
	def sendInfoChar(self,nm):
		currentChar=self.getCurrentCharacter()
		if currentChar!=None:
			currentChar.sendCompleteInfo(nm)
		else:
			print "user::sendInfoChar No currentChar"
		
	def deleteCharacter(self,id):
		for ch in self.listOfCharacter:
			if ch.getId()==id:
				ch.destroy()
				ch.delete()
				
	def getCharacterById(self,id):
		for c in self.listOfCharacter:
			if c.getId()==id:
				return c
				
		return None
	
	def addCharacter(self,name,face):
		"""
			params:
				name
				face
			create a new character with few starting skills (laser light, hunter light, pilotage, weapon)
		"""
		print "user::addcharacter "
		temp=character(0)
		temp.setFace(face)
		temp.setName(name)
		temp.setUserId(self.id)
		temp.zoneId=C_STARTING_ZONE
		self.listOfCharacter.append(temp)
		self.saveToBDD()
		temp.addShip(1)
		return temp
	
	@staticmethod
	def getUserById(id):
		User.lock.acquire()
		for usr in User.listOfUser:
			if User.listOfUser[usr].getId()==id:
				User.lock.release()
				return User.listOfUser[usr]
		User.lock.release()
		return None
	
	
	@staticmethod
	def getUserInstantiatedByName(name):
		User.lock.acquire()
		for usr in User.listOfUser:
			if User.listOfUser[usr].getName()==name:
				User.lock.release()
				return User.listOfUser[usr]
		User.lock.release()
		return None
		
	def getId(self):
		return self.id
	
	def loadFromBdd(self):
		shimDbConnector.lock.acquire()
		shimDbConnector.getInstance().resetConnection()
		if self.id==0:
			query="SELECT star001_passwd,star001_id,star001_name FROM star001_user WHERE star001_name = '" + str(self.name) + "'"
		else:
			query="SELECT star001_passwd,star001_id,star001_name FROM star001_user WHERE star001_id = '" + str(self.id) + "'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		#~ print query
		result_set = cursor.fetchall ()
		for row in result_set:
			self.name=row[2]
			self.id=int(row[1])
			self.password=row[0]
		cursor.close()
		#~ print "user::loadFromBdd 2 " + str(self.name)
		
		query="SELECT star002_id FROM star002_character WHERE star002_iduser_star001='" + str(self.id) + "'"
		#~ print "user::loadFromBdd " + str(query)
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			tempChar=character(int(row[0]))
			tempChar.setUserId(self.id)
			self.listOfCharacter.append(tempChar)
		cursor.close()
		shimDbConnector.lock.release()
		
	def saveToBDD(self):
		instanceDbConnector=shimDbConnector.getInstance()
		if self.id==0:
			query="insert into star001_user (star001_name,star001_passwd,star001_created) values('" + self.name + "','"+self.password+"',now())"
			cursor=instanceDbConnector.getConnection().cursor()
			cursor.execute(query)
			self.id=int(cursor.lastrowid)
			cursor.close()
			
		for ch in self.listOfCharacter:
			ch.saveToBDD()
		
		instanceDbConnector.commit()
		
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