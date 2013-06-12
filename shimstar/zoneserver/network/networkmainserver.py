from pandac.PandaModules import * 
from direct.distributed.PyDatagram import PyDatagram 
from direct.distributed.PyDatagramIterator import PyDatagramIterator 
from direct.stdpy import threading

from shimstar.core.constantes import *
from shimstar.zoneserver.network.netmessage import *
from shimstar.core.stateserver import *

class NetworkMainServer(threading.Thread):
	instance=None
	def __init__(self):
		threading.Thread.__init__(self)
		self.port=7777
		self.ip="127.0.0.1"
		self.stopThread=False
		self.timeout_in_miliseconds=3000  # 3 seconds
		self.listOfMessage=[] 
		
		self.cManager = QueuedConnectionManager()
		self.cReader = QueuedConnectionReader(self.cManager, 0)
		self.cWriter = ConnectionWriter(self.cManager,0)
		
		self.myConnection=self.cManager.openTCPClientConnection(self.ip,self.port,self.timeout_in_miliseconds)
		if self.myConnection:
			self.cReader.addConnection(self.myConnection)  # receive messages from server
			self.myConnection.setNoDelay(True)
			nm=netMessage(C_NETWORK_CONFIG_ZONE)
			nm.addInt(C_ID_ZONE)
			nm.addString(C_IP_ZONE)
			nm.addInt(C_PORT_ZONE)
			self.sendMessage(nm)
		
	@staticmethod
	def getInstance():
		if NetworkMainServer.instance==None:
			NetworkMainServer.instance=NetworkMainServer()
			
		return NetworkMainServer.instance
		
	def isConnected(self):
		if self.myConnection==None:
			return False
		else:
			return True
		
	def run(self):
		while not self.stopThread:
			while self.cReader.dataAvailable():
				datagram=NetDatagram()  # catch the incoming data in this instance
				if self.cReader.getData(datagram):
					self.myProcessDataFunction(datagram)
					
		print "le thread NetworkMainServer s'est termine proprement"
		
	def stop(self):
		self.stopThread=True
		
	def myProcessDataFunction(self,netDatagram):
		myIterator=PyDatagramIterator(netDatagram)
		connexion=netDatagram.getConnection()
		msgID=myIterator.getUint8()
		msgTab=[]
		if msgID==C_NETWORK_ACKNOWLEDGEMENT:
			StateServer.getInstance().setState(C_SERVERSTATE_RUNNING)
		
	def getListOfMessageById(self,id):
		msgToReturn=[]
		for msg in self.listOfMessage:
			iop=msg.getId()
			if(msg.getId()==id):
				msgToReturn.append(msg)
			
		return msgToReturn
		
	def removeMessage(self,msg):
		self.listOfMessage.remove(msg)
		
	def sendMessage(self,msg):
		self.cWriter.send(msg.getMsg(),self.myConnection)