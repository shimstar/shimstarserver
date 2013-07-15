from pandac.PandaModules import *

from math import sqrt

def calcDistance(node1,node2):
		pos1=node1.getPos()
		pos2=node2.getPos()
		dx=pos1.getX()-pos2.getX()
		dy=pos1.getY()-pos2.getY()
		dz=pos1.getZ()-pos2.getZ()
		distance=int(round(sqrt(dx*dx+dy*dy+dz*dz),0))
		return distance