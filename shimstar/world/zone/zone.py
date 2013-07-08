from direct.stdpy import threading
from panda3d.bullet import*

from shimstar.zoneserver.network.netmessageudp import *
from shimstar.zoneserver.network.networkmessageudp import *
from shimstar.core.constantes import *
from shimstar.user.user import *
from shimstar.core.constantes import *
from shimstar.bdd.dbconnector import *
from shimstar.world.zone.asteroid import *
from shimstar.world.zone.station import *

C_STEP_SIZE=1.0/60.0

class Zone(threading.Thread):
	instance=None
	def __init__(self,id):
		threading.Thread.__init__(self)
		self.stopThread=False
		self.id=id
		self.listOfAsteroid=[]
		self.listOfStation=[]
		self.lastGlobalTicks=0
		self.world = BulletWorld()
		self.world.setGravity(Vec3(0, 0, 0))
		self.worldNP = render.attachNewNode(self.name)
		
		self.loadZoneFromBdd()
		
	def run(self):
		while not self.stopThread:
			for usr in User.listOfUser:
				chr=User.listOfUser[usr].getCurrentCharacter()
				if chr.ship!=None and chr.ship.getNode()==None and chr.ship.getState()==0:
					chr.ship.loadEgg(self.world,self.worldNP)
				if chr.ship!=None and chr.ship.getNode()!=None and chr.ship.getNode().isEmpty()==False:
					if chr.ship.mustSentPos(globalClock.getRealTime())==True:
						for u in User.listOfUser:
							usrToSend=User.listOfUser[u]
							nm=netMessageUDP(C_NETWORK_CHARACTER_UPDATE_POS,usrToSend.getIp())
							nm.addInt(User.listOfUser[usr].getId())
							nm.addInt(chr.getId())
							nm.addFloat(chr.ship.bodyNP.getQuat().getR())
							nm.addFloat(chr.ship.bodyNP.getQuat().getI())
							nm.addFloat(chr.ship.bodyNP.getQuat().getJ())
							nm.addFloat(chr.ship.bodyNP.getQuat().getK())
							nm.addFloat(chr.ship.getPos().getX())
							nm.addFloat(chr.ship.getPos().getY())
							nm.addFloat(chr.ship.getPos().getZ())
							NetworkMessageUdp.getInstance().addMessage(nm)
			
			self.runPhysics()
		print "thread zone is ending"
		
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
			for usr in User.listOfUser:
				User.listOfUser[usr].getCurrentCharacter().getShip().runPhysics()	
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