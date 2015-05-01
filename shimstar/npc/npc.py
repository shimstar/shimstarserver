import shimstar.core.constantes
from shimstar.bdd.dbconnector import *
from pandac.PandaModules import Vec3
import os, sys
import os.path
import xml.dom.minidom
from shimstar.npc.intelligence.attitude import *
from shimstar.items.ship import *


class NPC(threading.Thread):
    listOfNpc = {}
    lock=threading.Lock()

    def __init__(self, id=0, idtemplate=0, zone=0):
        print "NPC::__init__" + str(id) + "/" + str(idtemplate)
        self.zone = zone
        self.ship = None
        self.className = "npc"
        self.template = idtemplate
        self.id = id
        self.idEvent = 0
        self.faction = 0
        self.attitude = Attitude(self)

        if self.id != 0:
            self.loadFromBDD()
        else:
            self.loadTemplateFromBDD()

        NPC.listOfNpc[self.id] = self

    def getId(self):
        return self.id

    def sendInfo(self, nm):
        nm.addInt(self.id)
        nm.addString(self.name)
        nm.addInt(self.template)
        self.ship.sendInfo(nm)

    def getClassName(self):
        return "NPC"

    def runPhysics(self):
        if self.attitude is not None:
            self.attitude.run()
            self.attitude.runPhysics()

    def getPos(self):
        return self.ship.getPos()

    def getQuat(self):
        return self.ship.getQuat()

    def getShip(self):
        return self.ship

    def loadFromBDD(self):
        query = "SELECT star034_name,star034_zone_star011zone,star034_template_star035,star034_event_star047,star034_faction_star059 FROM star034_npc WHERE star034_id='" + str(
            self.id) + "'"
        shimDbConnector.lock.acquire()
        instanceDbConnector = shimDbConnector.getInstance()
        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()
        for row in result_set:
            self.name = row[0]
            self.template = int(row[2])
            self.idEvent = int(row[3])
            self.faction = int(row[4])
        cursor.close()
        shimDbConnector.lock.release()
        self.loadShipFromBDD()

    def loadTemplateFromBDD(self):
        query = "SELECT star035_ship_star005,star035_name,star035_id_behaviour,star035_id_zone_behaviour_star011,star011_name,star035_id_faction_star059 "
        query += " FROM star035_npc_template JOIN star011_zone ON star035_id_zone_behaviour_star011 = star011_id WHERE star035_id='" + str(
            self.template) + "'"
        shimDbConnector.lock.acquire()
        instanceDbConnector = shimDbConnector.getInstance()
        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()
        for row in result_set:
            self.ship = Ship(0, int(row[0]))
            self.name = row[1]
            idbehav = row[2]
            zoneName = row[4]
            self.faction = int(row[5])
        cursor.close()
        shimDbConnector.lock.release()
        self.ship.loadEgg(self.zone.world, self.zone.worldNP)
        self.attitude.loadBehavior(idbehav, zoneName)


    def loadShipFromBDD(self):
        query = "SELECT star007_id FROM star007_ship ship JOIN  star006_item item ON item.star006_id=ship.star007_item_star006 "
        query += " WHERE star007_fitted=1 and  star006_container_starnnn='" + str(
            self.id) + "' AND star006_containertype='star034_npc'"
        shimDbConnector.lock.acquire()
        instanceDbConnector = shimDbConnector.getInstance()
        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()
        for row in result_set:
            self.ship = Ship(int(row[0]))
        cursor.close()
        shimDbConnector.lock.release()
        if self.ship is not None:
            self.ship.setOwner(self)


    def saveToBDD(self):
        if self.id == 0:
            query = "insert into star034_npc (star034_zone_star011zone,star034_name,star034_template_star035,star034_event_star047,star034_faction_star059)"
            query += " values ('" + str(self.zone.id) + "','" + self.name + "','" + str(self.template) + "','" + str(
                self.idEvent) + "','" + str(self.faction) + "')"
            shimDbConnector.lock.acquire()
            instanceDbConnector = shimDbConnector.getInstance()
            cursor = instanceDbConnector.getConnection().cursor()
            cursor.execute(query)
            if self.id == 0:
                self.id = cursor.lastrowid
            cursor.close()
        shimDbConnector.getInstance().commit()
        shimDbConnector.lock.release()
        self.ship.setOwner(self)
        self.ship.saveToBDD()
        self.saveToXml()

    def loadXml(self):
        if os.path.exists("./config/npc/npc" + str(self.id) + ".xml"):
            dom = xml.dom.minidom.parse("./config/npc/npc" + str(self.id) + ".xml")
            pp = dom.getElementsByTagName('patrolpoint')
            beh = self.attitude.setBehavior(C_BEHAVIOR_PATROL)
            for p in pp:
                pos = p.firstChild.data
                tabpos = pos.split(",")
                beh.addPatrolPoint(Vec3(float(tabpos[0]), float(tabpos[1]), float(tabpos[2])))
            # self.faction = int(dom.getElementsByTagName('faction')[0].firstChild.data)
            atti = dom.getElementsByTagName('attitude')
            for a in atti:
                typeAtti = int(a.getElementsByTagName('typeattitude')[0].firstChild.data)
                lvlAtti = int(a.getElementsByTagName('levelattitude')[0].firstChild.data)
                factionAtti = int(a.getElementsByTagName('faction')[0].firstChild.data)
                self.attitude.addAttitude(typeAtti, lvlAtti, factionAtti)


    def saveToXml(self):
        docXml = xml.dom.minidom.Document()
        npcXml = docXml.createElement("npc")
        idXml = docXml.createElement("id")
        idXml.appendChild(docXml.createTextNode(str(self.id)))

        for a in self.attitude.getAttitude():
            attitudeXml = docXml.createElement("attitude")
            typeAttiXml = docXml.createElement("typeattitude")
            typeAttiXml.appendChild(docXml.createTextNode(str(a.getTypeAttitude())))
            lvlAttiXml = docXml.createElement("levelattitude")
            lvlAttiXml.appendChild(docXml.createTextNode(str(a.getLevel())))
            factionXml = docXml.createElement("faction")
            factionXml.appendChild(docXml.createTextNode(str(a.getFaction())))
            attitudeXml.appendChild(typeAttiXml)
            attitudeXml.appendChild(lvlAttiXml)
            attitudeXml.appendChild(factionXml)
            npcXml.appendChild(attitudeXml)

        behaviors = self.attitude.getBehaviors()
        for bId in behaviors:
            b = behaviors[bId]
            if isinstance(b, behaviorPatrol):
                patrolsXml = docXml.createElement("patrol")
                pp = b.getPatrolPoints()
                for p in pp:
                    patrolXml = docXml.createElement("patrolpoint")
                    patrolXml.appendChild(docXml.createTextNode(
                        str(p.getPos().getX()) + "," + str(p.getPos().getY()) + "," + str(p.getPos().getZ())))
                    patrolsXml.appendChild(patrolXml)
                npcXml.appendChild(patrolsXml)
        npcXml.appendChild(idXml)
        docXml.appendChild(npcXml)
        fileHandle = open("./config/npc/npc" + str(self.id) + ".xml", 'w')
        fileHandle.write(docXml.toxml())
        fileHandle.close()


    @staticmethod
    def getNPC(id):
        # ~ print str(npc.listOfNpc.keys()) + " searching for " + str(id)
        if NPC.listOfNpc.has_key(id):
            return NPC.listOfNpc[id]
        else:
            return None