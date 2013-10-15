from shimstar.core.constantes import *
from shimstar.bdd.dbconnector import *
import os, sys
import os.path
import xml.dom.minidom
from shimstar.npc.intelligence.attitude import *
from shimstar.items.ship import *

class NPC:
	listOfNpc={}
	def __init__(self,id=0,idtemplate=0,zone=0):
		self.zone=zone
		self.ship=None
		self.template=idtemplate
		self.id=id
		self.idEvent=0
		self.faction=0
		self.attitude=Attitude(self)
		
		if self.id!=0:
			self.loadFromBDD()
		else:
			self.loadTemplateFromBDD()
			
		NPC.listOfNpc[self.id]=self
		
	def getId(self):
		return self.id
		
	def sendInfo(self,nm):
		#~ print "npc::sendinfo " + str(self.ship.getTemplate())
		nm.addInt(self.id)
		nm.addString(self.name)
		nm.addInt(self.template)
		nm.addInt(self.ship.getTemplate())
		
		
	def getClassName(self):
		return "NPC"
		
	def runPhysics(self):
		if self.attitude!=None:
			self.attitude.run()
			self.attitude.runPhysics()
		
	def getPos(self):
		return self.ship.getPos()
		
	def getQuat(self):
		return self.ship.getQuat()
		
	def getShip(self):
		return self.ship
	
	def getXml(self):
		doc = xml.dom.minidom.Document()
		npcxml=doc.createElement("npc")
		nameNpc=doc.createElement("name")
		nameNpc.appendChild(doc.createTextNode(self.name))
		idNpc=doc.createElement("idnpc")
		idNpc.appendChild(doc.createTextNode(str(str(self.id))))
		idZoneNpc=doc.createElement("idZone")
		idZoneNpc.appendChild(doc.createTextNode(str(self.zone.id)))
		factionNpc=doc.createElement("faction")
		factionNpc.appendChild(doc.createTextNode(str(self.faction)))
		npcxml.appendChild(nameNpc)
		npcxml.appendChild(idNpc)
		npcxml.appendChild(idZoneNpc)
		npcxml.appendChild(self.ship.getXml())
		doc.appendChild(npcxml)
		return doc
		
	def loadFromBDD(self):
		query="SELECT star034_name,star034_zone_star011zone,star034_template_star035,star034_event_star047 FROM star034_npc WHERE star034_id='"+ str(self.id) +"'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.name=row[0]
			self.template=int(row[2])
			self.idEvent=int(row[3])
		cursor.close()
		self.loadShipFromBDD()
		#~ self.loadXml()
		
	def loadTemplateFromBDD(self):
		query="SELECT star035_ship_star005,star035_name FROM star035_npc_template WHERE star035_id='"+ str(self.template)+"'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.ship=Ship(0,int(row[0]))
			self.name=row[1]
		cursor.close()
		
	def loadShipFromBDD(self):
		query="SELECT star007_id FROM star007_ship ship JOIN  star006_item item ON item.star006_id=ship.star007_item_star006 WHERE star007_fitted=1 and  star006_container_starnnn='" + str(self.id) + "' AND star006_containertype='star034_npc'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.ship=Ship(int(row[0]))
			#~ self.ship.setZone(self.zone)
		cursor.close()
		if self.ship!=None:
			self.ship.setOwner(self)
			
	def saveToBDD(self):
		if self.id==0:
			query="insert into star034_npc (star034_zone_star011zone,star034_name,star034_template_star035,star034_event_star047)"
			query+=" values ('"+ str(self.zone.id) + "','"+self.name+"','" + str(self.template) + "','"+str(self.idEvent)+"')"
		
			instanceDbConnector=shimDbConnector.getInstance()
			cursor=instanceDbConnector.getConnection().cursor()
			cursor.execute(query)
			if self.id==0:
				self.id=cursor.lastrowid
			cursor.close()
		
		self.ship.setOwner(self)
		self.ship.saveToBDD()
		self.saveToXml()
		shimDbConnector.getInstance().commit()
		
		
	def loadXml(self):
		if os.path.exists("./config/npc/npc" + str(self.id) + ".xml")==True:
			dom = xml.dom.minidom.parse("./config/npc/npc" + str(self.id) + ".xml")
			pp=dom.getElementsByTagName('patrolpoint')
			beh=self.attitude.setBehavior(C_BEHAVIOR_PATROL)
			for p in pp:
				pos=p.firstChild.data
				tabpos=pos.split(",")
				beh.addPatrolPoint(Vec3(float(tabpos[0]),float(tabpos[1]),float(tabpos[2])))
			#~ self.faction=int(dom.getElementsByTagName('faction')[0].firstChild.data)
			atti=dom.getElementsByTagName('attitude')
			for a in atti:
				typeAtti=int(a.getElementsByTagName('typeattitude')[0].firstChild.data)
				lvlAtti=int(a.getElementsByTagName('levelattitude')[0].firstChild.data)
				self.attitude.addAttitude(typeAtti,lvlAtti)
	
	def saveToXml(self):
		docXml = xml.dom.minidom.Document()
		npcXml=docXml.createElement("npc")
		idXml=docXml.createElement("id")
		idXml.appendChild(docXml.createTextNode(str(self.id)))
		
		for a in self.attitude.getAttitude():
			attitudeXml=docXml.createElement("attitude")
			typeAttiXml=docXml.createElement("typeattitude")
			typeAttiXml.appendChild(docXml.createTextNode(str(a)))
			lvlAttiXml=docXml.createElement("levelattitude")
			lvlAttiXml.appendChild(docXml.createTextNode(str(self.attitude.getAttitude()[a])))
			factionXml=docXml.createElement("faction")
			factionXml.appendChild(docXml.createTextNode(str(self.faction)))
			attitudeXml.appendChild(typeAttiXml)
			attitudeXml.appendChild(lvlAttiXml)
			attitudeXml.appendChild(factionXml)
			npcXml.appendChild(attitudeXml)
		
		behaviors=self.attitude.getBehaviors()
		for bId in behaviors:
			b=behaviors[bId]
			if isinstance(b,behaviorPatrol)==True:
				patrolsXml=docXml.createElement("patrol")
				pp=b.getPatrolPoints()
				for p in pp:
					patrolXml=docXml.createElement("patrolpoint")
					patrolXml.appendChild(docXml.createTextNode(str(p.getPos().getX()) +"," + str(p.getPos().getY()) +"," + str(p.getPos().getZ())))
					patrolsXml.appendChild(patrolXml)
				npcXml.appendChild(patrolsXml)
		npcXml.appendChild(idXml)
		docXml.appendChild(npcXml)
		fileHandle = open ( "./config/npc/npc" + str(self.id) + ".xml", 'w' ) 
		fileHandle.write(docXml.toxml())
		fileHandle.close()
		
		
	@staticmethod
	def getNPC(id):
		#~ print str(npc.listOfNpc.keys()) + " searching for " + str(id)
		if npc.listOfNpc.has_key(id)==True:
			return npc.listOfNpc[id]
		else:
			return None