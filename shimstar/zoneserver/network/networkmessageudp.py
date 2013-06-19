from shimstar.network.message import *
from shimstar.core.constantes import *

class NetworkMessageUdp:
	instance=None
	def __init__(self):
		NetworkMessageUdp.instance=self
		self.listOfMessage=[]
		
	def getListOfMessage(self):
		tmp=[]
		for msg in self.listOfMessage:
			tmp.append(msg)
		self.listOfMessage=[]
		return tmp
		
	def addMessage(self,msgID,msg,netAdr):
		temp=message(msgID,msg,netAdr)
		self.listOfMessage.append(temp)
	
	@staticmethod
	def getInstance():
		if NetworkMessageUdp.instance==None:
			NetworkMessageUdp.instance=NetworkMessageUdp()
		return NetworkMessageUdp.instance
