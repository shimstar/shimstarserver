from shimstar.core.constantes import *
from shimstar.bdd.dbconnector import *

class ShimItem(object):
	def __init__(self,id=0,template=0):
		self.id=id
		self.container=0
		self.owner=0
		self.typeItem=0
		self.name=""
		self.template=template
		self.energy=0
		self.owner=0
		self.img=""
		self.cost=0
		self.sell=0
		self.location=0
		self.place=0
		self.mission=0
		self.space=0
		self.id=id
		self.container=0
		self.stackable=0
		self.itemSpecific=0
		self.containertype=""
		self.nb=1
		if self.id>0:
			self.loadFromBdd()
		else:
			self.loadFromTemplate()
		
	def getNb(self):
		return self.nb
		
	def setNb(self,nb):
		self.nb=nb
	
			
	def loadFromBdd(self):
		query="SELECT star006_template_star004,star006_container_starnnn,star006_containertype,star006_owner_star001,star006_location,star006_nb "
		query+=" FROM star006_item "
		query+=" WHERE star006_id = '" + str(self.id) + "'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		
		result_set = cursor.fetchall ()
		for row in result_set:
			self.template=int(row[0])
			self.container=int(row[1])
			self.typeContainer=row[2]
			self.owner=int(row[3])
			self.location=int(row[4])
			self.nb=int(row[5])
		cursor.close()
		self.loadFromTemplate()
		
	def loadFromTemplate(self):
		query="SELECT star004_name, star004_type_star003, star004_energy, star004_img,star004_cost,star004_sell,star004_space,star004_mass,star004_stackable,star004_specific_starxxx "
		query+=" FROM star004_item_template "
		query+=" WHERE star004_id = '" + str(self.template) + "'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.name=row[0]
			self.typeItem=int(row[1])
			self.energy=int(row[2])
			self.img=row[3]
			self.cost=int(row[4])
			self.sell=int(row[5])
			self.space=int(row[6])
			self.mass=float(row[7])
			self.stackable=int(row[8])
			self.itemSpecific=int(row[9])
		cursor.close()
		
	def getOwner(self):
		return self.owner
		
	def delete(self):
		query="DELETE FROM STAR006_item WHERE STAR006_id ='"+ str(self.id) +"'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		cursor.close()
		
	def saveToBDD(self):
		if self.id==0:
			query="INSERT INTO STAR006_ITEM (star006_template_star004,star006_container_starnnn,star006_containertype,star006_location,star006_id_star036,star006_nb) "
			query+=" values ('" + str(self.template) + "','"+str(self.container)+"','"+self.containertype+"','"+ str(self.location)+"','" + str(self.mission) +"','" + str(self.nb) + "')"
		else:
			query="UPDATE STAR006_ITEM SET star006_container_starnnn='"+ str(self.container)+ "', star006_containertype='"+ self.containertype+"', star006_location='" + str(self.location)+ "'"
			query+=", star006_id_star036='" + str(self.mission) + "',star006_nb='" + str(self.nb) +"'"
			query+=" WHERE STAR006_id='"+ str(self.id)+"'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		if self.id==0:
			self.id=int(cursor.lastrowid)
		cursor.close()
	
		instanceDbConnector.commit()
		
	def setContainer(self,id):
		self.container=id
		
	def setMission(self,idMission):
		self.mission=idMission
		
	def getContainerType(self):
		return self.containertype
		
	def setContainerType(self,tc):
		self.containertype=tc
		
	def getContainer(self):
		return self.container
		
	def setOwner(self,id):
		self.owner=id
		
	def getId(self):
		return self.id
		
	def setId(self,id):
		self.id=id
		
	def getTypeItem(self):
		return self.typeItem
		
	def getPlace(self):
		return self.place
	
	def getLocation(self):
		return self.location
		
	def setPlace(self,place):
		self.place=place
		
	def setLocation(self,location):
		self.location=location
		
	def getName(self):
		return self.name
		
	def getImg(self):
		return self.img
		
	def getEnergy(self):
		return self.energy
		
	def getCost(self):
		return self.cost
		
	def getSell(self):
		return self.sell
	
	def getTemplate(self):
		return self.template
		
	def getStackable(self):
		return self.stackable
		
