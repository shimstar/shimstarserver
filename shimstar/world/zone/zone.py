from direct.stdpy import threading
from panda3d.bullet import*

from shimstar.zoneserver.network.netmessageudp import *
from shimstar.zoneserver.network.networkmessageudp import *
from shimstar.zoneserver.network.netmessage import *
from shimstar.zoneserver.network.networkzonetcpserver import *
from shimstar.zoneserver.network.networkzoneudpserver import *
from shimstar.core.constantes import *
from shimstar.user.user import *
from shimstar.core.constantes import *
from shimstar.bdd.dbconnector import *
from shimstar.world.zone.asteroid import *
from shimstar.world.zone.station import *
from shimstar.npc.npc import *

C_STEP_SIZE=1.0/60.0

class Zone(threading.Thread):
	instance=None
	def __init__(self,id):
		threading.Thread.__init__(self)
		self.stopThread=False
		self.id=id
		self.listOfAsteroid=[]
		self.listOfStation=[]
		self.npc=[]
		self.lastGlobalTicks=0
		self.lastNpcSendTicks=0
		self.world = BulletWorld()
		self.world.setGravity(Vec3(0, 0, 0))
		self.worldNP = render.attachNewNode(self.name)
		
		self.loadZoneFromBdd()
		
	def runNewUser(self):
		tempMsg=NetworkTCPServer.getInstance().getListOfMessageById(C_NETWORK_ASKING_NPC)
		if len(tempMsg)>0:
			for msg in tempMsg:
				netMsg=msg.getMessage()
				usrId=int(netMsg[0])
				usr=User.getUserById(usrId)
				if usr!=None:
					for temp in self.npc:
						nm=netMessage(C_NETWORK_NPC_INCOMING,usr.getConnexion())
						temp.sendInfo(nm)
						NetworkMessage.getInstance().addMessage(nm)
					nm=netMessage(C_NETWORK_NPC_SENT,usr.getConnexion())
					NetworkMessage.getInstance().addMessage(nm)
				NetworkTCPServer.getInstance().removeMessage(msg)
				
		tempMsg=NetworkTCPServer.getInstance().getListOfMessageById(C_NETWORK_ASKING_CHAR)
		if len(tempMsg)>0:
			for msg in tempMsg:
				netMsg=msg.getMessage()
				usrId=int(netMsg[0])
				usr=User.getUserById(usrId)
				#~ print "runnewUser::C_NETWORK_ASKING_CHAR " + str(usr)
				if usr!=None:
					nm=netMessage(C_NETWORK_CURRENT_CHAR_INFO,usr.getConnexion())
					usr.sendInfoChar(nm)
					NetworkMessage.getInstance().addMessage(nm)
					
					for othrUsr in User.listOfUser:
						if othrUsr!=usrId:
							nm=netMessage(C_NETWORK_CHAR_INCOMING,usr.getConnexion())
							User.listOfUser[othrUsr].sendInfoOtherPlayer(nm)
							NetworkMessage.getInstance().addMessage(nm)
							nm=netMessage(C_NETWORK_CHAR_INCOMING,User.listOfUser[othrUsr].getConnexion())
							usr.sendInfoOtherPlayer(nm)
							NetworkMessage.getInstance().addMessage(nm)
						
				NetworkTCPServer.getInstance().removeMessage(msg)
				
		
	def run(self):
		while not self.stopThread:
			User.lock.acquire()
			#~ print User.listOfUser
			for usr in User.listOfUser:
				usrObj=User.listOfUser[usr]
				chr=usrObj.getCurrentCharacter()
				if chr!=None:
					if chr.ship!=None and chr.ship.getNode()==None and chr.ship.getState()==0:
						chr.ship.loadEgg(self.world,self.worldNP)

					if chr.ship!=None and chr.ship.getNode()!=None and chr.ship.getNode().isEmpty()==False:
						if chr.ship.mustSentPos(globalClock.getRealTime())==True:
							for u in User.listOfUser:
								usrToSend=User.listOfUser[u]
								nm=netMessageUDP(C_NETWORK_CHARACTER_UPDATE_POS,usrToSend.getIp(),usrToSend.getUdpPort())
								nm.addInt(usrObj.getId())
								nm.addInt(chr.getId())
								nm.addFloat(chr.ship.bodyNP.getQuat().getR())
								nm.addFloat(chr.ship.bodyNP.getQuat().getI())
								nm.addFloat(chr.ship.bodyNP.getQuat().getJ())
								nm.addFloat(chr.ship.bodyNP.getQuat().getK())
								nm.addFloat(chr.ship.getPos().getX())
								nm.addFloat(chr.ship.getPos().getY())
								nm.addFloat(chr.ship.getPos().getZ())
								NetworkMessageUdp.getInstance().addMessage(nm)
			
			if globalClock.getRealTime()-self.lastNpcSendTicks>C_SENDTICKS:
				self.lastNpcSendTicks=globalClock.getRealTime()
				for u in User.listOfUser:
					if len(self.npc)>0:
						nm=netMessageUDP(C_NETWORK_NPC_UPDATE_POS,User.listOfUser[u].getIp(),User.listOfUser[u].getUdpPort())
						nm.addInt(len(self.npc))
						for n in self.npc:							
							nm.addInt(n.getId())
							nm.addFloat(n.ship.bodyNP.getQuat().getR())
							nm.addFloat(n.ship.bodyNP.getQuat().getI())
							nm.addFloat(n.ship.bodyNP.getQuat().getJ())
							nm.addFloat(n.ship.bodyNP.getQuat().getK())
							nm.addFloat(n.ship.getPos().getX())
							nm.addFloat(n.ship.getPos().getY())
							nm.addFloat(n.ship.getPos().getZ())
						NetworkMessageUdp.getInstance().addMessage(nm)
						
			User.lock.release()
			self.runPhysics()
			
			self.runUpdateCharShot()
			self.runBulletCollision()
			self.runNewUser()
		print "thread zone is ending"
				
	def runBulletCollision(self):
		Bullet.lock.acquire()
		bulletToRemove=[]
		for b in Bullet.listOfBullet:
			if Bullet.listOfBullet[b].stateBullet()==1:
				bulletToRemove.append(b)
				
			result = self.world.contactTest(Bullet.listOfBullet[b].bodyNP.node())
			for contact in result.getContacts():
				node1=contact.getNode1()
				objCollided=contact.getNode1().getPythonTag("obj")
				#~ print objCollided
				if isinstance(objCollided,Station)==True:
					for u in User.listOfUser:
						nm=netMessage(C_NETWORK_EXPLOSION,User.listOfUser[u].getConnexion())
						pos=Bullet.listOfBullet[b].getPos()
						nm.addFloat(pos.getX())
						nm.addFloat(pos.getY())
						nm.addFloat(pos.getZ())
						NetworkMessage.getInstance().addMessage(nm)
					bulletToRemove.append(b)
				elif isinstance(objCollided,Asteroid)==True:
					for u in User.listOfUser:
						nm=netMessage(C_NETWORK_EXPLOSION,User.listOfUser[u].getConnexion())
						pos=Bullet.listOfBullet[b].getPos()
						nm.addFloat(pos.getX())
						nm.addFloat(pos.getY())
						nm.addFloat(pos.getZ())
						NetworkMessage.getInstance().addMessage(nm)
					bulletToRemove.append(b)
				elif isinstance(objCollided,Ship)==True:
					objCollided.takeDamage(Bullet.listOfBullet[b].getDamage(),Bullet.listOfBullet[b].getShipOwner(),isinstance(objCollided.getOwner(),Character))
					User.lock.acquire()
					for u in User.listOfUser:
						if isinstance(objCollided.getOwner(),Character)==True:
							nm=netMessage(C_NETWORK_TAKE_DAMAGE_NPC,User.listOfUser[u].getConnexion())
						else:
							nm=netMessage(C_NETWORK_TAKE_DAMAGE_CHAR,User.listOfUser[u].getConnexion())
						nm.addInt(objCollided.getOwner().getId())
						nm.addInt(Bullet.listOfBullet[b].getDamage())
						NetworkMessage.getInstance().addMessage(nm)
					User.lock.release()
					if objCollided.getHullPoints()==0:
						User.lock.acquire()
						for u in User.listOfUser:
							if isinstance(objCollided.getOwner(),Character)==True:
								nm=netMessage(C_NETWORK_REMOVE_NPC,User.listOfUser[u].getConnexion())
							else:
								nm=netMessage(C_NETWORK_REMOVE_CHAR,User.listOfUser[u].getConnexion())
							nm.addInt(objCollided.getOwner().getId())
							NetworkMessage.getInstance().addMessage(nm)
						User.lock.release()
					User.lock.acquire()
					for u in User.listOfUser:
						nm=netMessage(C_NETWORK_REMOVE_SHOT,User.listOfUser[u].getConnexion())
						nm.addInt(Bullet.listOfBullet[b].getId())
						NetworkMessage.getInstance().addMessage(nm)
						nm=netMessage(C_NETWORK_EXPLOSION,User.listOfUser[u].getConnexion())
						pos=Bullet.listOfBullet[b].getPos()
						nm.addFloat(pos.getX())
						nm.addFloat(pos.getY())
						nm.addFloat(pos.getZ())
						NetworkMessage.getInstance().addMessage(nm)
					User.lock.release()
					bulletToRemove.append(b)
		
		
					
		for b in bulletToRemove:
			User.lock.acquire()
			for u in User.listOfUser:
				if Bullet.listOfBullet.has_key(b):
					nm=netMessage(C_NETWORK_REMOVE_SHOT,User.listOfUser[u].getConnexion())
					nm.addInt(Bullet.listOfBullet[b].getId())
					NetworkMessage.getInstance().addMessage(nm)
					Bullet.removeBullet(b)
			User.lock.release()
		Bullet.lock.release()
		
	def runUpdateCharShot(self):
		tempMsg=NetworkZoneUDPServer.getInstance().getListOfMessageById(C_NETWORK_CHAR_SHOT)
		if len(tempMsg)>0:
			for msg in tempMsg:
				netMsg=msg.getMessage()
				usr=int(netMsg[0])
				charact=int(netMsg[1])
				pos=Point3(float(netMsg[2]),float(netMsg[3]),float(netMsg[4]))
				quat=(float(netMsg[5]),float(netMsg[6]),float(netMsg[7]),float(netMsg[8]))
				if User.listOfUser.has_key(usr):
					ch=User.listOfUser[usr].getCurrentCharacter()
					Bullet.lock.acquire()
					b=ch.getShip().getWeapon().addBullet(pos,quat)
					Bullet.lock.release()
					User.lock.acquire()
					for u in User.listOfUser:
						nm=netMessage(C_NETWORK_NEW_CHAR_SHOT,User.listOfUser[u].getConnexion())
						nm.addInt(usr)
						nm.addInt(b.getId())
						nm.addFloat(b.getPos().getX())
						nm.addFloat(b.getPos().getY())
						nm.addFloat(b.getPos().getZ())
						nm.addFloat(b.getQuat().getR())
						nm.addFloat(b.getQuat().getI())
						nm.addFloat(b.getQuat().getJ())
						nm.addFloat(b.getQuat().getK())
						NetworkMessage.getInstance().addMessage(nm)
					User.lock.release()
			NetworkZoneUDPServer.getInstance().removeMessage(msg)
		
	def runPhysics(self):
		"""
			run bullet Physics
		"""
		actualTime=globalClock.getRealTime()
		if self.lastGlobalTicks==0:
			self.lastGlobalTicks=actualTime
		dt=actualTime-self.lastGlobalTicks
		
		if dt>C_STEP_SIZE:
			self.lastGlobalTicks=actualTime	
			User.lock.acquire()
			for usr in User.listOfUser:
				if User.listOfUser[usr].getCurrentCharacter()!=None:
					User.listOfUser[usr].getCurrentCharacter().getShip().runPhysics()	
			User.lock.release()	
			for npc in self.npc:
				npc.runPhysics()
				
			self.world.doPhysics(dt,10)

	@staticmethod
	def getInstance(id):
		if Zone.instance==None:
			Zone.instance=Zone(id)
			
		return Zone.instance
		
		
	def loadZoneFromBdd(self):
		query="SELECT star011_name, star011_typezone_star012 FROM star011_zone WHERE star011_id ='" + str(self.id) + "'"
		instanceDbConnector=shimDbConnector.getInstance()

		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.zoneName=row[0]
			self.typeZone=row[1]
		cursor.close()
		
		self.loadZoneAsteroidFromBdd()
		self.loadZoneStationFromBdd()
		self.loadZoneNPCFromBDD()
		
	def loadZoneNPCFromBDD(self):
		#~ temp=NPC(0,1,self)
		#~ temp.saveToBDD()
		#~ temp=NPC(0,1,self)
		#~ temp.saveToBDD()
		query="SELECT star034_id FROM star034_npc WHERE star034_zone_star011zone ='" + str(self.id) + "'"
		instanceDbConnector=shimDbConnector.getInstance()
		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			temp=NPC(int(row[0]),0,self)
			
			self.npc.append(temp)
			temp.ship.loadEgg(self.world,self.worldNP)
			temp.loadXml()
		
	def loadZoneAsteroidFromBdd(self):
		query="SELECT star014_id FROM star014_asteroid WHERE star014_zone_star011 ='" + str(self.id) + "'"
		instanceDbConnector=shimDbConnector.getInstance()

		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			astLoaded=Asteroid(row[0],self.world,self.worldNP)
			self.listOfAsteroid.append(astLoaded)
		cursor.close()
		
	def loadZoneStationFromBdd(self):
		query="SELECT star022_zone_star011 FROM star022_station WHERE star022_inzone_star011 ='" + str(self.id) + "'"
		instanceDbConnector=shimDbConnector.getInstance()

		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			stationLoaded=Station(row[0],self.world,self.worldNP)
			self.listOfStation.append(stationLoaded)
		cursor.close()