import direct.directbase.DirectStart
from pandac.PandaModules import * 
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.task.Task import Task
import sys, imp, os, string
from pandac.PandaModules import Point3, Vec3, Vec4,Quat
from direct.distributed.PyDatagram import PyDatagram 
from direct.distributed.PyDatagramIterator import PyDatagramIterator 
from shimstar.user.user import *
from shimstar.zoneserver.network.networkmessageudp import *
from shimstar.core.constantes import *
from shimstar.world.zone.zone import *
from shimstar.bdd.dbconnector import *
from direct.stdpy import threading


class NetworkZoneUDPServer(DirectObject,threading.Thread):
	instance=None
	def __init__(self,nom='threadUDP'):
		instance=self
		threading.Thread.__init__(self)
		self.nom = nom
		self.Terminated = False
		self.stopThread=False
		self.listOfUser=[]
		self.cManager = QueuedConnectionManager()
		self.cListener = QueuedConnectionListener(self.cManager, 0)
		self.cReader = QueuedConnectionReader(self.cManager, 0)
		self.cReader.setRawMode(0)
		self.cWriter = ConnectionWriter(self.cManager,0)
		self.cReader.setRawMode(0)
		self.Connections = {}
		self.activeConnections=[]                                                    # We'll want to keep track of these later

		self.port=C_PORT_UDP_ZONE                                                       #No-other TCP/IP services are using this port
		self.udpSocket = self.cManager.openUDPConnection(self.port)
		self.udpSocket.setReuseAddr(True) 

		self.cListener.addConnection(self.udpSocket)

	@staticmethod
	def getInstance():
		if NetworkZoneUDPServer.instance==None:
			NetworkZoneUDPServer.instance=NetworkZoneUDPServer()
		return NetworkZoneUDPServer.instance

	def run(self):
		"""
			This method send message in another task than the reader, to avoid nuggle
		"""
		while not self.stopThread:
			msgs=NetworkMessageUdp.getInstance().getListOfMessage()
			if len(msgs)>0:
				for msg in msgs:
					clientAddr = NetAddress() 
					clientAddr.setHost(msg.getConnexon(), self.port) 
					ret=self.cWriter.send(msg.getMsg(),self.udpSocket,clientAddr)
					
					with warnings.catch_warnings(record=True) as w:
						if len(w)>0:
							print "networkUpdWarningInSending " + str(w)
			if self.cReader.dataAvailable():
				datagram=NetDatagram()  
				if self.cReader.getData(datagram):
					self.myProcessDataFunction(datagram)

		
	#~ @updated
	def myProcessDataFunction(self,netDatagram):
		"""
			Process messages incoming from network
		"""
		myIterator=PyDatagramIterator(netDatagram)
		connexion=netDatagram.getConnection()
		msgID=myIterator.getUint32()
		print msgID


	def myNewPyDatagram(self,id,message):
		# send a test message
		myPyDatagram=PyDatagram()
		myPyDatagram.addUint8(id)
		myPyDatagram.addString(message)
		return myPyDatagram
		
		