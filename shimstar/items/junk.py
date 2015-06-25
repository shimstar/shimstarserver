import os, sys
import random
from pandac.PandaModules import Point3, Vec3, Vec4
from shimstar.bdd.dbconnector import *


class junk:
    numberOfJunk = 0
    junks = []

    def __init__(self, id, pos=Vec3(0, 0, 0), zone=0, idTemplate=0, items=None):
        self.idTemplate = idTemplate
        self.id = id
        self.name = ""
        self.egg = ""
        self.pos = pos
        self.hpr = (0, 0, 0)
        self.node = None
        self.items = {'toto': 'toti'}
        self.items.clear()
        self.zone = zone
        self.loadFromBdd()
        self.name = self.name + str(junk.numberOfJunk)

        junk.numberOfJunk += 1
        junk.junks.append(self)


    def saveToBDD(self):
        """
            save junk to BDD
        """
        instanceDbConnector = shimDbConnector.getInstance()
        if self.id == 0:
            query = "INSERT INTO STAR015_JUNK (star015_zone_star011,star015_posx,star015_posy,star015_posz)"
            query += " VALUES('" + str(self.zone) + "','" + str(self.pos.getX()) + "','" + str(
                self.pos.getY()) + "','" + str(self.pos.getZ()) + "')"
            instanceDbConnector = shimDbConnector.getInstance()
            cursor = instanceDbConnector.getConnection().cursor()
            cursor.execute(query)
            self.id = int(cursor.lastrowid)
            cursor.close()

        for tabItems in self.items:
            for i in self.items[tabItems]:
                query = "UPDATE STAR006_item "
                query += " set star006_container_starnnn='" + str(self.id) + "',"
                query += " star006_owner_star001 ='" + str(i.getOwner()) + "',"
                query += " star006_containertype ='star015_junk'"
                query += " WHERE star006_id='" + str(i.getId()) + "'"
                cursor = instanceDbConnector.getConnection().cursor()
                cursor.execute(query)
                cursor.close()
                # ~ print query

    def deleteFromBdd(self):
        instanceDbConnector = shimDbConnector.getInstance()
        query = "delete from star015_junk where star015_id = '" + str(self.id) + "'"
        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        cursor.close()

    def loadFromBdd(self):
        """
            load Junk From BDD
        """
        query = "SELECT star015_zone_star011,star015_posx,star015_posy,star015_posz, star015_hprh,star015_hprp,star015_hprr"
        query += " FROM  star015_junk "
        query += " WHERE  star015_id ='" + str(self.id) + "'"
        instanceDbConnector = shimDbConnector.getInstance()

        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()
        for row in result_set:
            self.zone = int(row[0])
            self.pos = (Vec3(float(row[1]), float(row[2]), float(row[3])))
            self.hpr = (Vec3(float(row[4]), float(row[5]), float(row[6])))
        cursor.close()

        query = "SELECT star006_id FROM STAR006_item"
        query += " WHERE star006_containertype='star015_junk' and star006_container_starnnn='" + str(self.id) + "'"

        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()
        for row in result_set:
            temp = ShimstarItem(int(row[0]))
            if self.items.has_key(temp.getOwner()) != True:
                self.items[temp.getOwner()] = []
            self.items[temp.getOwner()].append(temp)
        cursor.close()

    def getId(self):
        return self.id

    def getIdTemplate(self):
        return self.idTemplate

    def getZone(self):
        return self.zone

    def setZone(self, zoneId):
        self.zone = zoneId

    @staticmethod
    def getJunk(id):
        for j in junk.junks:
            if j.id == id:
                return j
        return None

    def populateFromShip(self, pShip):
        """
            params:
                ship
            This method create a junk from a ship. It uses damageHistory to populate the items, and attributes items for each player.
        """
        self.saveToBDD()  # allow to generate self.id
        items = []
        items.extend(pShip.getItems())
        items.extend(pShip.getInventory())
        damageHistory = pShip.getDamageHistory()
        usrCh = ""
        totalDamage = 0
        for u in damageHistory.keys():
            totalDamage += damageHistory[u]

        quadrant = 0
        userPrcent = {}

        for u in damageHistory.keys():
            prcent = int(damageHistory[u] / totalDamage * 100)
            quadrant += prcent
            userPrcent[quadrant] = u
        for ite in items:
            alea = random.randint(1, 100)
            choice = None
            for u in userPrcent.keys():
                if u <= 100 and alea <= u:
                    choice = u

            if choice is not None:
                if self.items.has_key(userPrcent[choice]) != True:
                    self.items[userPrcent[choice]] = []
                self.items[userPrcent[choice]].append(ite)
                ite.setOwner(userPrcent[choice])
                ite.setContainer(self.id)
        self.saveToBDD()

    def removeItem(self, typeItem, idItem):
        """
            Remove an item from the junk
            If there is no more item, the function return True in the aim to destroy the junk
        """
        for usr in self.items.keys():
            for it in self.items[usr]:
                if str(it.getTypeItem()) == typeItem and str(it.getId()) == idItem:
                    self.items[usr].remove(it)
                    break

        itemNb = 0
        for usr in self.items.keys():
            for it in self.items[usr]:
                itemNb += 1

        if itemNb == 0:
            return True
        else:
            return False

    def getItems(self):
        return self.items

    def getName(self):
        return self.name

    def getId(self):
        return self.id

    def getPos(self):
        return self.pos

    def destroy(self):
        """
            destructor
        """
        self.deleteFromBdd()
        if self.node != None:
            self.node.detachNode()
            self.node.removeNode()
        del junk.junks[self]

    def sendPos(self,nm,idUser):
        nm.addFloat(self.pos.getX())
        nm.addFloat(self.pos.getY())
        nm.addFloat(self.pos.getZ())
        nbItemForUser=0
        listOfItem=[]
        for usr in self.items.keys():
            if usr==idUser:
                nbItemForUser+=1
                listOfItem.append(self.items[user])

        nm.addInt(nbItemForUser)
        for it in listOfItem:
            nm.addInt(it.getTypeItem())
            nm.addInt(it.getTemplate())
            nm.addInt(it.getId())

        return nm

    def mustSendToUser(self,idUser):
        for usr in self.items.keys():
            if usr==idUser:
                return True

        return False