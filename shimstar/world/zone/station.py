import os, sys

from panda3d.bullet import *
from panda3d.core import BitMask32

from shimstar.bdd.dbconnector import *


class Station:
    def __init__(self, id, world, worldNP):
        self.id = id
        self.name = ""
        self.className = "station"
        self.bodyNP = None
        self.mass = 0
        self.file = ""
        self.world = world
        self.worldNP = worldNP
        self.loadStationFromBdd(world, worldNP)

    def getId(self):
        return self.id

    def destroy(self):
        if self.bodyNP != None:
            if self.world is not None:
                self.world.removeRigidBody(self.bodyNP.node())
            self.bodyNP.detachNode()
            self.bodyNP.removeNode()


    def getClassName(self):
        return self.className

    def getName(self):
        return self.name

    def getPos(self):
        return self.bodyNP.getPos()

    def loadStationFromBdd(self, world, worldNP):
        query = "SELECT star011_name, star022_posx, star022_posy,star022_posz,star022_hprh,star022_hprp,star022_hprr,star011_egg,star022_inzone_star011,star011_typezone_star012,star022_mass "
        query += " FROM star022_station join star011_zone on star011_id = star022_zone_star011 WHERE star022_zone_star011='" + str(
            self.id) + "'"
        shimDbConnector.lock.acquire()
        instanceDbConnector = shimDbConnector.getInstance()

        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()
        for row in result_set:
            self.name = row[0]
            self.pos = (float(row[1]), float(row[2]), float(row[3]))
            self.hpr = (float(row[4]), float(row[5]), float(row[6]))
            self.egg = row[7]
            self.mass = row[10]
            self.typeZone = int(row[9])
            self.zoneId = int(row[8])
            visNP = loader.loadModel(self.egg)
            geom = visNP.findAllMatches('**/+GeomNode').getPath(0).node().getGeom(0)
            shape = BulletConvexHullShape()
            shape.addGeom(geom)
            body = BulletRigidBodyNode("ast" + str(id))
            self.bodyNP = worldNP.attachNewNode(body)
            self.bodyNP.node().addShape(shape)
            self.bodyNP.setPos(self.pos)
            self.bodyNP.setHpr(self.hpr)
            self.bodyNP.setCollideMask(BitMask32.allOn())
            self.bodyNP.setPythonTag("obj", self)
            self.bodyNP.setPythonTag("pnode", visNP)
            world.attachRigidBody(self.bodyNP.node())

            visNP.reparentTo(self.bodyNP)

        cursor.close()
        shimDbConnector.lock.release()
	

