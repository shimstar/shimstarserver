import direct.directbase.DirectStart
from panda3d.core import BitMask32

from direct.showbase.DirectObject import DirectObject
from panda3d.bullet import *
import os, sys
from shimstar.bdd.dbconnector import *


class Asteroid(DirectObject):
    className = "asteroid"
    listOfAsteroid = {}

    def __init__(self, idasteroid, world, worldNP):
        self.id = idasteroid
        self.bodyNP = None
        self.text = ""
        self.mass = 0
        self.minerals = {}
        self.idTemplate = 0
        self.world = world
        self.worldNP = worldNP
        self.loadAsteroidFromBdd(world, worldNP)
        Asteroid.listOfAsteroid[self.id] = self

    def getNode(self):
        return self.node

    @staticmethod
    def getAsteroid(id):
        if Asteroid.listOfAsteroid.has_key(id) == True:
            return Asteroid.listOfAsteroid[id]
        return None

    def getScale(self):
        return self.scale

    def getId(self):
        return self.id

    def destroy(self):
        if self.bodyNP != None:
            if self.world is not None:
                self.world.removeRigidBody(self.bodyNP.node())
            self.bodyNP.detachNode()
            self.bodyNP.removeNode()

    def loadAsteroidFromBdd(self, world, worldNP):
        query = "SELECT star014_zone_star011, star014_posx, star014_posy, star014_posz, star014_hprh,star014_hprp,star014_hprr, star013_egg, star013_mass,star014_template_star013"
        query += " FROM star014_asteroid A1 JOIN star013_asteroid_template A2 on A1.star014_template_star013 = A2.star013_id "
        query += " WHERE A1.star014_id = '" + str(self.id) + "'"
        shimDbConnector.lock.acquire()
        instanceDbConnector = shimDbConnector.getInstance()

        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()
        for row in result_set:
            self.zoneId = row[0]
            self.pos = (float(row[1]), float(row[2]), float(row[3]))
            self.hpr = (float(row[4]), float(row[5]), float(row[6]))
            egg = row[7]
            self.mass = row[8]
            self.idTemplate = int(row[9])
            visNP = loader.loadModel(egg)
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

        query = "SELECT STAR058_idmineral_star004, star058_nb from star058_ast_mineral where star058_idast_star013 = '" + str(
            self.idTemplate) + "'"
        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()
        for row in result_set:
            self.minerals[int(row[0])] = int(row[1])

            # ~ print self.minerals
        cursor.close()
        shimDbConnector.lock.release()

    def getMinerals(self):
        return self.minerals

    def collectByIdMineral(self, id, nb):
        if self.minerals.has_key(id) == True:
            self.minerals[id] -= nb

    def getPos(self):
        return self.bodyNP.getPos()

    def getHpr(self):
        return self.bodyNP.getHpr()

    def getObj(self):
        return self.bodyNP

    def getName(self):
        return self.name

    def getText(self):
        return self.text

    def setName(self, name):
        self.name = name
        self.bodyNP.setName(self.name)
