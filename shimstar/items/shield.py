import os, sys
import xml.dom.minidom
from shimstar.core.constantes import *
from shimstar.bdd.dbconnector import *
from shimstar.items.item import *


class Shield(ShimItem):
    def __init__(self, id, template=0):
        self.maxHitpoints = 0
        self.tempo = 0
        self.hitpoints = 0
        self.lastTicks = 0
        super(Shield, self).__init__(id, template)
        super(Shield, self).loadFromBdd()
        self.loadFromTemplate()


    def loadFromTemplate(self):
        query = "SELECT star067_hitpoints,star067_reload_tempo"
        query += " FROM star004_item_template IT"
        query += " join star067_shield w on w.star067_id = IT.star004_specific_starxxx "
        query += "WHERE IT.star004_id = '" + str(self.template) + "'"
        # ~ print query
        shimDbConnector.lock.acquire()
        instanceDbConnector = shimDbConnector.getInstance()

        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()
        for row in result_set:
            self.tempo = int(row[1])
            self.maxHitpoints = int(row[0])
        cursor.close()
        shimDbConnector.lock.release()

        super(Shield, self).loadFromTemplate()


    def getHitPoints(self):
        return self.maxHitpoints

    def setActualHitPoints(self , hp):
        self.hitpoints = hp

    def getActualHitPoints(self):
        return self.hitpoints

    def getAcceleration(self):
        return self.tempo
				
    def takeDamage(self,hp):
        self.hitpoints-=hp
        self.hitpoints = self.hitpoints if self.hitpoints>0 else 0

    def run(self):
        if self.hitpoints<self.maxHitpoints:
            dt = globalClock.getRealTime() - self.lastTicks
            if dt >= 1:
                self.hitpoints += self.tempo
                self.hitpoints = self.hitpoints if self.hitpoints <= self.maxHitpoints else self.maxHitpoints
