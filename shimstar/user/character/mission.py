import xml.dom.minidom
import os, sys
from shimstar.bdd.dbconnector import *
from shimstar.core.constantes import *
from shimstar.user.character.objectif import *
from shimstar.user.character.reward import *
from shimstar.event.trigger import *

C_TYPE_MISSION_SHIPTODESTROY=1
C_STATEMISSION_DONTHAVE=0
C_STATEMISSION_GOTIT=1
C_STATEMISSION_SUCCESS=2
C_STATEMISSION_FINISHED=3
C_TYPEMISSION_COIN=1

class Mission:
	def __init__(self,id,ichar=0):
		self.id=int(id)
		self.idChar=ichar
		self.label=""
		self.preItems=[]
		self.status=0
		self.events=[]
		self.triggers={}
		self.loadFromBDD()
		
	def getId(self):
		return self.id
		
	def loadFromBDD(self):
		query="SELECT star036_label,star036_endingnpc_star034 FROM star036_mission where star036_id='" + str(self.id) + "'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.label=row[0]
			self.endingNPC=int(row[1])
		cursor.close()
		
		self.loadPreItems()
		self.loadObjectifFromBDD()
		self.loadRewardsFromBDD()
		self.loadTriggerFromBDD()
	
	def loadPreItems(self):
		query="SELECT star041_itemtemplate_star004, star041_nb FROM  star041_givenitem_mission where star041_mission_star036='" + str(self.id) + "'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			nb=int(row[1])
			for i in range(nb):
				self.preItems.append(int(row[0]))
		cursor.close()
		
	def loadTriggerFromBDD(self):
		self.triggers={}
		query="SELECT star064_id FROM STAR064_trigger_mission WHERE star064_idmission_star036=" + str(self.id)
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			temp=Trigger(int(row[0]))
			temp.setCharId(self.idChar)
			self.triggers[temp.getOrder()]=temp
		cursor.close()
		
		
	def loadObjectifFromBDD(self):
		self.objectifs=[]
		query="SELECT star038_id FROM STAR038_OBJECTIF WHERE star038_mission_star036=" + str(self.id)
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			tempObjectif=Objectif(row[0])
			self.objectifs.append(tempObjectif)
		cursor.close()
		
		if self.idChar>0:
			for o in self.objectifs:
				query="SELECT star040_nbitem FROM star040_character_objectif WHERE star040_character_star002='" + str(self.idChar) + "' and star040_objectif_star038='" + str(self.id) + "'"
			cursor=instanceDbConnector.getConnection().cursor()
			cursor.execute(query)
			result_set = cursor.fetchall ()
			for row in result_set:
				nbItem=int(row[0])
				o.setNbItemCharacter(nbItem)
			cursor.close()
		
	def loadRewardsFromBDD(self):
		self.rewards=[]
		query="SELECT star042_id FROM STAR042_rewards_mission WHERE star042_mission_star036=" + str(self.id)
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.rewards.append(Reward(row[0]))
		cursor.close()
		
	def loadEventFromBDD(self):
		self.events=[]
		query="SELECT star047_id FROM STAR047_event WHERE star047_mission_star036 = '" + str(self.id) + "'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.events.append(event(row[0]))
		cursor.close()
		
	def getEvents(self):
		return self.events
		
	def setCharacterStatus(self,status):
		self.status=status
		
	def getStatus(self):
		return self.status
		
	def setStatus(self,status):
		self.status=status
		
	def getObjectifs(self):
		return self.objectifs

	def getId(self):
		return self.id
		
	def getRewards(self):
		return self.rewards
		
	def getEndingNPC(self):
		return self.endingNPC
		
	def getPreItems(self):
		return self.preItems
		
	def evaluateStatus(self):
		"""
			each time, an objectif is updated, evaluate new status of the mission. Is it still in progress, or maybe it is successfull.
		"""
		finished=False
		for o in self.objectifs:
			if o.getIdType()==C_OBJECTIF_DESTROY:
				if o.getNbItemCharacter()==o.getNbItem():
					finished=True
			else:
				finished=False
				break
				
		if finished==True:
			self.status=C_STATEMISSION_SUCCESS
		