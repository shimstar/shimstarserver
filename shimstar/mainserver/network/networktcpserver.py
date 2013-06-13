import direct.directbase.DirectStart
from pandac.PandaModules import * 
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
import sys, imp, os, string
from direct.distributed.PyDatagram import PyDatagram 
from direct.distributed.PyDatagramIterator import PyDatagramIterator 

from shimstar.mainserver.network.networkmessage import *
from shimstar.mainserver.network.netmessage import *
from shimstar.core.constantes import *
from shimstar.user.user import *
from shimstar.world.zone.zonemainserver import *

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

		self.portAddressTCP=7777                                                       #No-other TCP/IP services are using this port
		backlog=1000                                                            #If we ignore 1,000 connection attempts, something is wrong!
		self.tcpSocket = self.cManager.openTCPServerRendezvous(self.portAddressTCP,backlog)

		self.cListener.addConnection(self.tcpSocket)
		
		taskMgr.add(self.tskListenerPolling,"Poll the connection listener",-39)
		#~ taskMgr.add(self.tskListenerPolling,"Poll the connection listener")
		taskMgr.add(self.tskReaderPolling,"Poll the connection reader",-40)
		taskMgr.add(self.tskNetworkMessage,"Poll the messages",-38)
		
	
	def tskNetworkMessage(self,task):
		"""
			This method send message in another task than the reader, to avoid nuggle
		"""
		msgs=NetworkMessage.getInstance().getListOfMessage()
		
		if len(msgs)>0:
			for msg in msgs:
				ret=self.cWriter.send(msg.getMsg(),msg.getConnexion(),True)
		
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
					if usr.getConnexion()==c:
						usrToDelete=usr
				if usrToDelete!=None:
					#~ usrToDelete.saveToBDD()
					usrToDelete.destroy()
					for usr in User.listOfUser:
						if usr!=usrToDelete:
							NetworkMessage.getInstance().addMessage(C_USER_OUTGOING,str(usrToDelete.getId()),usr.getConnexion())
				if usrToDelete!=None:
					#~ if User.listOfUser.index(usrToDelete.getId())>=0:
						#~ User.listOfUser.remove(usrToDelete)		
					userToDelete.destroy()
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
			name=myIterator.getString()
			password=myIterator.getString()
			if User.userExists(name)==True:
				if User.getUserInstantiatedByName(name)==False:
					tempUser=User(name=name)				
					if(tempUser.getPwd()==password):					
						nm=netMessage(C_NETWORK_CONNECT,connexion)
						nm.addInt(C_CONNEXION_OK)
						nm.addString(tempUser.getXml().toxml())
						NetworkMessage.getInstance().addMessage(nm)
						tempUser.destroy()
					else:
						nm=netMessage(C_NETWORK_CONNECT,connexion)
						nm.addInt(C_CONNEXION_WRONGPWD)
						NetworkMessage.getInstance().addMessage(nm)
						tempUser.destroy()						
				else:
					nm=netMessage(C_NETWORK_CONNECT,connexion)
					nm.addInt(C_CONNEXION_ALREADYCONNECTED)
					NetworkMessage.getInstance().addMessage(nm)
					tempUser.destroy()
			else:
				nm=netMessage(C_NETWORK_CONNECT,connexion)
				nm.addInt(C_CONNEXION_NOACCOUNT)
				NetworkMessage.getInstance().addMessage(nm)
		elif msgID==C_NETWORK_CONFIG_ZONE:
			id=myIterator.getUint32()
			ip=myIterator.getString()
			port=myIterator.getUint32()
			pp=ZoneMainServer.getZone(id)
			temp=ZoneMainServer(id,ip,port,connexion)
			nm=netMessage(C_NETWORK_ACKNOWLEDGEMENT,connexion)
			NetworkMessage.getInstance().addMessage(nm)
		elif msgID==C_NETWORK_INFO_ZONE:
			id=myIterator.getUint32()
			zm=ZoneMainServer.getZone(id)
			ip,port=zm.getConfig()
			nm=netMessage(C_NETWORK_INFO_ZONE,connexion)
			nm.addString(ip)
			nm.addInt(port)
			NetworkMessage.getInstance().addMessage(nm)
		elif msgID==C_NETWORK_USER_CHOOSE_HERO:
			iduser=myIterator.getUint32()
			idchar=myIterator.getUint32()
			tempUser=User.getUserById(iduser)
			if tempUser!=None:
				tempUser.setCurrent(idchar)
		
		
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