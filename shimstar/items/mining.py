import os, sys
import xml.dom.minidom
from shimstar.core.constantes import *
from shimstar.bdd.dbconnector import *
from shimstar.items.item import *


class Mining(ShimItem):
    def __init__(self, id, template=0):
        self.maxHitpoints = 0
        self.nb = 0
        self.distance = 0
        self.lastTicks = 0
        super(Mining, self).__init__(id, template)
        super(Mining, self).loadFromBdd()
        self.loadFromTemplate()


    def loadFromTemplate(self):
        query = "SELECT star055_nb,star055_range"
        query += " FROM star004_item_template IT"
        query += " join star055_mining_item w on w.star055_id = IT.star004_specific_starxxx "
        query += "WHERE IT.star004_id = '" + str(self.template) + "'"
        # ~ print query
        shimDbConnector.lock.acquire()
        instanceDbConnector = shimDbConnector.getInstance()

        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()
        for row in result_set:
            self.nb = int(row[0])
            self.distance = int(row[1])
        cursor.close()
        shimDbConnector.lock.release()

        super(Mining, self).loadFromTemplate()


    def getNb(self):
        return self.nb

    def getDistance(self):
        return self.distance

