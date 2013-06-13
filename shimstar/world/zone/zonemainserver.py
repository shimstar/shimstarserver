class ZoneMainServer:
	listOfZone={}
	def __init__(self,id,ip,port,connexion):
		self.id=id
		self.port=port
		self.ip=ip
		self.connexion=connexion
		ZoneMainServer.listOfZone[self.id]=self
		
	@staticmethod
	def getZone(id):
		if ZoneMainServer.listOfZone.has_key(id)==True:
			return ZoneMainServer.listOfZone[id]
		return None
		
	def getConfig(self):
		return self.ip,self.port
		
	def getConnexion(self):
		return self.connexion