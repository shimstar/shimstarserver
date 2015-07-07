from pandac.PandaModules import Point3, Vec3, Vec4
from pandac.PandaModules import *
from panda3d.bullet import *
from math import sqrt
from direct.stdpy import threading
from shimstar.core.constantes import *


class Bullet(threading.Thread):
    nbBullet = 0
    listOfBullet = {}
    lock = threading.Lock()

    def __init__(self, pos, quat, egg, range, speed, weapon):
        # ~ print "bullet::__init__"
        threading.Thread.__init__(self)
        self.id = Bullet.nbBullet
        Bullet.nbBullet += 1
        self.weapon = weapon
        self.range = range
        self.speed = speed
        self.lastSentTicks = 0
        self.worldNP = self.weapon.worldNP
        self.world = self.weapon.world
        visNP = loader.loadModel("models/" + egg)
        geom = visNP.findAllMatches('**/+GeomNode').getPath(0).node().getGeom(0)
        shape = BulletConvexHullShape()
        shape.addGeom(geom)
        body = BulletRigidBodyNode("bullet" + str(self.id))
        self.bodyNP = self.worldNP.attachNewNode(body)
        self.bodyNP.node().addShape(shape)
        self.bodyNP.node().setMass(0.0001)
        self.bodyNP.setQuat(quat)
        pt1, pt2 = self.weapon.ship.bodyNP.getTightBounds()
        xDim = pt2.getX() - pt1.getX()
        yDim = pt2.getY() - pt1.getY()

        #~ print "bullet dims " +  str(xDim) + "/" + str(yDim)
        dim = xDim
        if xDim < yDim:
            dim = yDim
        self.bodyNP.setPos(weapon.ship.bodyNP, Vec3(0, dim + (dim / 5), 0))
        #~ self.bodyNP.setPos(weapon.ship.bodyNP,Vec3(0,200,0))
        self.initPos = self.bodyNP.getPos()
        self.bodyNP.setCollideMask(BitMask32.allOn())
        self.bodyNP.setPythonTag("obj", self)
        self.bodyNP.setPythonTag("pnode", visNP)
        self.world.attachRigidBody(self.bodyNP.node())
        visNP.reparentTo(self.bodyNP)
        forwardVec = self.bodyNP.getQuat().getForward()
        self.bodyNP.node().setLinearVelocity(
            Vec3(forwardVec.getX() * self.speed, forwardVec.getY() * self.speed, forwardVec.getZ() * self.speed))
        Bullet.listOfBullet[self.id] = self

    def mustSentPos(self, timer):
        """
         if the time elapsed between 2 messages sent to others players is over the sendticks, return true, otherwise return false
        """
        dt = (timer - self.lastSentTicks)
        if dt > C_SENDTICKS:
            self.lastSentTicks = timer
            return True
        else:
            return False

    @staticmethod
    def removeBullet(id):
        if Bullet.listOfBullet.has_key(id) == True:
            Bullet.listOfBullet[id].destroy()
            del Bullet.listOfBullet[id]

    @staticmethod
    def getBullet(id):
        """
            Static :: retrieve a bullet by its id from all current bullets
        """
        if Bullet.listOfBullet.has_key(id) == True:
            return Bullet.listOfBullet[id]
        else:
            return None

    @staticmethod
    def getBullets():
        """
            static :: get list of all bullets existing
        """
        if bullet.listOfBullet.has_key('titi'):
            bullet.listOfBullet.clear()
        return bullet.listOfBullet

    def getId(self):
        return self.id

    def getClassName(self):
        return bullet.className

    def getShipOwner(self):
        return self.weapon.ship.owner

    def getWeapon(self):
        return self.weapon

    def getDamage(self):
        return self.weapon.getDamage()

    def getPos(self):
        return self.bodyNP.getPos()

    def getQuat(self):
        return Quat(self.bodyNP.getQuat())

    def getHpr(self):
        return self.bodyNP.getHpr()

    def destroy(self):
        # print "bullet::destroy " + str(self.id)
        if self.bodyNP != None:
            if self.world is not None:
                self.world.removeRigidBody(self.bodyNP.node())
            self.bodyNP.detachNode()
            self.bodyNP.removeNode()


    def stateBullet(self):
        """
        determines if a bullet is at end of life or not
        return 1, if the bullet must be destroyed, 0 otherwise
        """
        distance = self.calcDistance()
        # ~ print "bullet:state bullezqqqqqqt " + str(self.id) + "/" +  str(distance) + "/" + str(self.range)
        if distance > self.range:
            #~ if (time-self.startTime)>self.range:
            return 1
        return 0


    def getName(self):
        return self.name


    def calcDistance(self):
        pos1 = self.initPos
        pos2 = self.bodyNP.getPos()
        dx = pos1.getX() - pos2.getX()
        dy = pos1.getY() - pos2.getY()
        dz = pos1.getZ() - pos2.getZ()
        distance = int(round(sqrt(dx * dx + dy * dy + dz * dz), 0))
        return distance
    