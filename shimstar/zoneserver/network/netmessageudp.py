from direct.distributed.PyDatagram import PyDatagram 

class netMessageUDP:
	def __init__(self,msgID,IP):
		self.msg=self.myNewPyDatagram(msgID)
		self.ip=IP
		
	def getIP(self):
		return self.ip
		
	def getNumero(self):
		return self.numero
			
	def getMsg(self):
		return self.msg
		
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
		