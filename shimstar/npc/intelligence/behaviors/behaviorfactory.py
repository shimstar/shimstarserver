from shimstar.core.constantes import *
from shimstar.npc.intelligence.behaviors.behaviorpatrol import *
#~ from shimstar.intelligence.behaviors.behaviorattack import *

class behaviorFactory():
	def __init__(self):
		pass
		
	@staticmethod
	def getBehavior(type,npc):
		if type==C_BEHAVIOR_PATROL:
			return behaviorPatrol(npc)
		return None
		