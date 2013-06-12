import xml.dom.minidom
from pandac.PandaModules import *
from shimstar.bdd.dbconnector import *
from shimstar.items.ship import *



C_TYPEZONE_ZONE=1
C_TYPEZONE_STATION=2

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
		self.lastStation=1
		if self.id!=0:
			self.loadFromBDD()
			
	def setUserId(self,userId):
		self.userId=userId
		
	def setName(self,name):
		self.name=name
		
	def getClassName(self):
		return character.className
		
	def getZoneId(self):
		return self.zoneId
		
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
		
	def getXml(self,docXml=None):
		if docXml==None:
			docXml = xml.dom.minidom.Document()
		charXml=docXml.createElement("character")
		idXml=docXml.createElement("idchar")
		idXml.appendChild(docXml.createTextNode(str(self.id)))
		nameXml=docXml.createElement("name")
		nameXml.appendChild(docXml.createTextNode(str(self.name)))
		faceXml=docXml.createElement("face")
		faceXml.appendChild(docXml.createTextNode(str(self.face)))
		coinXml=docXml.createElement("coin")
		coinXml.appendChild(docXml.createTextNode(str(self.coin)))
		zoneXml=docXml.createElement("zone")
		zoneXml.appendChild(docXml.createTextNode(str(self.zoneId)))
		laststationXml=docXml.createElement("laststation")
		laststationXml.appendChild(docXml.createTextNode(str(self.lastStation)))
		
		shipXml=self.ship.getXml()
		
		charXml.appendChild(idXml)
		charXml.appendChild(nameXml)
		charXml.appendChild(faceXml)
		charXml.appendChild(coinXml)
		charXml.appendChild(zoneXml)
		charXml.appendChild(shipXml)
		charXml.appendChild(laststationXml)
		
		return charXml
	
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
		#~ print query
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

	def setCurrent(self,current):
		""" 
			set character to current. It is the character choosen to play
		"""
		#~ print "character::setCurrent " + str(self.id) + "/" + str(current)
		self.current=current

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
	