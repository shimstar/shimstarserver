from shimstar.npc.intelligence.behaviors.behavior import *
from shimstar.core.constantes import *
import os,sys

class BehaviorAttack(behavior):
	def __init__(self,npc):
		super(BehaviorAttack,self).__init__(npc)
		self.patrolsPoint=[]
	
	def setTarget(self,target):
		self.target=target
		
	def run(self):
		if self.target==None or self.target.isEmpty()==True:
			self.status=C_BEHAVIOR_STATUS_FINISHED
		else:
			self.runBehav()
			self.runPhysics()
		
	def runBehav(self):
		if self.target.isEmpty()!=True:
			if self.avoidTarget==None:
				if self.target!=None:
					self.runShotTo()
			else:
				self.pointerToGo.setPos(self.ship.bodyNP.getPos())
				self.pointerToGo.lookAt(self.avoidTarget)
				dist=self.calcDistance(self.avoidTarget,self.ship.bodyNP)
				if dist<50:
					self.avoidTarget=None
				
	def runShotTo(self):
		shooterForward = self.ship.bodyNP.getQuat().getForward()
		shooterForward.normalize()
		posShooter = self.ship.bodyNP.getPos() + shooterForward*100
		self.pointerToGo.setPos(posShooter)
		posTarget = self.target.getPos()
		targetVelocityVect = self.target.node().getLinearVelocity()
		speedShooter = self.ship.getWeapon().getSpeed()			
		speedTarget = sqrt(targetVelocityVect.getX()*targetVelocityVect.getX()+targetVelocityVect.getY()*targetVelocityVect.getY()+targetVelocityVect.getZ()*targetVelocityVect.getZ())
		if speedTarget == 0:
			self.pointerToGo.lookAt(self.target.getPos())
		else:
			diameterPoint1 = posShooter + (posTarget - posShooter) * ( speedShooter / ( speedShooter + speedTarget)) # internal diameter point
			diameterPoint2 = posShooter + (posTarget - posShooter) * ( speedShooter / ( speedShooter - speedTarget)) # external diameter point TODO: manage the case where speeds are equal (right now, we have a division by 0 exception)
			dp1X = diameterPoint1.getX()
			dp1Y = diameterPoint1.getY()
			dp1Z = diameterPoint1.getZ()
			dp2X = diameterPoint2.getX()
			dp2Y = diameterPoint2.getY()
			dp2Z = diameterPoint2.getZ()
			dpDiffX = dp1X - dp2X
			dpDiffY = dp1Y - dp2Y
			dpDiffZ = dp1Z - dp2Z
			touchSphereCenter = (diameterPoint1 + diameterPoint2) / 2 # middle
			touchSphereRadius = 0.5 * sqrt(dpDiffX*dpDiffX + dpDiffY*dpDiffY + dpDiffZ*dpDiffZ)
			# we now want to find the intersection between the sphere and the Target ship movement
			# we translate coordinates so that the sphere is centered on the origin (this simplifies the equation). Movement vector remains unchanged.
			# sphere equation can now be written as:
			# x*x + y*y + z*z = radius*radius
			translatedPosTarget = posTarget - touchSphereCenter
			translatedDirTarget = targetVelocityVect
			# movement line is now:
			# (x, y, z) = pos + t*dir (with t unknown)
			pX = translatedPosTarget.getX()
			pY = translatedPosTarget.getY()
			pZ = translatedPosTarget.getZ()
			dX = translatedDirTarget.getX()
			dY = translatedDirTarget.getY()
			dZ = translatedDirTarget.getZ()
			# we have to solve:
			# (pX+t*dX)**2 + (pY+t*dY)**2 + (pZ+t*dZ)**2 = radius**2
			# this can be written as:
			# coefA*(t*t) + coefB*(t) + coefC = 0
			# with:
			coefA = dX*dX + dY*dY + dZ*dZ
			coefB = (dX*pX + dY*pY + dZ*pZ)*2
			coefC = pX*pX + pY*pY + pZ*pZ - touchSphereRadius*touchSphereRadius
			coefDelta = coefB*coefB - 4*coefA*coefC
			# if the bullet is faster than the target, delta should always be positive. TODO: manage exceptions
			sol1T=0
			sol2T=0
			if coefA!=0:
				try:
					sol1T = (-coefB + sqrt(abs(coefDelta)))/(2*coefA)
					sol2T = (-coefB - sqrt(abs(coefDelta)))/(2*coefA)
				except:
					print "behaviorAttack::runShotTo " + str(coefB) + "//" + str(coefA) + "//" + str(coefDelta)
					print sys.exc_info()[0]
			else:
				sol1T=0
				sol2T=0
			# only one solution for (t) is positive. This is the one we want because it corresponds to the point in the same direction as the ship movement (the other solution is backward)
			maxT = 0
			if sol1T > sol2T:
				maxT = sol1T
			else:
				maxT = sol2T
			#as defined above:
			translatedIntersect = translatedPosTarget + translatedDirTarget*maxT
			#we translate back to the original coordinates
			finalIntersect = translatedIntersect + touchSphereCenter
			self.pointerToGo.lookAt(finalIntersect.getX(),finalIntersect.getY(),finalIntersect.getZ())
			#~ print str(finalIntersect.getX()) + "/" + str (finalIntersect.getY()) + str(finalIntersect.getZ())
				
	def avoidTargeted(self):
		self.avoidTarget=NodePath('PatrolPoint')
		self.avoidTarget.setHpr(self.ship.bodyNP.getHpr())
		self.avoidTarget.setPos(self.target.getPos())
		self.avoidTarget.setPos(self.avoidTarget,(200,0,200))
					
	def runPhysics(self):
		#~ print self.ship.getPos()
		result = self.world.contactTest(self.bodyNP.node())
		for contact in result.getContacts():
			pass
			#~ self.avoidObstacle(contact.getNode0().getPythonTag("pnode"),contact.getNode1().getPythonTag("obj"),contact.getNode1().getPythonTag("pnode"))
		
		y=0
		p=0
		
		HDif=self.ship.bodyNP.getH()-self.pointerToGo.getH()
		PDif=self.ship.bodyNP.getP()-self.pointerToGo.getP()
		RDif=self.ship.bodyNP.getR()-self.pointerToGo.getR()
		
		if HDif>1 and HDif<179:
			p=-1
		elif HDif<-1 and HDif>-179:
			p=1
		elif HDif>179:
			p=1
		elif HDif<-179:
			p=-1
			
		if PDif>1 and PDif<179:
			y=-1
		elif PDif<-1 and PDif>-179:
			y=1
		elif PDif>179:
			y=1
		elif PDif<-179:
			y=-1
		
		forwardVec=self.ship.bodyNP.getQuat().getForward()
		v=Vec3(y*self.ship.torque,0.0,p*self.ship.torque)
		v= self.worldNP.getRelativeVector(self.ship.bodyNP,v) 
		self.ship.bodyNP.node().applyTorqueImpulse(v)
		av=self.ship.bodyNP.node().getAngularVelocity()
		av2=av*self.ship.frictionAngular
		self.ship.bodyNP.node().setAngularVelocity(av2)
		
		if self.target!=None and self.target.isEmpty()!=True:
			dist=self.calcDistance(self.target,self.ship.bodyNP)
			if dist <300:
				self.avoidTargeted()
			else:
				if dist<self.ship.weapon.getRange():
					if (HDif+PDif)<50:
						self.ship.shot()
			if dist > 100:
				if (self.ship.bodyNP.node().getLinearVelocity()==Vec3(0,0,0)):
					f=Vec3(forwardVec.getX()**self.ship.engine.getSpeedMax()/2,forwardVec.getY()**self.ship.engine.getSpeedMax()/2,forwardVec.getZ()**self.ship.engine.getSpeedMax()/2)
				else:
					f=Vec3(forwardVec.getX()**self.ship.engine.getSpeedMax()/2,forwardVec.getY()**self.ship.engine.getSpeedMax()/2,forwardVec.getZ()**self.ship.engine.getSpeedMax()/2)
				self.ship.bodyNP.node().applyCentralForce(f)
			if self.ship.bodyNP.node().getLinearVelocity()!=Vec3(0,0,0):
				self.ship.bodyNP.node().setLinearVelocity((self.ship.bodyNP.node().getLinearVelocity().getX()*self.ship.frictionVelocity,self.ship.bodyNP.node().getLinearVelocity().getY()*self.ship.frictionVelocity,self.ship.bodyNP.node().getLinearVelocity().getZ()*self.ship.frictionVelocity))

