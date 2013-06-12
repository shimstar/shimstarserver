from direct.task.Task import Task

#~ from shimstar.mainserver.stateserver import *

class MainServer:
	def __init__(self):
		taskMgr.add(self.run,"Poll mainserver",-36)
		
		
	def run(self,task):
		while StateServer.getInstance().getState()!=C_SERVERSTATE_QUIT:
			self.runUserUpdate()
			
		return Task.cont
		
	def runUserUpdate(self):
		pass
	