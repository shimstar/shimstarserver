from shimstar.bdd.dbconnector import *

class Event:
	def __init__(self,id):
		self.id=id
		self.type=0
		self.idZone=0
		self.point=(0,0,0)
		self.idtrigger=0
		self.npcTemplate=0
		self.idMission=0
				
	def loadFromBDD(self):
		query="select star047_type_star048, star047_mission_star036,star047_npc_star035"
		query+=" ,star047_pointX,star047_pointY,star047_pointZ,star047_zone_star011,star047_idtrigger_star064"
		query+=" FROM star047_event "
		query+=" where star047_id = " + str(self.id)
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.type=int(row[0])
			self.idMission=int(row[1])
			self.npcTemplate=int(row[2])
			self.point=(int(row[3]),int(row[4]),int(row[5]))
			self.idZone=int(row[6])
			self.idTrigger=int(row[7])
		cursor.close()
				
	def getIdMission(self):
		return self.idMission
	
	def getId(self):
		return self.id
		
	def getType(self):
		return self.type
	
	def getIdZone(self):
		return self.idZone
		
	def getPoint(self):
		return self.point
	
	def getIdTrigger(self):
		return self.idTrigger
		
	def getNpcTemplate(self):
		return self.npcTemplate
		
