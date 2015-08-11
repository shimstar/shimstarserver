from direct.distributed.PyDatagram import PyDatagram 

class netMessage:
	def __init__(self,msgID,connexion=None):
		self.msg=self.myNewPyDatagram(msgID)
		self.connexion=connexion
		
	def getConnexion(self):
		return self.connexion
			
	def getMsg(self):
		return self.msg
		
	def myNewPyDatagram(self,id):
		# send a test message
		myPyDatagram=PyDatagram()
		myPyDatagram.addUint32(id)
		return myPyDatagram
		
	def addFloat(self,param):
		self.msg.addStdfloat(param)
	
	def addUInt(self,param):
		self.msg.addUint32(param)
		
	def addString(self,param):
		self.msg.addString(param)
		