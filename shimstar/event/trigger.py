from shimstar.bdd.dbconnector import *
from shimstar.event.event import *

class Trigger:
	def __init__(self,templateId,charId=0):
		self.id=0
		self.type=0
		self.idZone=0
		self.point=(0,0,0)
		self.radius=0
		self.itemTemplate=0
		self.nbTemplate=0
		self.timer=0
		self.npcTemplate=0
		self.order=0
		self.idMission=0
		self.triggerTemplate=templateId
		self.characterId=charId
		self.charState=0
		self.event=None
		self.loadFromTemplate()
		if charId>0:
			self.loadUserFromBdd()
			
	def setCharId(self,c):
		self.characterId=c
		self.loadUserFromBdd()
			
	def loadUserFromBdd(self):
		query="select star066_state,star066_id from star066_trigger_character"
		query+=" where star066_trigger_star064 = " + str(triggerTemplate) + " and star066_character_star002 = " + str(self.characterId)
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.charState=int(row[0])
			self.id=int(row[1])
		cursor.close()

	def saveToBdd(self):
		if self.id>0:
			query="update star066_trigger_character set star066_state = " + str(self.charState) + " where star066_id = " + str(self.id)
			instanceDbConnector=shimDbConnector.getInstance()
			cursor=instanceDbConnector.getConnection().cursor()
			cursor.execute(query)
			cursor.close()
		else:
			query="insert into star066_trigger_character (star066_state,star066_trigger_star064,star066_character_star002)"
			query+=" values(" + str(self.charState) + "," + str(self.triggerTemplate) + "," + str(self.characterId) + ")"
			instanceDbConnector=shimDbConnector.getInstance()
			cursor=instanceDbConnector.getConnection().cursor()
			cursor.execute(query)
			self.id=cursor.lastrowid
			cursor.close()
			
	
	def loadFromTemplate(self):
		query="select star064_type_star065,star064_idzone_star011,star064_point_x,star064_point_y,star064_point_z"
		query+=",star064_radius,star064_itemtemplate_star004,star064_nb_template,star064_timer"
		query+=",star064_npctemplate_star035,star064_order"
		query+=" FROM star064_trigger_mission,star064_idmission_star036"
		query+=" where star064_id = " + str(self.triggerTemplate)
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.type=int(row[0])
			self.idZone=int(row[1])
			self.point=(int(row[2]),int(row[3]),int(row[4]))
			self.radius=int(row[5])
			self.itemTemplate=int(row[6])
			self.nbTemplate=int(row[7])
			self.timer=int(row[8])
			self.npcTemplate=int(row[9])
			self.order=int(row[10])
			self.idMission=int(row[11])
		cursor.close()
		
		self.loadEvent()
		
	def loadEvent(self):
		query="Select star047_id from star047_event where star047_idtrigger_star064 = " + str(self.id)
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.event=Event(int(row[0]))
		cursor.close()
		
	def getEvent(self):
		return self.event
		
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
	
	def getRadius(self):
		return self.radius
		
	def getItemTemplate(self):
		return self.itemTemplate
		
	def getNbTemplate(self):
		return self.nbTemplate
		
	def getTimer(self):
		return self.timer

	def getNpcTemplate(self):
		return self.npcTemplate
		
	def getOrder(self):
		return self.order
