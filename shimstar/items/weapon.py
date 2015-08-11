import os, sys
import xml.dom.minidom
from shimstar.items.bullet import *
from shimstar.core.constantes import *
from shimstar.bdd.dbconnector import *
from shimstar.items.item import *


class Weapon(ShimItem):
    def __init__(self, id, template=0):
        super(Weapon, self).__init__(id, template)
        self.range = 0
        self.damage = 0
        self.bullets = []
        self.cadence = 0
        self.lastShot = 0
        self.speed = 0
        self.place = 0
        self.egg = None
        self.mission = 0
        self.zone = 0
        self.ship = None
        self.loadFromTemplate()
        self.world = None
        self.worldNP = None

    def setShip(self, ship):
        self.ship = ship
        self.world = ship.world
        self.worldNP = ship.worldNP


    def getShip(self):
        return self.ship

    def getBullets(self):
        return self.bullets

    def getSpeed(self):
        return self.speed


    def shot(self, pos, quat, ship, name=None):
        """
            receiving shot command. Test if the time elapsed is enough depending of the cadence of shot of the weapon.
            Return the bullet created, otherwise None
        """
        if globalClock.getRealTime() - self.lastShot > self.cadence:
            self.lastShot = globalClock.getRealTime()
            bul = Bullet(pos, quat, self.egg, self.range, self.speed, self.slot.x, self.slot.y,self.slot.z)
            self.lastShot = globalClock.getRealTime()
            self.bullets.append(bul)
            return bul
        else:
            return None

    def getDamage(self):
        return self.damage

    def getId(self):
        return self.id

    def setZone(self, zone):
        self.zone = zone

    def addBullet(self, pos, quat):
        bul = Bullet(pos, quat, self.egg, self.range, self.speed, self,self.slot.x,self.slot.y,self.slot.z)
        self.bullets.append(bul)
        return bul

    def loadFromTemplate(self):
        query = "SELECT star018_damage,star018_range,star018_egg,star018_cadence,star018_speed"
        query += " FROM star004_item_template IT join star018_weapon w on w.star018_id = IT.star004_specific_starxxx "
        query += "WHERE IT.star004_id = '" + str(self.template) + "'"
        shimDbConnector.lock.acquire()
        instanceDbConnector = shimDbConnector.getInstance()

        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()
        for row in result_set:
            self.range = int(row[1])
            self.damage = int(row[0])
            self.egg = str(row[2])
            self.cadence = float(row[3])
            self.speed = int(row[4])
        cursor.close()
        shimDbConnector.lock.release()
        super(Weapon, self).loadFromTemplate()

    def getRange(self):
        return self.range
				
