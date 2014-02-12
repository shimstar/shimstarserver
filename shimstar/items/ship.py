from pandac.PandaModules import *
from panda3d.bullet import *

from shimstar.zoneserver.network.netmessage import *
from shimstar.zoneserver.network.networkzonetcpserver import *
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
		self.engine=None
		self.owner=None
		self.torque=0
		self.frictionAngular=0
		self.frictionVelocity=0
		self.weapon=None
		self.lastSentTicks=0
		self.state=0
		self.maxhullpoints=0
		self.hullpoints=0
		self.egg=None
		self.world=None
		self.worldNP=None
		self.poussee=0
		self.name=""
		self.damageHistory={}
		self.pyr={'p':0,'y':0,'r':0,'a':0,'w':0}
		self.bodyNP=None
		if self.id!=0:
			self.loadFromBDD()
		elif self.template!=0:
			self.loadFromTemplate()
			
		print "ship::__init__" + str(self.id)
			
	def getTemplate(self):
		return self.template
		
	def getState(self):
		return self.state
		
	def destroy(self):
		if self.bodyNP!=None:
			self.bodyNP.detachNode()
			self.bodyNP.removeNode()
		
	def getWorld(self):
		return self.world,self.worldNP
		
	def shot(self):
		if self.worldNP==None:
			return None
		else:
			if self.weapon!=None:
				bul= self.weapon.shot(self.bodyNP.getPos(),self.bodyNP.getQuat(),self)
				#~ print "ship::shot" + str(bul)
				if bul!=None:
					nm=netMessage(C_NETWORK_NEW_NPC_SHOT,None)
					nm.addInt(self.owner.id)
					nm.addInt(bul.getId())
					nm.addFloat(bul.getPos().getX())
					nm.addFloat(bul.getPos().getY())
					nm.addFloat(bul.getPos().getZ())
					nm.addFloat(bul.getQuat().getR())
					nm.addFloat(bul.getQuat().getI())
					nm.addFloat(bul.getQuat().getJ())
					nm.addFloat(bul.getQuat().getK())
					NetworkMessage.getInstance().addMessageForAllUsers(nm)
				return bul
				
		return None
		
	def sendInfo(self,nm):
		#~ print "ship::sendInfo " + str(self.template)
		nm.addInt(self.id)
		nm.addInt(self.template)
		nm.addInt(len(self.itemInInventory))
		if len(self.itemInInventory)>0:
			for i in self.itemInInventory:
				nm.addInt(i.getTypeItem())
				nm.addInt(i.getTemplate())
				nm.addInt(i.getId())
		
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
		if self.bodyNP!=None and self.bodyNP.isEmpty()==False:
			return self.bodyNP.getPos()
		else:
			return None
			
	def getQuat(self):
		if self.bodyNP!=None and self.bodyNP.isEmpty()==False:
			return self.bodyNP.getQuat()
		else:
			return None
		
	def modifyPYR(self,key,value):
		"""
			save in self.pyr, the keypressed by a player in the aim to use it in movement.
		"""
		if key=='d':
			self.pyr['p']=-int(value)
		elif key=='z':
			self.pyr['y']=-int(value)
		elif key=='s':
			self.pyr['y']=int(value)
		elif key=='q':
			self.pyr['p']=int(value)
		elif key=='a':
			self.pyr['a']=int(value)
		elif key=='w':
			self.pyr['w']=int(value)
			
	def getHullPoints(self):
		return self.hullpoints
		
	def takeDamage(self,hp,who=None,character=False):
		"""
			params : 
					hp : number of hitpoints received
					who : who has fired
			remove hitpoints from ship and save in the damageHistory
			
		"""
		#~ print "ship::takedamage"
		self.hullpoints-=hp
		
		if who!=None:
			if character==True:
				if self.damageHistory.has_key(who.getId())==True:
					self.damageHistory[who.getId()]+=hp
				else:
					self.damageHistory[who.getId()]=hp
					
	def loadFromTemplate(self):
		"""
			Load a ship from a template (the id of the template is given in the constructor)
		"""
		instanceDbConnector=shimDbConnector.getInstance()
		query="SELECT star005_egg,star005_hull,star005_mass,star005_maniability,star005_img,star005_item_star004 "
		query+=", star004_name"
		query+=" FROM STAR005_SHIP_TEMPLATE join star004_item_template on star005_item_star004=star004_id"
		query+=" WHERE STAR005_id ='" + str(self.template) + "'"
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.maniability=int(row[3])
			self.maxhullpoints=int(row[1])
			self.egg=row[0]
			self.fitted=1
			self.mass=float(row[2])
			self.img=row[4]
			self.type=self.template
			self.hullpoints=int(row[1])
			self.itemTemplate=int(row[5])
			self.name=str(row[6])
		cursor.close()
		
		cursor=instanceDbConnector.getConnection().cursor()
		query="SELECT star009_id FROM star009_slot WHERE star009_ship_star005='" + str(self.template) + "'"
		cursor.execute(query)
		result_set = cursor.fetchall ()
		self.slots=[]
		for row in result_set:
			tempSlot=Slot(0,row[0])
			self.slots.append(tempSlot)
			if tempSlot.getItem()!=None and tempSlot.getItem().getTypeItem()==C_ITEM_ENGINE:
				self.engine=tempSlot.getItem()
			if tempSlot.getItem()!=None and tempSlot.getItem().getTypeItem()==C_ITEM_WEAPON:
				self.weapon=tempSlot.getItem()
			
		cursor.close()
		
	def loadFromBDD(self):
		query="SELECT star007_fitted,star005_egg,star005_hull,star005_mass,star005_torque,star005_img,star007_template_star005shiptemplate,star007_hull "
		query+=" ,star007_posx,star007_posy,star007_posz,star005_friction_angular,star005_friction_velocity"
		query+=",star004_name"
		query+=" FROM star007_ship ship JOIN star005_ship_template shiptemplate ON ship.star007_template_star005shiptemplate = shiptemplate.star005_id  "
		query+=" join star004_item_template on star005_item_star004=star004_id "
		query+="where star007_id ='" + str(self.id) + "'"
		#~ print "ship::LoadFromBdd "
		#~ print query
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.torque=int(row[4])
			self.maxhullpoints=int(row[2])
			self.egg=row[1]
			self.fitted=int(row[0])
			self.mass=float(row[3])
			self.img=row[5]
			self.type=int(row[6])
			self.hullpoints=int(row[7])
			self.pos=Vec3(float(row[8]),float(row[9]),float(row[10]))
			self.frictionAngular=float(row[11])
			self.frictionVelocity=float(row[12])
			self.name=str(row[13])
			self.template=int(row[6])
			
		cursor.close()
		
		cursor=instanceDbConnector.getConnection().cursor()
		query="SELECT star009_id FROM star009_slot WHERE star009_ship_star007='" + str(self.id) + "'"
		cursor.execute(query)
		#~ print query
		result_set = cursor.fetchall ()
		for row in result_set:
			tempSlot=Slot(row[0])
			self.slots.append(tempSlot)

			if tempSlot.getItem()!=None and isinstance(tempSlot.getItem(),Engine):
				self.engine=tempSlot.getItem()
			if tempSlot.getItem()!=None and isinstance(tempSlot.getItem(),Weapon):
				self.weapon=tempSlot.getItem()
				self.weapon.setShip(self)
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
		
	def runPhysics(self):
		"""
			on each step, add torque and forces to ship node.
			It uses the self.pyr saved keypressed
		"""
		#~ print "SHip::runPhysics " + str(self.id) + " " + str(self.engine)
		if self.bodyNP!=None and self.bodyNP.isEmpty()==False:			
			if self.worldNP!=None:
				self.bodyNP.node().setActive(True)		
				forwardVec=self.bodyNP.getQuat().getForward()
				v=Vec3(self.pyr['y']*self.torque,0.0,self.pyr['p']*self.torque)
				v= self.worldNP.getRelativeVector(self.bodyNP,v) 
				self.bodyNP.node().applyTorque(v)
				
				if self.engine!=None:
					if self.pyr['a']==1:
						if self.poussee<self.engine.getSpeedMax():
							self.poussee+=self.engine.getAcceleration()
					if self.pyr['w']==1:
						if self.poussee>0:
							self.poussee-=self.engine.getAcceleration()
							
				self.bodyNP.node().applyCentralForce(Vec3(forwardVec.getX()*self.poussee,forwardVec.getY()*self.poussee,forwardVec.getZ()*self.poussee))

				self.bodyNP.node().setLinearVelocity((self.bodyNP.node().getLinearVelocity().getX()*self.frictionVelocity,self.bodyNP.node().getLinearVelocity().getY()*self.frictionVelocity,self.bodyNP.node().getLinearVelocity().getZ()*self.frictionVelocity))
				self.bodyNP.node().setAngularVelocity((self.bodyNP.node().getAngularVelocity().getX()*self.frictionAngular,self.bodyNP.node().getAngularVelocity().getY()*self.frictionAngular,self.bodyNP.node().getAngularVelocity().getZ()*self.frictionAngular))
	
	def saveToBDD(self):
		instanceDbConnector=shimDbConnector.getInstance()
		if self.id>0:
			query="UPDATE STAR007_SHIP SET star007_hull='" + str(self.hullpoints) + "'"
			if self.bodyNP!=None and self.bodyNP.isEmpty()==False:
				query+=",star007_posx='" + str(self.bodyNP.getPos().getX()) + "'"
				query+=",star007_posy='" + str(self.bodyNP.getPos().getY()) + "'"
				query+=",star007_posZ='" + str(self.bodyNP.getPos().getZ()) + "'"
			query+=" WHERE star007_id='" + str(self.id) + "'"
			cursor=instanceDbConnector.getConnection().cursor()
			cursor.execute(query)
			cursor.close()
		elif self.id==0:
			query="INSERT INTO STAR006_ITEM (star006_template_star004,star006_container_starnnn,star006_containertype,star006_owner_star001,star006_location)"
			query+=" values  ('" + str(self.template) + "','" + str(self.owner.id) + "',"
			if self.owner.getClassName()=='character':
				query+="'star002_character'"
			elif self.owner.getClassName()=='NPC':
				query+="'star034_npc'"
			query+=",0,0)"
			#~ print query
			cursor=instanceDbConnector.getConnection().cursor()
			cursor.execute(query)
			self.itemId=int(cursor.lastrowid)
			cursor.close()
			query="INSERT INTO STAR007_ship (star007_item_star006,star007_fitted,star007_template_star005shiptemplate,star007_hull) "
			query+=" values ('"+str(self.itemId)+"','1','"+str(self.template)+"','"+str(self.hullpoints)+"')"
			cursor=instanceDbConnector.getConnection().cursor()
			cursor.execute(query)
			self.id=int(cursor.lastrowid)
			cursor.close()

		for it in self.itemInInventory:
			if it.getId()>0:
				#~ if it.getTypeItem()==C_ITEM_MINERAL:
					#~ query="UPDATE STAR006_ITEM SET STAR006_location = '" + str(it.getLocation()) + "', star006_containertype='star007_ship', star006_container_starnnn='" + str(self.id) +"'"
					#~ query+=" ,star006_nb='" + str(it.getNb()) + "'"
					#~ query+=" WHERE star006_id='" + str(it.getId()) + "'"
				#~ else:
				query="UPDATE STAR006_ITEM SET STAR006_location = '" + str(it.getLocation()) + "', star006_containertype='star007_ship', star006_container_starnnn='" + str(self.id) +"'"
				query+=" WHERE star006_id='" + str(it.getId()) + "'"
				cursor=instanceDbConnector.getConnection().cursor()
				cursor.execute(query)
				cursor.close()
				
		for sl in self.slots:
			sl.setShip(self.id)
			sl.saveToBDD()
		
		instanceDbConnector.commit()
		
	def loadEgg(self,world,worldNP):
		"""
		don't create the node, geom and physics at connection start, but in the incoming of a zone.
		It is why it is a loadEgg, and it is not load in loadXml
		"""
		self.world=world
		self.worldNP=worldNP
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
		
	def getWeapon(self):
		return self.weapon