import xml.dom.minidom
from pandac.PandaModules import *
from shimstar.bdd.dbconnector import *
from shimstar.items.ship import *
from shimstar.user.character.mission import *

class character:
	className="character"

	def __init__(self,id=0):
		self.id=id
		self.name=""
		self.className="character"
		self.userId=""
		self.coin=0
		self.face=""
		self.zone=None
		self.zoneId=0
		self.faction=1
		self.current=False
		self.lastStation=3
		self.ship=None
		self.readDialogs=[]
		self.isMining=False
		self.miningAsteroid=None
		self.lastMiningTicks=0
		self.missions=[]
		if self.id!=0:
			self.loadFromBDD()
		#~ print self.ship
		
	def grabMining(self):
		if self.isMining==True:
			if globalClock.getRealTime()-self.lastMiningTicks>0.5:
				self.lastMiningTicks=globalClock.getRealTime()
				return 10
		return 0

	def setMiningAsteroid(self,a):
		self.miningAsteroid=a

	def getMiningAsteroid(self):
		return self.miningAsteroid
	
	def getIsMining(self):
		return self.isMining
		
	def setIsMining(self,m):
		self.isMining=m
		
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
		query="SELECT star002_name,star002_laststation_star022station,star002_face,star002_coin,star002_iduser_star001,star002_zone_star011zone,star002_faction_star059 FROM star002_character WHERE star002_id = '" + str(self.id) + "'"
		shimDbConnector.lock.acquire()
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
			self.faction=int(row[6])
		cursor.close()
		shimDbConnector.lock.release()
		self.loadMissionsFromBDD()
		self.loadShipFromBDD()
		
	def loadMissionsFromBDD(self):
		shimDbConnector.lock.acquire()
		instanceDbConnector=shimDbConnector.getInstance()
		query="SELECT star039_mission_star036,star036_status_star044 FROM star039_character_mission where star039_character_star002='" +str(self.id)+ "'"
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			id=int(row[0])
			tempM=Mission(id,self.id)
			tempM.setCharacterStatus(int(row[1]))
			self.missions.append(tempM)
		cursor.close()
		shimDbConnector.lock.release()
		
	def loadReadDialogs(self):
		query = "select star029_dialogue_star025 from star029_character_dialogue where star029_character_star002 = '" + str(self.id) + "'"
		shimDbConnector.lock.acquire()
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.readDialogs.append(int(row[0]))
		cursor.close()
		shimDbConnector.lock.release()
		
	def getReadDialogs(self):
		if len(self.readDialogs)==0: # if len == 0, maybe there is no readDialogs, or maybe we have just not read it
			self.loadReadDialogs()
		return self.readDialogs
		
	def appendReadDialog(self,idDialogue):
		self.readDialogs.append(idDialogue)
		query = "insert into star029_character_dialogue (star029_dialogue_star025,star029_character_star002)"
		query +=" values ('" + str(idDialogue) + "','" + str(self.id) + "')"
		shimDbConnector.lock.acquire()
		instanceDbConnector=shimDbConnector.getInstance()

		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		cursor.close()
			
		instanceDbConnector.commit()
		shimDbConnector.lock.release()
		
	def saveReadDialog(self):
		query = "delete from star029_character_dialog where star029_character_star002 =  '" + str(self.id) + "'"
		shimDbConnector.lock.acquire()
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
		shimDbConnector.lock.release()
		
	def loadShipFromBDD(self):
		"""
			load current ship from bdd
		"""
		query="SELECT star007_id FROM star007_ship ship JOIN  star006_item item ON item.star006_id=ship.star007_item_star006 WHERE star007_fitted=1 and  star006_container_starnnn='" + str(self.id) + "' AND star006_containertype='star002_character'"
		shimDbConnector.lock.acquire()
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
		shimDbConnector.lock.release()
		
	def sendInfo(self,nm):
		nm.addInt(self.id)
		nm.addString(self.name)
		nm.addString(self.face)
		nm.addInt(self.zoneId)
		
	def sendMission(self,nm):
		nm.addInt(len(self.missions))
		for m in self.missions:
			nm.addInt(m.getId())
			nm.addInt(m.getStatus())
			
	def sendReadDialogs(self,nm):
		self.getReadDialogs()
		nm.addInt(len(self.readDialogs))
		for d in self.readDialogs:
			nm.addInt(d)
		
	def sendCompleteInfoForStation(self,nm):
		self.ship.sendInfo(nm)
		self.sendReadDialogs(nm)
		self.sendMission(nm)
		
	def sendCompleteInfo(self,nm):
		self.ship.sendInfo(nm)
		self.sendMission(nm)
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
		shimDbConnector.lock.acquire()
		instanceDbConnector=shimDbConnector.getInstance()
		instanceDbConnector.commit()
		shimDbConnector.lock.release()
		
	def saveCharacterToBDD(self):
		if self.id>0:
			query="update star002_character SET star002_zone_star011zone='" +str(self.zoneId) +  "',star002_coin='" + str(self.coin)+ "',star002_laststation_star022station='"+ str(self.lastStation)+"'"
			query+=" WHERE star002_id='" +str(self.id) + "'"
		else:
			query="insert into star002_character (star002_iduser_star001,star002_name,star002_face,star002_coin,star002_zone_star011zone,star002_laststation_star022station)"
			query+=" values ('"+ str(self.userId) + "','"+self.name+"','"+self.face+"',0,"+str(C_STARTING_ZONE)+"," + str(C_STARTING_ZONE) +")"
		shimDbConnector.lock.acquire()
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		
		if self.id==0:
			self.id=cursor.lastrowid
		cursor.close()
		instanceDbConnector.commit()
		shimDbConnector.lock.release()
	
	def saveToBDD(self):
		"""
			main save
		"""
		self.saveCharacterToBDD()
		self.saveMissionToBDD()
		self.ship.saveToBDD()

	
	def saveMissionToBDD(self):		
		shimDbConnector.lock.acquire()
		instanceDbConnector=shimDbConnector.getInstance()
		for m in self.missions:
			query="SELECT star039_mission_star036 FROM star039_character_mission where star039_character_star002='" +str(self.id)+ "' AND star039_mission_star036='"+str(m.getId())+"'"
			
			cursor=instanceDbConnector.getConnection().cursor()
			cursor.execute(query)
			result_set = cursor.fetchall ()
			id=-1
			for row in result_set:
				id=int(row[0])
			cursor.close()
			if id==-1:
				query="INSERT INTO star039_character_mission (star039_mission_star036,star039_character_star002,star036_status_star044) value('"+str(m.getId())+"','"+str(self.id)+"','1')"
				cursor=instanceDbConnector.getConnection().cursor()
				cursor.execute(query)
				cursor.close()
				objectifs=m.getObjectifs()
				for o in objectifs:
					query="INSERT INTO star040_character_objectif (star040_character_star002,star040_objectif_star038,star040_nbitem)"
					query+=" values ('"+str(self.id)+"','"+str(o.getId())+"',0)"
					cursor=instanceDbConnector.getConnection().cursor()
					cursor.execute(query)
					cursor.close()
			else:
				query="UPDATE star039_character_mission set star036_status_star044='" + str(m.getStatus()) + "' WHERE star039_character_star002='" + str(self.getId()) + "' and star039_mission_star036 = '" + str(m.getId()) + "'"
				cursor=instanceDbConnector.getConnection().cursor()
				cursor.execute(query)
				cursor.close()
				objectifs=m.getObjectifs()
				for o in objectifs:
					query="UPDATE star040_character_objectif set star040_nbitem='" + str(o.getNbItemCharacter()) + "' WHERE star040_character_star002='" + str(self.id) + "'"
					query+="AND star040_objectif_star038='" + str(o.getId()) + "'"
					cursor=instanceDbConnector.getConnection().cursor()
					cursor.execute(query)
					cursor.close()
				
		missionToRemove=[]
		query="SELECT star039_mission_star036 FROM star039_character_mission where star039_character_star002='" +str(self.id)+ "'"
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			id=int(row[0])
			found=False
			for m in self.missions:
				if m.getId()==id:
					found=True
					break
			if found==False:
				missionToRemove.append(id)
			
		cursor.close()
		for m in missionToRemove:
			query="DELETE FROM star039_character_mission where star039_character_star002='" +str(self.id)+ "' and star039_mission_star036='"+str(m)+"'"
			cursor=instanceDbConnector.getConnection().cursor()
			cursor.execute(query)
			cursor.close()
			mi=mission(m)
			objectifs=mi.getObjectifs()
			for o in objectifs:
				query="DELETE FROM star040_character_objectif WHERE star040_character_star002='" +str(self.id)+ "' and star040_objectif_star038='" + str(o.getId()) + "'"
				cursor=instanceDbConnector.getConnection().cursor()
				cursor.execute(query)
				cursor.close()
			
		instanceDbConnector.commit()
		shimDbConnector.lock.release()

	def delete(self):
		query="DELETE FROM star002_character WHERE STAR002_id ='"+ str(self.id)+"'"
		shimDbConnector.lock.acquire()
		instanceDbConnector=shimDbConnector.getInstance()

		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		cursor.close()
		instanceDbConnector.commit()
		shimDbConnector.lock.release()

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
		print "Character :: destroy " + str(self.id)
		if self.ship!=None:
			self.ship.destroy()
		
	def acceptMission(self,idMission):
		"""
			Manage the accept mission action
		"""
		found=False
		for m in self.missions:
			if m.getId()==int(idMission):
				found=True
				break
		if found==False:
			mi=Mission(idMission,self.id)
			mi.setCharacterStatus(C_STATEMISSION_INPROGRESS)
			self.missions.append(mi)
			preItems=mi.getPreItems()
			for p in preItems:
				if self.missionItemBelongsToCharacter(mi.getId(),p)==False:
					newItem=self.ship.addItemFromTemplateInInventory(p)
					newItem.setMission(mi.getId())
					#~ networkmessage.instance.addMessage(C_CHAR_UPDATE,str(self.userId) + "/" + str(self.id) + "/additem=" + str(newItem.getXml().toxml()),self.connexion)
			self.saveToBDD()
			