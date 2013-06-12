from direct.distributed.PyDatagram import PyDatagram 

class netMessage:
	def __init__(self,msgID):
		self.msg=self.myNewPyDatagram(msgID)
		
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
		