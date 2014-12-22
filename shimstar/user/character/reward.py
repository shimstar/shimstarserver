from shimstar.bdd.dbconnector import *

class Reward:
	def __init__(self,id):
		self.id=id
		self.typeReward=0
		self.templateItem=0
		self.nb=0
		self.loadFromBDD()
		
	def loadFromBDD(self):
		query="SELECT star042_typerewards_star043, star042_itemtemplate_star004, star042_nb"
		query+=" FROM star042_rewards_mission where star042_id=" + str(self.id)

		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.typeReward=int(row[0])
			self.templateItem=int(row[1])
			self.nb=int(row[2])
		cursor.close()
		
	def getId(self):
		return self.id
		
	def getTypeReward(self):
		return self.typeReward
		
	def getTemplateItem(self):
		return self.templateItem
		
	def getNb(self):
		return self.nb
		
