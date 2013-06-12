from direct.distributed.PyDatagram import PyDatagram 

class netMessage:
	def __init__(self,msgID,connexion):
		self.msgID=msgID
		self.msg=self.myNewPyDatagram(msgID)
		self.connexion=connexion
		
	def getNumero(self):
		return self.numero
			
	def getId(self):
		return self.msgID
			
	def getMsg(self):
		return self.msg
		
	def getConnexion(self):
		return self.connexion

	def myNewPyDatagram(self,id):
		# send a test message
		myPyDatagram=PyDatagram()
		myPyDatagram.addUint32(id)
		return myPyDatagram
		
	def addFloat(self,param):
		self.msg.addStdfloat(param)
	
	def addInt(self,param):
		self.msg.addUint32(param)
		
	def addString(self,param):
		self.msg.addString(param)
		