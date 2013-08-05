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
		self.world = BulletWorld()
		self.world.setGravity(Vec3(0, 0, 0))
		self.worldNP = render.attachNewNode(self.name)
		
		self.loadZoneFromBdd()
		
	def newToZone(self,usr):
		for temp in self.npc:
			nm=netMessage(C_NETWORK_NPC_INCOMING,usr.getConnexion())
			nm.addString(temp.getXml().toxml())
			nm.addFloat(temp.getPos().getX())
			nm.addFloat(temp.getPos().getY())
			nm.addFloat(temp.getPos().getZ())
			nm.addFloat(temp.getQuat().getR())
			nm.addFloat(temp.getQuat().getI())
			nm.addFloat(temp.getQuat().getJ())
			nm.addFloat(temp.getQuat().getK())
			NetworkMessage.getInstance().addMessage(nm)
			usr.setNewToZone(False)
		
	def run(self):
		while not self.stopThread:
			User.lock.acquire()
			for usr in User.listOfUser:
				usrObj=User.listOfUser[usr]
				if usrObj.isNewToZone():
					self.newToZone(usrObj)
				chr=usrObj.getCurrentCharacter()
				if chr.ship!=None and chr.ship.getNode()==None and chr.ship.getState()==0:
					chr.ship.loadEgg(self.world,self.worldNP)
				if chr.ship!=None and chr.ship.getNode()!=None and chr.ship.getNode().isEmpty()==False:
					if chr.ship.mustSentPos(globalClock.getRealTime())==True:
						for u in User.listOfUser:
							usrToSend=User.listOfUser[u]
							nm=netMessageUDP(C_NETWORK_CHARACTER_UPDATE_POS,usrToSend.getIp())
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
			
			
			for n in self.npc:
				if n.ship.mustSentPos(globalClock.getRealTime())==True:
					for u in User.listOfUser:
						nm=netMessageUDP(C_NETWORK_NPC_UPDATE_POS,User.listOfUser[u].getIp())
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
		print "thread zone is ending"
		
		
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
					b=ch.getShip().getWeapon().addBullet(pos,quat)
					
					for u in User.listOfUser:
						nm=netMessageUDP(C_NETWORK_CHAR_SHOT,User.listOfUser[u].getIp())
						nm.addInt(b.getId())
						nm.addFloat(float(netMsg[2]))
						nm.addFloat(float(netMsg[3]))
						nm.addFloat(float(netMsg[4]))
						nm.addFloat(float(netMsg[5]))
						nm.addFloat(float(netMsg[6]))
						nm.addFloat(float(netMsg[7]))
						nm.addFloat(float(netMsg[8]))
						NetworkMessageUdp.getInstance().addMessage(nm)
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
			astLoaded=asteroid(row[0],self.world,self.worldNP)
			self.listOfAsteroid.append(astLoaded)
		cursor.close()
		
	def loadZoneStationFromBdd(self):
		query="SELECT star022_zone_star011 FROM star022_station WHERE star022_inzone_star011 ='" + str(self.id) + "'"
		instanceDbConnector=shimDbConnector.getInstance()

		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			stationLoaded=station(row[0],self.world,self.worldNP)
			self.listOfStation.append(stationLoaded)
		cursor.close()