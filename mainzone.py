import os,sys
from pandac.PandaModules import loadPrcFileData 
loadPrcFileData("", "window-type none")
import direct.directbase.DirectStart
from pandac.PandaModules import * 
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
from shimstar.core.stateserver import *
from shimstar.zoneserver.network.networkmainserver import *
from shimstar.zoneserver.network.networkzonetcpserver import *
from shimstar.world.zone.zone import *

class ShimStarServerZone():
	def __init__(self):
		if NetworkMainServer.getInstance().isConnected()==True:
			NetworkMainServer.getInstance().start()
		else:
			self.quit()
			
		NetworkTCPServer.getInstance()
		z=Zone(C_ID_ZONE)
		z.start()
		taskMgr.add(self.event,"Poll main event",-38)
		
	def event(self,task):
		if StateServer.getInstance().getState()==C_SERVERSTATE_QUIT:
			self.quit()
			return Task.done
		return Task.cont
		
	def quit(self):
		taskMgr.remove("Poll main event")
		sys.exit()
	
	def saveOnForcedQuit(self):
		print "main::saveOnForcedQuit"
	
app=ShimStarServerZone()
run()
			
atexit.register(app.saveOnForcedQuit)