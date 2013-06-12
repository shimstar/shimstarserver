class World:
	instance=None
	def __init__(self):
		self.zone={}
		
	@staticmethod
	def getInstance():
		if World.instance==None:
			World.instance=World()
		return World.instance
		
	def setZone(self,id,ip,port):
		self.zone[id]=str(ip) + ":" + str(port)
		
	def getZone(self,id):
		if self.zone.has_key(id)==True:
			return self.zone[id]
		else:
			return None
			
