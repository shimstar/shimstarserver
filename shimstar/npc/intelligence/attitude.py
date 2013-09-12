from shimstar.core.constantes import *
from shimstar.npc.intelligence.commons.commons import *
from shimstar.npc.intelligence.behaviors.behavior import *
from shimstar.npc.intelligence.behaviors.behaviorpatrol import *
from shimstar.npc.intelligence.behaviors.behaviorattack import *
from shimstar.npc.intelligence.behaviors.behaviorfactory import *
#~ from shimstar.core.function import *

class Attitude:
	def __init__(self,npc):
		self.behavior={}
		self.currentBehavior=-1
		self.attitude={}
		self.npc=npc
		
	def getBehaviors(self):
		return self.behavior
		
	def getAttitude(self):
		return self.attitude
		
	def run(self):
		if self.currentBehavior>=0:
			if self.behavior.has_key(self.currentBehavior)==True:
				if self.behavior[self.currentBehavior].getStatus()==C_BEHAVIOR_STATUS_CURRENT:
					self.behavior[self.currentBehavior].run()
				else:
					if len(self.behavior)>1:
						del self.behavior[self.currentBehavior]
						self.currentBehavior=len(self.behavior)-1
		else:
			if len(self.behavior)>0:
				self.currentBehavior=0
		
		if self.attitude.has_key(C_ATTITUDE_AGGRESSIVITE):
			if self.attitude[C_ATTITUDE_AGGRESSIVITE]>2:
				alreadyAttack=False
				for behav in self.behavior:
					if isinstance(self.behavior[behav],BehaviorAttack)==True:
						alreadyAttack=True
						break
				if alreadyAttack==False:
					nearer=None
					nearerDist=100000000
					ships=[]
					nnn=[]
					#~ users=self.npc.zone.users
					#~ for u in users:
						#~ ship=u.getCurrentCharacter().ship
						#~ ships.append(ship)
						#~ nnn.append(u)
					for n in self.npc.zone.npc:
						if n!=self.npc:
							ship=n.ship
							ships.append(ship)
							nnn.append(n)
					for s in ships:
						if s.bodyNP.isEmpty()==False:
							dist=calcDistance(self.npc.ship.bodyNP,s.bodyNP)
							if dist<nearerDist:
								nearerDist=dist
								nearer=ship
					if nearer!=None:
						print "attitude::run acquiring new target " + str(nearer)
						behav=self.setBehavior(C_BEHAVIOR_ATTACK)
						behav.setTarget(nearer.bodyNP)
					
	def runPhysics(self):
		if self.currentBehavior>=0:
			if self.behavior.has_key(self.currentBehavior)==True:
				self.behavior[self.currentBehavior].runPhysics()
		
	def setBehavior(self,beh):
		if self.behavior.has_key(beh)==False:
			self.behavior[beh]=behaviorFactory.getBehavior(beh,self.npc)
			self.currentBehavior=beh
		return self.behavior[beh]
		
	def addAttitude(self,att,lvl):
		self.attitude[att]=lvl
		
		