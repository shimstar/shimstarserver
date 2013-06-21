from direct.distributed.PyDatagram import PyDatagram 

class message:
	nbMessage=0
	def __init__(self,msgID,msg,connexion):
		self.numero=message.nbMessage
		message.nbMessage+=1
		self.msgID=msgID
		self.msg=self.myNewPyDatagram(msgID,str(self.numero) + "@" + msg)
		self.connexion=connexion
		
	def getId(self):
		return self.msgID
		
	def getNumero(self):
		return self.numero
			
	def getMsg(self):
		return self.msg
		
	def getConnexion(self):
		return self.connexion

	def myNewPyDatagram(self,id,msg):
		# send a test message
		myPyDatagram=PyDatagram()
		myPyDatagram.addUint32(id)
		if isinstance(msg,str)==True:
			myPyDatagram.addString(msg)
		else:
			for el in msg:
				if isinstance(el,int):
					print "int"
				elif isintance(el,float):
					print "float"
				elif isinstance(el,str):
					print "str"
		myPyDatagram.addString(msg)
		#~ pass
		return myPyDatagram