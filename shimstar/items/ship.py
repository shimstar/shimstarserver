from pandac.PandaModules import *
from panda3d.bullet import *

from shimstar.items.item import *
from shimstar.items.engine import *
from shimstar.items.weapon import *
from shimstar.items.slot import *
from shimstar.core.constantes import *

class Ship(ShimItem):
	className="ship"
	def __init__(self,id=0,template=0):
		super(Ship,self).__init__(id,template)	
		self.pos=Point3(0,0,0)
		self.hpr=Point3(0,0,0)
		self.slots=[]
		self.itemInInventory=[]
		self.loadShipFromBDD()
		self.lastSentTicks=0
		self.state=0
		self.bodyNP=None
		
	def getState(self):
		return self.state
		
	def getXml(self,docXml=None):
		if docXml==None:
			docXml = xml.dom.minidom.Document()
		shipXml=docXml.createElement("ship")
		idXml=docXml.createElement("idship")
		idXml.appendChild(docXml.createTextNode(str(self.id)))
		nameXml=docXml.createElement("name")
		nameXml.appendChild(docXml.createTextNode(str(self.name)))
		maniabilityXml=docXml.createElement("maniability")
		maniabilityXml.appendChild(docXml.createTextNode(str(self.maniability)))
		hullpointsXml=docXml.createElement("hullpoints")
		hullpointsXml.appendChild(docXml.createTextNode(str(self.hullpoints)))
		maxhullpointsXml=docXml.createElement("maxhullpoints")
		maxhullpointsXml.appendChild(docXml.createTextNode(str(self.maxhullpoints)))
		eggXml=docXml.createElement("egg")
		eggXml.appendChild(docXml.createTextNode(self.egg))
		imgXml=docXml.createElement("img")
		imgXml.appendChild(docXml.createTextNode(self.img))
		shipXml.appendChild(idXml)
		shipXml.appendChild(nameXml)
		shipXml.appendChild(maniabilityXml)
		shipXml.appendChild(maxhullpointsXml)
		shipXml.appendChild(hullpointsXml)
		shipXml.appendChild(eggXml)
		shipXml.appendChild(imgXml)
		if len(self.slots)>0:
			slotsXml=docXml.createElement("slots")
			for s in self.slots:
				slotXml=s.getXml(docXml)
				slotsXml.appendChild(slotXml)
			shipXml.appendChild(slotsXml)
			
		if len(self.itemInInventory)>0:
			invXml=docXml.createElement("inventory")
			for i in self.itemInInventory:
				itemXml=docXml.createElement("item")
				idXml=docXml.createElement("iditem")
				idXml.appendChild(docXml.createTextNode(str(i.getId())))
				typeitemXml=docXml.createElement("typeitem")
				typeitemXml.appendChild(docXml.createTextNode(str(i.getTypeItem())))
				templateXml=docXml.createElement("template")
				templateXml.appendChild(docXml.createTextNode(str(i.getTemplate())))
				if i.getTypeItem()==C_ITEM_MINERAL:
					qtyXml=docXml.createElement("quantity")
					qtyXml.appendChild(docXml.createTextNode(str(i.getNb())))
					itemXml.appendChild(qtyXml)
				itemXml.appendChild(idXml)
				itemXml.appendChild(typeitemXml)
				itemXml.appendChild(templateXml)
				invXml.appendChild(itemXml)
			shipXml.appendChild(invXml)
		return shipXml
		
	def mustSentPos(self,timer):
		"""
		 if the time elapsed between 2 messages sent to others players is over the sendticks, return true, otherwise return false
		"""
		dt=(timer-self.lastSentTicks)
		if  dt > C_SENDTICKS:
			self.lastSentTicks=timer
			return True
		else:
			return False
		
	def getNode(self):
		return self.bodyNP
		
	def getPos(self):
		return self.bodyNP.getPos()
		
	def loadShipFromBDD(self):
		query="SELECT star007_fitted,star005_egg,star005_hull,star005_mass,star005_maniability,star005_img,star007_template_star005shiptemplate,star007_hull "
		query+=" ,star007_posx,star007_posy,star007_posz "
		query+=" FROM star007_ship ship JOIN star005_ship_template shiptemplate ON ship.star007_template_star005shiptemplate = shiptemplate.star005_id  where star007_id ='" + str(self.id) + "'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.maniability=int(row[4])
			self.maxhullpoints=int(row[2])
			self.egg=row[1]
			self.fitted=int(row[0])
			self.mass=float(row[3])
			self.img=row[5]
			self.type=int(row[6])
			self.hullpoints=int(row[7])
			self.pos=Vec3(float(row[8]),float(row[9]),float(row[10]))
			
		cursor.close()
		
		cursor=instanceDbConnector.getConnection().cursor()
		query="SELECT star009_id FROM star009_slot WHERE star009_ship_star007='" + str(self.id) + "'"
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			tempSlot=Slot(row[0])
			self.slots.append(tempSlot)
			if tempSlot.getItem()!=None and tempSlot.getItem().getTypeItem()==C_ITEM_ENGINE:
				self.engine=tempSlot.getItem()
			if tempSlot.getItem()!=None and tempSlot.getItem().getTypeItem()==C_ITEM_WEAPON:
				self.weapon=tempSlot.getItem()
		cursor.close()
		
		cursor=instanceDbConnector.getConnection().cursor()
		query="SELECT star004_type_star003,star006_id FROM star006_item item JOIN star004_item_template itemTemplate ON item.star006_template_star004 = itemTemplate.star004_id WHERE star006_containertype ='star007_ship' and star006_container_starnnn='" + str(self.id) + "'"
		
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			typeItem=row[0]
			if typeItem==C_ITEM_ENGINE:
				itemTemp=Engine(int(row[1]))
			elif typeItem==C_ITEM_WEAPON:
				itemTemp=Weapon(int(row[1]),self)
			else:
				itemTemp=ShimItem(int(row[1]))
			self.itemInInventory.append(itemTemp)
		cursor.close()
		
	def loadEgg(self,world,worldNP):
		"""
		don't create the node, geom and physics at connection start, but in the incoming of a zone.
		It is why it is a loadEgg, and it is not load in loadXml
		"""

		visNP = loader.loadModel(self.egg)
		geom = visNP.findAllMatches('**/+GeomNode').getPath(0).node().getGeom(0)			
		shape=BulletConvexHullShape()
		shape.addGeom(geom)
		body = BulletRigidBodyNode(self.name)
		self.bodyNP = worldNP.attachNewNode(body)
		self.bodyNP.node().addShape(shape)
		self.bodyNP.node().setMass(1.0)
		self.bodyNP.setPos(self.pos)
		self.bodyNP.setHpr(self.hpr)
		self.bodyNP.setCollideMask(BitMask32.allOn())
		self.bodyNP.setPythonTag("obj",self)
		self.bodyNP.setPythonTag("pnode",visNP)
		world.attachRigidBody(self.bodyNP.node())

		visNP.reparentTo(self.bodyNP)
		self.state=1