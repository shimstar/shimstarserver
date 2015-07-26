import os, sys
import xml.dom.minidom
from shimstar.core.constantes import *
from shimstar.bdd.dbconnector import *
from shimstar.items.item import *

class Reactor(ShimItem):
	def __init__(self,id,template=0):
		self.energy=0
		super(Reactor,self).__init__(id,template)
		super(Reactor,self).loadFromBdd()
		self.loadFromTemplate()
					
	def loadFromTemplate(self):
		query="SELECT star016_energy"
		query+=" FROM star004_item_template IT"
		query+=" join star016_reactor w on w.star016_id = IT.star004_specific_starxxx "
		query+="WHERE IT.star004_id = '" +str(self.template) + "'"
		#~ print query
		shimDbConnector.lock.acquire()
		instanceDbConnector=shimDbConnector.getInstance()

		cursor=instanceDbConnector.getConnection().cursor()
		cursor.execute(query)
		result_set = cursor.fetchall ()
		for row in result_set:
			self.energy=int(row[0])
		cursor.close()
		shimDbConnector.lock.release()
		
		super(Reactor,self).loadFromTemplate()
				
	def getEnergy(self):
		return self.energy

