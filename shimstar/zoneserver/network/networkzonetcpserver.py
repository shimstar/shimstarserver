import direct.directbase.DirectStart
from pandac.PandaModules import * 
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
import sys, imp, os, string
from direct.distributed.PyDatagram import PyDatagram 
from direct.distributed.PyDatagramIterator import PyDatagramIterator 

from shimstar.network.networkmessage import *
from shimstar.network.netmessage import *
from shimstar.network.message import *
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
		self.activeConnections=[]          		# We'll want to keep track of these later
		self.listOfMessage=[] 
		
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
				if msg.getConnexion()!=None and isinstance(msg.getConnexion(),Connection):
					ret=self.cWriter.send(msg.getMsg(),msg.getConnexion(),True)
				else:
					print "Error in networkzonetctpserver::tskNetworkMessage Connection is not good " +str(msg.getConnexion())
				
		msgs=NetworkMessage.getInstance().getListOfMessageForAllUsers()
		
		if len(msgs)>0:
			for msg in msgs:
				User.lock.acquire()
				for u in User.listOfUser:
					ret=self.cWriter.send(msg.getMsg(),User.listOfUser[u].getConnexion(),True)
				User.lock.release()
		
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
			#~ print self.activeConnections.count(c)
			if self.activeConnections.count(c)>0:
				self.activeConnections.remove(c)
				usrToDelete=None
				User.lock.acquire()
				for usr in User.listOfUser:
					if  User.listOfUser[usr].getConnexion()==c:
						usrToDelete=User.listOfUser[usr]
				User.lock.release()
				if usrToDelete!=None:
					usrToDelete.saveToBDD()
					usrToDelete.destroy()
					User.lock.acquire()
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
		#~ print msgID
		if msgID==C_NETWORK_CONNECT:
			idusr=int(myIterator.getUint32())
			idchar=int(myIterator.getUint32())
			print "networkzonetcpserver::myprocessdatafunction " + str(idchar)
			tempUser=User(id=idusr)
			tempUser.setIp(netDatagram.getAddress().getIpString())			
			tempUser.setConnexion(connexion)
			tempUser.setCurrentCharacter(idchar)
			print "user connected to zone"
		elif msgID==C_NETWORK_DEATH_CHAR:
			idusr=int(myIterator.getUint32())
			userFound=None
			User.lock.acquire()
			for usr in User.listOfUser:
				if usr==idusr:
					userFound=User.listOfUser[usr]
			User.lock.release()
			if userFound!=None:
				User.listOfUser[usr].destroy()

		elif msgID==C_NETWORK_ASKING_NPC:
			iduser=int(myIterator.getUint32())
			msgTab=[]
			msgTab.append(iduser)
			temp=message(msgID,msgTab)
			self.listOfMessage.append(temp)
		elif msgID==C_NETWORK_ASKING_CHAR:
			iduser=int(myIterator.getUint32())
			msgTab=[]
			msgTab.append(iduser)
			temp=message(msgID,msgTab)
			self.listOfMessage.append(temp)
		elif msgID==C_NETWORK_CHARACTER_MOUSE:
			iduser=int(myIterator.getUint32())
			mousePosX=float(myIterator.getStdfloat())
			mousePosY=float(myIterator.getStdfloat())
			usr=User.getUserById(iduser)
			if usr!=None:
				usr.getCurrentCharacter().getShip().setMousePos(mousePosX,mousePosY)
		###UDP STUFF
		elif msgID==C_NETWORK_CHARACTER_SPEED:
			iduser=int(myIterator.getUint32())
			speed=int(myIterator.getInt32())
		
			usr=User.getUserById(iduser)
			if usr!=None:
				usr.getCurrentCharacter().getShip().setMouseWheel(speed)
		elif msgID==C_NETWORK_CHARACTER_KEYBOARD:
			idUser=myIterator.getUint32()
			usr=User.getUserById(idUser)
			if usr!=None:
				nbKeys=myIterator.getUint32()
				for i in range(nbKeys):
					key=myIterator.getString()
					val=myIterator.getUint32()
					usr.getCurrentCharacter().getShip().modifyPYR(key,val)
		elif msgID==C_NETWORK_CHAR_SHOT:
			msgTab=[]
			msgTab.append(myIterator.getUint32())
			msgTab.append(myIterator.getUint32())
			msgTab.append(myIterator.getStdfloat())
			msgTab.append(myIterator.getStdfloat())
			msgTab.append(myIterator.getStdfloat())
			msgTab.append(myIterator.getStdfloat())
			msgTab.append(myIterator.getStdfloat())
			msgTab.append(myIterator.getStdfloat())
			msgTab.append(myIterator.getStdfloat())
			temp=message(msgID,msgTab)
			self.listOfMessage.append(temp)
		elif msgID==C_NETWORK_START_MINING:
			msgTab=[]
			msgTab.append(myIterator.getUint32()) #userId
			msgTab.append(myIterator.getUint32()) #asteroid Id
			temp=message(msgID,msgTab)
			self.listOfMessage.append(temp)	
		elif msgID==C_NETWORK_STOP_MINING:
			msgTab=[]
			msgTab.append(myIterator.getUint32()) #userId
			temp=message(msgID,msgTab)
			self.listOfMessage.append(temp)	
		
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
		
	def removeMessage(self,msg):
		self.listOfMessage.remove(msg)