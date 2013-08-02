import os, sys
import xml.dom.minidom
from shimstar.core.constantes import *
from shimstar.bdd.dbconnector import *
from shimstar.items.item import *

class Engine(ShimItem):
	def __init__(self,id,template=0):
		self.typeEngine=0
		self.speedMax=0
		self.acceleration=0
		super(Engine,self).__init__(id,template)	
		super(Engine,self).loadFromBdd()
		self.loadFromTemplate()
			
		
	def getXml(self,docXml=None):
		itemXml=super(Engine,self).getXml(docXml)
		if docXml==None:
			docXml = xml.dom.minidom.Document()
		speedXml=docXml.createElement("speedMax")
		speedXml.appendChild(docXml.createTextNode(str(self.speedMax)))
		accelerationXml=docXml.createElement("acceleration")
		accelerationXml.appendChild(docXml.createTextNode(str(self.acceleration)))
		
		itemXml.appendChild(speedXml)
		itemXml.appendChild(accelerationXml)
				
		return itemXml
		
	def loadFromTemplate(self):
		query="SELECT star017_acceleration,star017_speed"
		query+=" FROM star004_item_template IT"
		query+=" join star017_engine w on w.star017_id = IT.star004_specific_starxxx "
		query+="WHERE IT.star004_id = '" +str(self.template) + "'"
		#~ print query
		instanceDbConnector=shimDbConnector.getInstance()

		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.speedMax=int(row[1])
			self.acceleration=int(row[0])
		cursor.close()
		
		super(Engine,self).loadFromTemplate()	
				
	def getSpeedMax(self):
		return self.speedMax
		
	def getAcceleration(self):
		return self.acceleration
				
