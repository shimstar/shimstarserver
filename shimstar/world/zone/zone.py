from direct.stdpy import threading
from panda3d.bullet import*

from shimstar.user.user import *
from shimstar.core.constantes import *
from shimstar.bdd.dbconnector import *

class Zone(threading.Thread):
	instance=None
	def __init__(self,id):
		threading.Thread.__init__(self)
		self.stopThread=False
		self.id=id
		self.users=[]
		#~ self.name="zoneThread"
		self.loadZoneFromBdd()
		
		self.world = BulletWorld()
		self.world.setGravity(Vec3(0, 0, 0))
		self.worldNP = render.attachNewNode(self.name)
		
		
	def run(self):
		while not self.stopThread:
			pass
			
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