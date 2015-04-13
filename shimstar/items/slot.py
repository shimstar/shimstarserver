import os, sys
from shimstar.bdd.dbconnector import *
from shimstar.core.constantes import *
from shimstar.items.engine import *
from shimstar.items.weapon import *
import xml.dom.minidom

class Slot:
	def __init__(self,id=0,template=0):
		self.id=id
		self.template=template
		self.location=0
		self.types=[]
		self.nb=0
		self.idShip=0
		self.item=None
		if self.id>0:
			self.loadFromBDD()
		else:
			self.id=template
			self.loadFromBDD()
			self.id=0
			
			
	def sendInfo(self,nm):
		nm.addInt(self.getId())
		nm.addInt(len(self.types))
		for t in self.types:
			nm.addInt(t)
		it=self.getItem()
		if it is not None:
			nm.addInt(it.getTypeItem())
			nm.addInt(it.getTemplate())
			nm.addInt(it.getId())
		else:
			nm.addInt(0)
			nm.addInt(0)
			nm.addInt(0)
			
	def getTypes(self):
		return self.types
			
	def setItem(self,item):
		self.item=item
		if item is not None:
			item.setContainer(self.id)
			item.setContainerType("star009_slot")
			
	def getId(self):
		return self.id
			
	def setShip(self,idShip):
		self.idShip=idShip
	
	def loadFromBDD(self):
		query="SELECT star009_location_star008,star009_numero,star009_item_star006 FROM star009_slot where star009_id ='" +str(self.id) + "' "
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.location=int(row[0])
			self.nb=int(row[1])
			idItem=int(row[2])
		cursor.close()		
		#~ print "slot::loadFromBDD" + str(idItem)
		if idItem>0:
			query="SELECT star004_type_star003,star004_id "
			query +=" FROM star006_item item JOIN star004_item_template itemTemplate ON item.star006_template_star004 = itemTemplate.star004_id "
			query+=" WHERE star006_id = '" + str(idItem) + "'"
			#~ print "### " + str(query)
			cursor=instanceDbConnector.getConnection().cursor()
			cursor.execute(query)
			result_set = cursor.fetchall ()
			
			for row in result_set:
				typeItem=row[0]
				if self.template>0:
					idItem=row[1]
				if typeItem==C_ITEM_ENGINE:
					if self.template>0:
						self.item=Engine(0,idItem)
					else:
						self.item=Engine(idItem)
				elif typeItem==C_ITEM_WEAPON:
					if self.template>0:
						self.item=Weapon(0,idItem)
					else:
						self.item=Weapon(idItem,self)
				#~ elif typeItem==C_ITEM_MINING:
					#~ if self.template>0:
						#~ self.item=miningItem(0,idItem)
					#~ else:
						#~ self.item=miningItem(idItem)
				#~ elif typeItem==C_ITEM_CONTAINER:
					#~ if self.template>0:
						#~ self.item=stockbay(0,idItem)
					#~ else:
						#~ self.item=stockbay(idItem)
				#~ elif typeItem==C_ITEM_RADAR:
					#~ if self.template>0:
						#~ self.item=radaritem(0,idItem)
					#~ else:
						#~ self.item=radaritem(idItem)
			cursor.close()		
		#~ print query
		query="SELECT star021_typeitem_star003 FROM star021_slot_typeitem WHERE star021_slot_star009='" + str(self.id)+ "'"
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.types.append(int(row[0]))
		cursor.close()		
		#~ print self.types
		#~ print self.item
	
	def getItem(self):
		return self.item
		
	def getXml(self,docXml=None):
		if docXml is None:
			docXml = xml.dom.minidom.Document()
		slotXml=docXml.createElement("slot")
		idXml=docXml.createElement("id")
		idXml.appendChild(docXml.createTextNode(str(self.id)))
		locationXml=docXml.createElement("location")
		locationXml.appendChild(docXml.createTextNode(str(self.location)))
		numeroXml=docXml.createElement("numero")
		numeroXml.appendChild(docXml.createTextNode(str(self.nb)))
		typesString=""
		for t in self.types:
			if typesString=="":
				typesString=str(t)
			else:
				typesString+="," + str(t)
		typesXml=docXml.createElement("types")
		typesXml.appendChild(docXml.createTextNode(str(typesString)))
		
		if self.item is not None:
			itemXml=docXml.createElement("item")
			iditemXml=docXml.createElement("iditem")
			iditemXml.appendChild(docXml.createTextNode(str(self.item.getId())))
			typeXml=docXml.createElement("typeitem")
			typeXml.appendChild(docXml.createTextNode(str(self.item.getTypeItem())))
			templateXml=docXml.createElement("template")
			templateXml.appendChild(docXml.createTextNode(str(self.item.getTemplate())))
			itemXml.appendChild(iditemXml)
			itemXml.appendChild(typeXml)
			itemXml.appendChild(templateXml)
			slotXml.appendChild(itemXml)
		
		slotXml.appendChild(idXml)
		slotXml.appendChild(locationXml)
		slotXml.appendChild(typesXml)
		slotXml.appendChild(numeroXml)
		return slotXml
	
	def saveToBDD(self):		
		bNew=False
		if self.id==0:
			bNew=True
			
		if self.item is not None:
			self.item.setContainer(self.id)
			self.item.setContainerType("star009_slot")
			self.item.saveToBDD()
		if self.id>0:
			query="UPDATE star009_slot set star009_item_star006='"
			if self.item is not None:
				query+=str(self.item.getId())
			else:
				query+="0"
			query+="' WHERE STAR009_id = '" + str(self.id) + "'"
		else:
			query="INSERT INTO star009_slot (star009_location_star008,star009_numero,star009_ship_star007,star009_item_star006)"
			query+=" VALUES ('" + str(self.location) + "','" + str(self.nb) + "','"+str(self.idShip)+"','"
			if self.item is not None:
				query+=str(self.item.getId())
			else:
				query+="0"
			query+="')"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		if self.id==0:
			self.id=int(cursor.lastrowid)
			
		cursor.close()
		
		if bNew:
			for t in self.types:
				query="INSERT INTO star021_slot_typeitem (star021_typeitem_star003,star021_slot_star009) values('"+str(t)+"','"+str(self.id)+"')"
				#~ print query
				cursor=instanceDbConnector.getConnection().cursor()
				cursor.execute(query)
				cursor.close()
		
		if self.item is not None:
			self.item.setContainer(self.id)
			self.item.saveToBDD()
		
		instanceDbConnector.commit()
		
	def deleteFromBDD(self):
		query="DELETE FROM star009_slot WHERE STAR009_id='" + str(self.id) + "'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		cursor.close()
		
	def delete(self):
		self.deleteFromBDD()
	
	def getNb(self):
		return self.nb
		
	def getLocation(self):
		return self.location
		