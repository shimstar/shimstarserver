
class NetworkMessage:
	instance=None
	def __init__(self):
		self.listOfMessage=[]
		self.listOfMessageForAllUsers=[]
		
	@staticmethod
	def getInstance():
		if NetworkMessage.instance==None:
			NetworkMessage.instance=NetworkMessage()
			
		return NetworkMessage.instance
		
	def getListOfMessage(self):
		tmp=[]
		for msg in self.listOfMessage:
			tmp.append(msg)
		self.listOfMessage=[]
		return tmp

	def addMessage(self,msg):
		self.listOfMessage.append(msg)
	
	def addMessageForAllUsers(self,msg):
		self.listOfMessageForAllUsers.append(msg)
	
	def getListOfMessageForAllUsers(self):
		tmp=[]
		for msg in self.listOfMessageForAllUsers:
			tmp.append(msg)
		self.listOfMessageForAllUsers=[]
		return tmp