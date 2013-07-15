from panda3d.bullet import *
from pandac.PandaModules import *
from shimstar.core.constantes import *
from math import sqrt

class behavior(object):
	def __init__(self,npc):
		self.npc=npc
		self.ship=npc.ship
		self.pointerToGo = loader.loadModelCopy("models/arrow.egg")
		self.pointerToGo.setPos(self.ship.getPos())
		self.pointerToGo.setQuat(self.ship.getQuat())
		self.avoidTarget=None
		self.currentPatrolPoint=0
		self.target=None
		self.obstacle=None
		self.currentObstacle=None
		self.world=self.ship.world
		self.worldNP=self.ship.worldNP
		visNP = loader.loadModel(self.ship.egg)
		geom = visNP.findAllMatches('**/+GeomNode').getPath(0).node().getGeom(0)			
		shape=BulletConvexHullShape()
		shape.addGeom(geom)
		body = BulletGhostNode("ghost" + self.ship.name)
		self.bodyNP = self.worldNP.attachNewNode(body)
		self.bodyNP.node().addShape(shape)
		self.bodyNP.setPos(0,200,0)
		self.bodyNP.setHpr(self.ship.hpr)
		self.bodyNP.setCollideMask(BitMask32.allOn())
		self.bodyNP.setPythonTag("obj",self)
		self.bodyNP.setPythonTag("pnode",visNP)
		self.world.attachGhost(self.bodyNP.node())
		self.bodyNP.reparentTo(self.ship.bodyNP)
		self.status=C_BEHAVIOR_STATUS_CURRENT
		
	def getStatus(self):
		return self.status
		
	def run(self):
		self.runBehav()
		self.runPhysics()
		
	def runBehav(self):
		pass
		
	def runPhysics(self):
		pass
		
	def calcDistance(self,node1,node2):
		pos1=node1.getPos()
		pos2=node2.getPos()
		dx=pos1.getX()-pos2.getX()
		dy=pos1.getY()-pos2.getY()
		dz=pos1.getZ()-pos2.getZ()
		distance=int(round(sqrt(dx*dx+dy*dy+dz*dz),0))
		return distance
		
	def avoidObstacle(self,NPship,obj,NPobj):
		if self.obstacle!=obj:
			self.obstacle=obj
			#~ print obj
			if self.target==None:
				self.target=NodePath('PatrolPoint')
			pt1, pt2 = NPobj.getTightBounds()
			size=0
			xDim = pt2.getX() - pt1.getX() 
			yDim = pt2.getY() - pt1.getY() 
			zDim = pt2.getZ() - pt1.getZ() 
			if xDim > yDim:
				if xDim > zDim:
					size=xDim
				elif zDim>yDim:
					size=zDim
				else:
					size=yDim
			else:
				if yDim > zDim:
					size=yDim
				else:
					size=zDim
			#~ size*=3
			pt1, pt2 = NPship.getTightBounds()
			size2=0
			xDim = pt2.getX() - pt1.getX() 
			yDim = pt2.getY() - pt1.getY() 
			zDim = pt2.getZ() - pt1.getZ() 
			if xDim > yDim:
				if xDim > zDim:
					size2=xDim
				elif zDim>yDim:
					size2=zDim
				else:
					size2=yDim
			else:
				if yDim > zDim:
					size2=yDim
				else:
					size2=zDim
			if size2>size:
				size=size2

			if size<50:
				size=50
			if self.bodyNP!=None and self.bodyNP.isEmpty()==False and obj.bodyNP!=None and obj.bodyNP.isEmpty==False:
				#~ self.target.setHpr(self.ship.bodyNP.getHpr())
				self.target.setQuat(self.ship.getQuat())
				self.target.setPos(obj.bodyNP.getPos())
				self.target.setPos(self.target,(size,0,size))

			self.currentPatrolPoint-=1
			if self.currentPatrolPoint<0:
				self.currentPatrolPoint=len(self.patrolsPoint)-1
				#~ print "behavior::avoidobstalce " + str(self.ship.bodyNP.getPos())
			
	def avoidTargeted(self):
		self.avoidTarget=NodePath('PatrolPoint')
		self.avoidTarget.setQuat(self.ship.bodyNP.getQuat())
		self.avoidTarget.setPos(self.target.getPos())
		self.avoidTarget.setPos(self.avoidTarget,(200,0,200))