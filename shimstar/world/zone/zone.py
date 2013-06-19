from direct.stdpy import threading
from panda3d.bullet import*

from shimstar.user.user import *
from shimstar.core.constantes import *
from shimstar.bdd.dbconnector import *
from shimstar.world.zone.asteroid import *
from shimstar.world.zone.station import *

class Zone(threading.Thread):
	instance=None
	def __init__(self,id):
		threading.Thread.__init__(self)
		self.stopThread=False
		self.id=id
		self.users=[]
		self.listOfAsteroid=[]
		self.listOfStation=[]
		self.world = BulletWorld()
		self.world.setGravity(Vec3(0, 0, 0))
		self.worldNP = render.attachNewNode(self.name)
		
		self.loadZoneFromBdd()
		
	def run(self):
		while not self.stopThread:
			for usr in User.listOfUser:
				chr=User.listOfUser[usr].getCurrentCharacter()
				if chr.ship!=None and chr.ship.getNode()==None and chr.ship.getState==0:
					chr.ship.loadEgg(self.world,self.worldNP)
				if chr.ship!=None and chr.ship.getNode()!=None and chr.ship.getNode().isEmpty()==False:
					if chr.ship.mustSentPos(globalClock.getRealTime())==True:
						for u in self.users:
							vitesse=chr.ship.getVitesse()
							nm=netMessage(C_UPDATE_POS_CHAR,u.getIP())
							nm.addInt(usr.getId())
							nm.addInt(chr.getId())
							nm.addFloat(chr.ship.bodyNP.getQuat().getR())
							nm.addFloat(chr.ship.bodyNP.getQuat().getI())
							nm.addFloat(chr.ship.bodyNP.getQuat().getJ())
							nm.addFloat(chr.ship.bodyNP.getQuat().getK())
							nm.addFloat(chr.ship.getPos().getX())
							nm.addFloat(chr.ship.getPos().getY())
							nm.addFloat(chr.ship.getPos().getZ())
							nm.addFloat(vitesse)
							networkmessageUdp.instance.addMessage2(nm)
			
		print "thread zone is ending"
			
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