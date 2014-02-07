from direct.distributed.PyDatagram import PyDatagram 

class netMessageUDP:
	def __init__(self,msgID,IP,port):
		self.msg=self.myNewPyDatagram(msgID)
		self.ip=IP
		self.port=port
		
	def getIP(self):
		return self.ip
		
	def getPort(self):
		return self.port
		
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
		