from shimstar.bdd.dbconnector import *
from shimstar.core.constantes import *

class Objectif:
	def __init__(self,id):
		self.id=id
		self.nbItemCharacter=0
		self.loadFromBDD()
		self.status=False
		
	def loadFromBDD(self):
		query="SELECT star038_mission_star036, star038_type_star037, star038_text, star038_item_starXXX,star038_item_table, star038_zone_star012,star038_nbitem"
		query+=" FROM star038_objectif where star038_id=" + str(self.id)

		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.idType=int(row[1])
			self.text=row[2]
			self.idItem=int(row[3])
			self.tableItem=row[4]
			self.zone=int(row[5])
			self.nbItem=int(row[6])
		cursor.close()
		
	def checkStatus(self):
		self.status=False
		if self.idType==C_OBJECTIF_DESTROY:
			if self.nbItemCharacter>=self.nbItem:
				self.status=True
		
	def setNbItemCharacter(self,nb):
		self.nbItemCharacter=nb
		
	def getNbItemCharacter(self):
		return self.nbItemCharacter
		
	def getId(self):
		return self.id
		
	def getIdType(self):
		return self.idType
		
	def getText(self):
		return self.text
		
	def getIdItem(self):
		return self.idItem
		
	def getTableItem(self):
		return self.tableItem
		
	def getZone(self):
		return self.zone
		
	def getNbItem(self):
		return self.nbItem
		
	def getStatus(self):
		self.checkStatus()
		return self.status
		
	def setStatus(self,status):
		self.status=status
		
		
	