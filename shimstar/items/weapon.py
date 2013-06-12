import os, sys
import xml.dom.minidom
#~ from shimstar.items.bullet import *
from shimstar.core.constantes import *
from shimstar.bdd.dbconnector import *
from shimstar.items.item import *

class Weapon(ShimItem):
	def __init__(self,id,template=0):
		super(Weapon,self).__init__(id,template)	
		self.range=0
		self.damage=0
		self.bullets=[]
		self.cadence=0
		self.lastShot=0
		self.speed=0
		self.place=0
		self.mission=0
		self.zone=0		
		self.loadFromTemplate()
		
	def getBullets(self):
		return self.bullets
		
	def getSpeed(self):
		return self.speed
		
	def getXml(self,docXml=None):
		if docXml==None:
			docXml = xml.dom.minidom.Document()
		itemXml=super(Weapon,self).getXml(docXml)
		nameXml=docXml.createElement("name")
		nameXml.appendChild(docXml.createTextNode(str(self.name)))
		damageXml=docXml.createElement("damage")
		damageXml.appendChild(docXml.createTextNode(str(self.damage)))
		rangeXml=docXml.createElement("range")
		rangeXml.appendChild(docXml.createTextNode(str(self.range)))
		eggXml=docXml.createElement("egg")
		eggXml.appendChild(docXml.createTextNode(str(self.egg)))
		cadenceXml=docXml.createElement("cadence")
		cadenceXml.appendChild(docXml.createTextNode(str(self.cadence)))
		speedXml=docXml.createElement("speed")
		speedXml.appendChild(docXml.createTextNode(str(self.speed)))
		itemXml.appendChild(damageXml)
		itemXml.appendChild(rangeXml)
		itemXml.appendChild(eggXml)
		itemXml.appendChild(cadenceXml)
		itemXml.appendChild(speedXml)
		return itemXml
	
	def getDamage(self):
		return self.damage
		
	def getId(self):
		return self.id
		
	def setZone(self,zone):
		self.zone=zone
		
	def loadFromTemplate(self):
		query="SELECT star018_damage,star018_range,star018_egg,star018_cadence,star018_speed"
		query+=" FROM star004_item_template IT join star018_weapon w on w.star018_id = IT.star004_specific_starxxx "
		query+="WHERE IT.star004_id = '" +str(self.template) + "'"
		#~ print "weapon::loadFRomTempalte " + query
		instanceDbConnector=shimDbConnector.getInstance()

		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.range=int(row[1])
			self.damage=int(row[0])
			self.cadence=float(row[3])
			self.speed=int(row[4])
		cursor.close()
		
	def getRange(self):
		return self.range
				
