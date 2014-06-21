import os, sys
import xml.dom.minidom
from shimstar.core.constantes import *
from shimstar.bdd.dbconnector import *
from shimstar.items.item import *

class Mineral(ShimItem):
	def __init__(self,id,template=0):
		super(Mineral,self).__init__(id,template)	
		super(Mineral,self).loadFromBdd()
		self.loadFromTemplate()
		
	def loadFromTemplate(self):
		super(Mineral,self).loadFromTemplate()	
	
