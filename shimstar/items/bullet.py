from pandac.PandaModules import Point3,Vec3,Vec4
from pandac.PandaModules import *
from panda3d.bullet import *
from math import sqrt

class Bullet:
	nbBullet=0
	listOfBullet={}
	def __init__(self,pos,quat,egg,range,speed,weapon):
		#~ print "bullet::__init__"
		self.id=Bullet.nbBullet
		Bullet.nbBullet+=1
		self.weapon=weapon
		self.range=range
		self.speed=speed
		world,worldNP=self.weapon.getShip().getWorld()
		visNP = loader.loadModel("models/" + egg)
		geom = visNP.findAllMatches('**/+GeomNode').getPath(0).node().getGeom(0)			
		shape=BulletConvexHullShape()
		shape.addGeom(geom)
		body = BulletRigidBodyNode("bullet" + str(self.id))
		self.bodyNP = worldNP.attachNewNode(body)
		self.bodyNP.node().addShape(shape)
		self.bodyNP.node().setMass(0.0001)
		self.bodyNP.setQuat(quat)
		self.bodyNP.setPos(weapon.ship.bodyNP,Vec3(0,200,0))
		self.initPos=self.bodyNP.getPos()
		self.bodyNP.setCollideMask(BitMask32.allOn())
		self.bodyNP.setPythonTag("obj",self)
		self.bodyNP.setPythonTag("pnode",visNP)
		world.attachRigidBody(self.bodyNP.node())
		visNP.reparentTo(self.bodyNP)
		forwardVec=self.bodyNP.getQuat().getForward()
		self.bodyNP.node().setLinearVelocity(Vec3(forwardVec.getX()*self.speed,forwardVec.getY()*self.speed,forwardVec.getZ()*self.speed))
		Bullet.listOfBullet[self.id]=self
		
	@staticmethod
	def getBullet(id):
		"""
			Static :: retrieve a bullet by its id from all current bullets
		"""
		if Bullet.listOfBullet.has_key(id)==True:
			return Bullet.listOfBullet[id]
		else:
			return None
			
	@staticmethod
	def getBullets():
		"""
			static :: get list of all bullets existing
		"""
		if bullet.listOfBullet.has_key('titi'):
			bullet.listOfBullet.clear()
		return  bullet.listOfBullet
		
	def getId(self):
		return self.id
	
	def getClassName(self):
		return bullet.className
			
	def getShipOwner(self):
		return self.weapon.ship.name
			
	def getWeapon(self):
		return self.weapon
		
	def getDamage(self):
		return self.weapon.getDamage()

	def getPos(self):
		return self.bodyNP.getPos()
	
	def getQuat(self):
		return Quat(self.bodyNP.getQuat())
		
	def getHpr(self):
		return self.bodyNP.getHpr()
		
	def destroy(self):
		del bullet.listOfBullet[self.name]

	def stateBullet(self,time):
		"""
		determines if a bullet is at end of life or not
		return 1, if the bullet must be destroyed, 0 otherwise
		"""
		distance=self.calcDistance()
		if distance>self.range:
		#~ if (time-self.startTime)>self.range:
			return 1
		return 0
		
	def getName(self):
		return self.name
		
	def calcDistance(self):
		pos1=self.initPos
		pos2=self.bodyNP.getPos()
		dx=pos1.getX()-pos2.getX()
		dy=pos1.getY()-pos2.getY()
		dz=pos1.getZ()-pos2.getZ()
		distance=int(round(sqrt(dx*dx+dy*dy+dz*dz),0))
		return distance
    