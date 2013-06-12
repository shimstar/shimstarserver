# -*- coding:cp1252 -*-
try: import psyco;psyco.full()
except:pass

import os, sys
from sys import argv
from string import *

myPath=".\\"

nbline=0

def nbLine(directory):	
	nbline=0
	for files in os.listdir(directory):
		nblinefic=0
		if files!="compte.py":
				if os.path.isfile(directory + files):
					if files[len(files)-3:]==".py":
						f=open(directory +files,'r')
						line=f.readline()
						while line:						
							line=f.readline()
							if(len(strip(line))>0):
								nbline+=1
								nblinefic+=1
						f.close()
						print files + " contient " + str(nblinefic) + " lignes de code"
				elif os.path.isdir(directory + files):
						if files!="." and files!="..":
							nbline+=nbLine(directory + files + "\\")
	return nbline

nbline+=nbLine(myPath)

print "***************"
print "Le nombre de lignes total est " + str(nbline)