import direct.directbase.DirectStart
from pandac.PandaModules import * 
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
import sys, imp, os, string
from direct.distributed.PyDatagram import PyDatagram 
from direct.distributed.PyDatagramIterator import PyDatagramIterator 

from shimstar.network.networkmessage import *
from shimstar.network.netmessage import *
from shimstar.core.constantes import *
from shimstar.user.user import *

class NetworkTCPServer():
	instance=None
	def __init__(self):
		instance=self
		
		#~ networkmessage()
		self.listOfMessage=[]
		self.cManager = QueuedConnectionManager()
		self.cListener = QueuedConnectionListener(self.cManager, 0)
		self.cReader = QueuedConnectionReader(self.cManager, 0)
		self.cWriter = ConnectionWriter(self.cManager,0)
		self.Connections = {}
		self.activeConnections=[]                                                    # We'll want to keep track of these later
		
		self.portAddressTCP=C_PORT_ZONE                               #No-other TCP/IP services are using this port
		
		backlog=1000                                                            #If we ignore 1,000 connection attempts, something is wrong!
		try:
			self.tcpSocket = self.cManager.openTCPServerRendezvous(self.portAddressTCP,backlog)
		except:
			print "Unexpected error:", sys.exc_info()[0]

		self.cListener.addConnection(self.tcpSocket)
		
		taskMgr.add(self.tskListenerPolling,"Poll the connection listener",-39)
		#~ taskMgr.add(self.tskListenerPolling,"Poll the connection listener")
		taskMgr.add(self.tskReaderPolling,"Poll the connection reader",-40)
		taskMgr.add(self.tskNetworkMessage,"Poll the messages",-38)
		
	@staticmethod
	def getInstance():
		if NetworkTCPServer.instance==None:
			NetworkTCPServer.instance=NetworkTCPServer()
			
		return NetworkTCPServer.instance
		
	
	def tskNetworkMessage(self,task):
		"""
			This method send message in another task than the reader, to avoid nuggle
		"""
		msgs=NetworkMessage.getInstance().getListOfMessage()
		
		if len(msgs)>0:
			for msg in msgs:
				ret=self.cWriter.send(msg.getMsg(),msg.getConnexion(),True)
				
		msgs=NetworkMessage.getInstance().getListOfMessageForAllUsers()
		
		if len(msgs)>0:
			for msg in msgs:
				for u in User.listOfUser:
					ret=self.cWriter.send(msg.getMsg(),User.listOfUser[u].getConnexion(),True)
		
		return Task.cont
		
	def tskListenerPolling(self,taskdata):
		"""
			Listener on connexion
		"""
		#~ print self.cListener.newConnectionAvailable()
		if self.cListener.newConnectionAvailable():
			rendezvous = PointerToConnection()
			netAddress = NetAddress()
			newConnection = PointerToConnection()
		
			if self.cListener.getNewConnection(rendezvous,netAddress,newConnection):
				newConnection = newConnection.p()
				newConnection.setNoDelay(True)
				self.activeConnections.append(newConnection) # Remember connection
				self.cReader.addConnection(newConnection)     # Begin reading connection
				self.Connections[str(newConnection.this)] = rendezvous 
		if self.cManager.resetConnectionAvailable():
			conn=PointerToConnection()
			self.cManager.getResetConnection(conn)
			c=conn.p()
			if self.activeConnections.count(c)>0:
				self.activeConnections.remove(c)
				usrToDelete=None
				for usr in User.listOfUser:
					if  User.listOfUser[usr].getConnexion()==c:
						usrToDelete=User.listOfUser[usr]
				if usrToDelete!=None:
					#~ usrToDelete.saveToBDD()
					User.lock.acquire()
					usrToDelete.destroy()
					for usr in User.listOfUser:
						if User.listOfUser[usr]!=usrToDelete:
							nm=netMessage(C_NETWORK_USER_OUTGOING,User.listOfUser[usr].getConnexion())
							nm.addInt(usrToDelete.getId())
							NetworkMessage.getInstance().addMessage(nm)
							#~ NetworkMessage.getInstance().addMessage(C_NETWORK_USER_OUTGOING,str(usrToDelete.getId()),User.listOfUser[usr].getConnexion())
					User.lock.release()
				
			if self.Connections.has_key(str(c)):
				del self.Connections[str(c)]
			self.cReader.removeConnection(c)
			self.cManager.closeConnection(c)

		return Task.cont
	
	def tskReaderPolling(self,taskdata):
		"""
			Read the network data
		"""
		if self.cReader.dataAvailable():
			datagram=NetDatagram()  # catch the incoming data in this instance
			# Check the return value; if we were threaded, someone else could have
			# snagged this data before we did
			#~ print datagram
			if self.cReader.getData(datagram):
				self.myProcessDataFunction(datagram,taskdata.time)
		return Task.cont
		
	#~ @updated
	def myProcessDataFunction(self,netDatagram,timer):
		"""
			Process messages incoming from network
		"""
		myIterator=PyDatagramIterator(netDatagram)
		connexion=netDatagram.getConnection()
		msgTab=[]
		msgID=myIterator.getUint32()		
		print msgID
		if msgID==C_NETWORK_CONNECT:
			User.lock.acquire()
			idusr=int(myIterator.getUint32())
			idchar=int(myIterator.getUint32())
			#~ print "networktcp:: id " + str(idusr) + "/" + str(idchar)
			tempUser=User(id=idusr)
			tempUser.setIp(netDatagram.getAddress().getIpString())
			tempUser.setConnexion(connexion)
			tempUser.setCurrentCharacter(idchar)
			print "user connected to zone"
			User.lock.release()
			
				
		
	def sendMessage(self,idMessage,message,connexion):
		"""
		method allowing to send directly a msg
		"""
		print "MESSAGE SORTANT ============" + str(idMessage) + "/" + str(message)
		self.cWriter.send(self.myNewPyDatagram(id,message),connexion)

	def myNewPyDatagram(self,id,message):
		# send a test message
		myPyDatagram=PyDatagram()
		myPyDatagram.addUint8(id)
		myPyDatagram.addString(message)
		return myPyDatagram
		
	def getListOfMessageById(self,id):
		msgToReturn=[]
		for msg in self.listOfMessage:
			iop=msg.getId()
			if(msg.getId()==id):
				msgToReturn.append(msg)
			
		return msgToReturn