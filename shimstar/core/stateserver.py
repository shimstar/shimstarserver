from shimstar.core.constantes import *

class StateServer:
	instance=None
	
	def __init__(self):
		self.state=C_SERVERSTATE_INI
		
	def setState(self,state):
		self.state=state
		
	def getState(self):
		return self.state
		
	@staticmethod
	def getInstance():
		if StateServer.instance is None:
			StateServer.instance=StateServer()
			
		return StateServer.instance