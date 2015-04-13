from shimstar.npc.intelligence.behaviors.behavior import *
from shimstar.core.constantes import *

class behaviorPatrol(behavior):
	def __init__(self,npc):
		super(behaviorPatrol,self).__init__(npc)
		self.patrolsPoint=[]
		
	def getPatrolPoints(self):
		return self.patrolsPoint
	
	def addPatrolPoint(self,pTarget):
		tgt=NodePath('tgtBehav' + str(len(self.patrolsPoint)))
		tgt.setPos(pTarget)
		self.patrolsPoint.append(tgt)
		
	def runBehav(self):
		nbPatrolsPoints=len(self.patrolsPoint)
		# If there is patrolspoints
		if nbPatrolsPoints>0:
			#if the patrolpoint change, change the target to turn into
			if self.target is None:
				self.target=self.patrolsPoint[self.currentPatrolPoint]
			self.pointerToGo.setPos(self.ship.bodyNP.getPos())
			self.pointerToGo.lookAt(self.target)

			dist=self.calcDistance(self.target,self.ship.bodyNP)
			#if distance to patrol point < 200, change patrol point or maybe stop the behavior because there was only one patrol point
			if dist<100:
				if nbPatrolsPoints==1:
					self.state=C_STOP_BEHAVIOR
				else:
					self.currentPatrolPoint+=1
					if self.currentPatrolPoint+1>len(self.patrolsPoint):
						self.currentPatrolPoint=0
					self.target=self.patrolsPoint[self.currentPatrolPoint]
		
	def runPhysics(self):
		self.runBehav()
		
		result = self.world.contactTest(self.bodyNP.node())
		for contact in result.getContacts():
			self.avoidObstacle(contact.getNode0().getPythonTag("pnode"),contact.getNode1().getPythonTag("obj"),contact.getNode1().getPythonTag("pnode"))
		
		y=0
		p=0
		
		HDif=self.ship.bodyNP.getH()-self.pointerToGo.getH()
		PDif=self.ship.bodyNP.getP()-self.pointerToGo.getP()
		RDif=self.ship.bodyNP.getR()-self.pointerToGo.getR()
		
		if 10 < HDif < 179:
			p=-1
		elif -10 > HDif > -179:
			p=1
		elif HDif>179:
			p=1
		elif HDif<-179:
			p=-1
			
		if 10 < PDif < 179:
			y=-1
		elif -10 > PDif > -179:
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
		
		if self.target is not None:
			dist=self.calcDistance(self.target,self.ship.bodyNP)
			if dist > 100:
				if self.ship.bodyNP.node().getLinearVelocity()==Vec3(0,0,0):
					f=Vec3(forwardVec.getX()*self.ship.engine.getSpeedMax(),forwardVec.getY()*self.ship.engine.getSpeedMax(),forwardVec.getZ()*self.ship.engine.getSpeedMax())
				else:
					f=Vec3(forwardVec.getX()*self.ship.engine.getSpeedMax()/2,forwardVec.getY()*self.ship.engine.getSpeedMax()/2,forwardVec.getZ()*self.ship.engine.getSpeedMax()/2)
				self.ship.bodyNP.node().applyCentralForce(f)
		if self.ship.bodyNP.node().getLinearVelocity()!=Vec3(0,0,0):
			self.ship.bodyNP.node().setLinearVelocity((self.ship.bodyNP.node().getLinearVelocity().getX()*self.ship.frictionVelocity,self.ship.bodyNP.node().getLinearVelocity().getY()*self.ship.frictionVelocity,self.ship.bodyNP.node().getLinearVelocity().getZ()*self.ship.frictionVelocity))
