import xml.dom.minidom
from pandac.PandaModules import *
from shimstar.bdd.dbconnector import *
from shimstar.items.ship import *

class character:
	className="character"

	def __init__(self,id=0):
		self.id=id
		self.name=""
		self.userId=""
		self.coin=0
		self.face=""
		self.zone=None
		self.zoneId=0
		self.current=False
		self.lastStation=3
		self.ship=None
		self.readDialogs=[]
		if self.id!=0:
			self.loadFromBDD()
		#~ print self.ship
		
	def manageDeathFromMainServer(self):
		self.ship.deleteFromBdd()
		self.ship.destroy()
		self.ship=None
		self.addShip(1)
			
	def setZoneId(self,id):
		self.zoneId=id
			
	def getShip(self):
		return self.ship
	
	def getId(self):
		return self.id
			
	def setUserId(self,userId):
		self.userId=userId
		
	def setName(self,name):
		self.name=name
		
	def getClassName(self):
		return character.className
		
	def getZoneId(self):
		return self.zoneId
		
	def getLastStation(self):
		return self.lastStation
		
	def loadFromBDD(self):
		"""
			main loading of character
		"""
		query="SELECT star002_name,star002_laststation_star022station,star002_face,star002_coin,star002_iduser_star001,star002_zone_star011zone FROM star002_character WHERE star002_id = '" + str(self.id) + "'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.name=row[0]
			self.lastStation=row[1]
			self.face=row[2]
			self.coin=row[3]
			self.user=row[4]
			self.zoneId=row[5]
		cursor.close()
		
		self.loadShipFromBDD()
		
	def loadReadDialogs(self):
		query = "select star029_dialogue_star025 from star029_character_dialogue where star029_character_star002 = '" + str(self.id) + "'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.readDialogs.append(int(row[0]))
		cursor.close()
		
	def getReadDialogs(self):
		if len(self.readDialogs)==0: # if len == 0, maybe there is no readDialogs, or maybe we have just not read it
			self.loadReadDialogs()
		return self.readDialogs
		
	def appendReadDialog(self,idDialogue):
		self.readDialogs.append(idDialogue)
		query = "insert into star029_character_dialogue (star029_dialogue_star025,star028_character_star002)"
		query +=" values ('" + str(r) + "','" + str(self.id) + "')"
		instanceDbConnector=shimDbConnector.getInstance()

		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		cursor.close()
			
		instanceDbConnector.commit()
		
	def saveReadDialog(self):
		query = "delete from star029_character_dialog where star029_character_star002 =  '" + str(self.id) + "'"
		instanceDbConnector=shimDbConnector.getInstance()

		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		cursor.close()
		for r in self.readDialogs:
			query = "insert into star029_character_dialogue (star029_dialogue_star025,star028_character_star002)"
			query +=" values ('" + str(r) + "','" + str(self.id) + "')"
			instanceDbConnector=shimDbConnector.getInstance()

			cursor=instanceDbConnector.getConnection().cursor()
			cursor.execute(query)
			cursor.close()
			
		instanceDbConnector.commit()
		
	def sendReadDialogs(self,nm):
		nm.addInt(len(self.readDialogs))
		for d in self.readDialogs:
			nm.addInt(d)
		
	def loadShipFromBDD(self):
		"""
			load current ship from bdd
		"""
		query="SELECT star007_id FROM star007_ship ship JOIN  star006_item item ON item.star006_id=ship.star007_item_star006 WHERE star007_fitted=1 and  star006_container_starnnn='" + str(self.id) + "' AND star006_containertype='star002_character'"
		instanceDbConnector=shimDbConnector.getInstance()

		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.ship=Ship(int(row[0]))

		if self.ship==None:
			self.addShip(1)

		self.ship.setOwner(self)
		cursor.close()
		
	def sendInfo(self,nm):
		nm.addInt(self.id)
		nm.addString(self.name)
		nm.addString(self.face)
		nm.addInt(self.zoneId)
		
	def sendCompleteInfo(self,nm):
		self.ship.sendInfo(nm)
		#~ nm.addInt(self.ship.getTemplate())
		
	def setCurrent(self,current,nm=None):
		""" 
			set character to current. It is the character choosen to play
		"""
		#~ print "character::setCurrent " + str(self.id) + "/" + str(current)
		self.current=current
		if current==True:
			if nm!=None:
				self.ship.sendInfo(nm)
		
	def getPos(self):
		return self.ship.getPos()
	
	def getQuat(self):
		return self.ship.getQuat()
		
	def addShip(self,type):
		"""
			change ship of the character (ie : when the death is coming)
		"""
		self.ship=Ship(0,type)
		self.ship.setOwner(self)
		self.ship.saveToBDD()

		instanceDbConnector=shimDbConnector.getInstance()
		instanceDbConnector.commit()
	
	def saveToBDD(self):
		"""
			main save
		"""
		if self.id>0:
			query="update star002_character SET star002_zone_star011zone='" +str(self.zoneId) +  "',star002_coin='" + str(self.coin)+ "',star002_laststation_star022station='"+ str(self.lastStation)+"'"
			query+=" WHERE star002_id='" +str(self.id) + "'"
		else:
			query="insert into star002_character (star002_iduser_star001,star002_name,star002_face,star002_coin,star002_zone_star011zone,star002_laststation_star022station)"
			query+=" values ('"+ str(self.userId) + "','"+self.name+"','"+self.face+"',0,"+str(C_STARTING_ZONE)+"," + str(C_STARTING_ZONE) +")"
		
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		if self.id==0:
			self.id=cursor.lastrowid
		cursor.close()
		instanceDbConnector.commit()
		

	def delete(self):
		query="DELETE FROM star002_character WHERE STAR002_id ='"+ str(self.id)+"'"
		instanceDbConnector=shimDbConnector.getInstance()

		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		cursor.close()
		instanceDbConnector.commit()

	
	def getIsCurrent(self):
		return self.current

	def getName(self):
		return self.name
	
	def getCoin(self):
		return self.coin
		
	def setCoin(self,coin):
		self.coin=coin

	def setFace(self,face):
		self.face=face
		
	def getFace(self):
		return self.face
	
	def destroy(self):
		if self.ship!=None:
			self.ship.destroy()
		