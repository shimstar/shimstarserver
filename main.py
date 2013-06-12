from pandac.PandaModules import loadPrcFileData 
loadPrcFileData("", "window-type none")
#~ loadPrcFileData('','want-pstats 1')
import direct.directbase.DirectStart
from pandac.PandaModules import * 
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task

from shimstar.mainserver.network.networktcpserver import *
from shimstar.mainserver.mainserver import *
from shimstar.core.stateserver import *

class ShimStarServer():
	def __init__(self):
		NetworkTCPServer()
		#~ MainServer()
		taskMgr.add(self.event,"Poll main event",-36)
		
	def quit(self):
		taskMgr.remove("Poll main event")
		sys.exit()
		
	def event(self,task):
		if StateServer.getInstance().getState()==C_SERVERSTATE_QUIT:
			self.quit()
			return Task.done
		return Task.cont
	
	def saveOnForcedQuit(self):
		print "main::saveOnForcedQuit"
	
app=ShimStarServer()
run()
			
atexit.register(app.saveOnForcedQuit)