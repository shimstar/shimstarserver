from shimstar.core.constantes import *
from shimstar.bdd.dbconnector import *

from pandac.PandaModules import Point3, Vec3, Vec4
from pandac.PandaModules import *
from panda3d.bullet import *

class ItemInSpace:
    listItem=[]
    def __init__(self,id=0,idTemplate=0):
        self.pos = (0,0,0)
        self.hpr = (0,0,0)
        self.id = id
        self.templateId = idTemplate
        self.mass = 0
        self.zoneId = 0
        self.img = ""
        self.name = ""
        self.scale = 1
        self.typeItem = ""
        self.egg = ""
        self.eggMiddle = ""
        self.eggFar = ""
        self.hullpoints = 0
        self.maxHullpoints = 0
        self.bodyNP = None
        self.world = None
        self.worldNP = None

        if self.id > 0:
            self.loadFromBdd()
        else:
            self.loadTemplateFromBdd()

        ItemInSpace.listItem.append(self)

    @staticmethod
    def getListItemInSpace():
        return ItemInSpace.listItem

    def loadEgg(self, world, worldNP):
        self.world = world
        self.worldNP = worldNP
        visNP = loader.loadModel(self.egg)

        geom = visNP.findAllMatches('**/+GeomNode').getPath(0).node().getGeom(0)
        shape = BulletConvexHullShape()
        shape.addGeom(geom)
        body = BulletRigidBodyNode(self.name)
        self.bodyNP = worldNP.attachNewNode(body)
        self.bodyNP.node().addShape(shape)
        self.bodyNP.node().setMass(self.masse)
        self.bodyNP.setPos(self.pos)
        self.bodyNP.setHpr(self.hpr)
        self.bodyNP.setCollideMask(BitMask32.allOn())
        self.bodyNP.setPythonTag("obj", self)
        self.bodyNP.setPythonTag("pnode", visNP)
        self.world.attachRigidBody(self.bodyNP.node())
        visNP.reparentTo(self.bodyNP)

    def getHullPoints(self):
        return self.hullpoints

    def getMaxHullPoints(self):
        return self.maxHullpoints

    def sendInfo(self,nm):
        nm.addUInt(self.id)
        nm.addUInt(self.template)
        nm.addUInt(self.hullpoints)
        if self.bodyNP is not None and  not self.bodyNP.isEmpty():
            nm.addFloat(self.bodyNP.getPos().getX())
            nm.addFloat(self.bodyNP.getPos().getY())
            nm.addFloat(self.bodyNP.getPos().getZ())
            nm.addFloat(self.bodyNP.getQuat().getR())
            nm.addFloat(self.bodyNP.getQuat().getI())
            nm.addFloat(self.bodyNP.getQuat().getJ())
            nm.addFloat(self.bodyNP.getQuat().getK())
        else:
            nm.addFloat(0)
            nm.addFloat(0)
            nm.addFloat(0)
            nm.addFloat(0)
            nm.addFloat(0)
            nm.addFloat(0)
            nm.addFloat(0)

    def destroy(self):
        if self.bodyNP is not None:
            if self.world is not None:
                self.world.removeRigidBody(self.bodyNP.node())
            self.bodyNP.detachNode()
            self.bodyNP.removeNode()

        if self in ItemInSpace.listItem:
            ItemInSpace.listItem.remove(self)


    def setZoneId(self,zoneid):
        self.zoneId = zoneid

    def setPos(self,pos):
        self.pos=pos

    def setHpr(self,hpr):
        self.hpr=hpr

    def getPos(self):
        if self.bodyNP is not None and  not self.bodyNP.isEmpty():
            return self.bodyNP.getPos()
        return self.pos

    def getQuat(self):
        if self.bodyNP is not None and  not self.bodyNP.isEmpty():
            return self.bodyNP.getQuat()
        return None

    def loadFromBdd(self):
        query="SELECT star068_posx,star068_posy,star068_posz,star068_hprh,star068_hprp,star068_hprr, star068_scale, star068_template_star069,star068_zone_star011"
        query+=" ,star069_name, star069_type_star003,star069_img, star069_masse,star069_egg,star069_egg_middle,star069_egg_far"
        query+=" , star068_hullpoints, star069_hullpoints"
        query+=" FROM star068_iteminspace join star069_iteminspace_template on star068_template_star004 = star069_id"
        query+=" WHERE star068_id = " + str(self.id)

        shimDbConnector.lock.acquire()
        instanceDbConnector=shimDbConnector.getInstance()

        cursor=instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall ()
        for row in result_set:
            self.pos=(float(row[0]),float(row[1]),float(row[2]))
            self.hpr=(float(row[3]),float(row[4]),float(row[5]))
            self.scale = float(row[6])
            self.scale = float(row[7])
            self.templateId = int(row[7])
            self.zoneId = int(row[8])
            self.name = row[9]
            self.typeItem = int(row[10])
            self.img = row[11]
            self.masse = int(row[12])
            self.egg = row[13]
            self.eggMiddle = row[14]
            self.eggFar = row[15]
            self.hullpoints = int(row[16])
            self.maxHullpoints = int(row[17])
        cursor.close()
        shimDbConnector.lock.release()

    def loadFromTemplate(self):
        query = "SELECT star069_name, star069_type_star003,star069_img, star069_masse,star069_egg,star069_egg_middle,star069_egg_far,star069_scale,star069_hullpoints"
        query+= " from star069_iteminspace_template "
        query+= " where star069_id = " + str(self.templateId)
        shimDbConnector.lock.acquire()
        instanceDbConnector=shimDbConnector.getInstance()

        cursor=instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall ()
        for row in result_set:
            self.name = row[0]
            self.typeItem = int(row[1])
            self.img = row[2]
            self.masse = int(row[3])
            self.egg = row[4]
            self.eggMiddle = row[5]
            self.eggFar = row[6]
            self.scale = float(row[7])
            self.hullpoints = int(row[8])
            self.maxHullpoints = int(row[8])

        cursor.close()
        shimDbConnector.lock.release()

    def delete(self):
        query = "DELETE FROM star068_iteminspace WHERE STAR068_id ='" + str(self.id) + "'"
        shimDbConnector.lock.acquire()
        instanceDbConnector = shimDbConnector.getInstance()
        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        cursor.close()
        shimDbConnector.lock.release()


    def saveToBDD(self):
        shimDbConnector.lock.acquire()
        if self.id == 0:
            query = "INSERT INTO star068_iteminspace (star068_posx,star068_posy,star068_posz,star068_hprh,star068_hprp,star068_hprr"
            query += " ,star068_scale, star068_template_star069,star068_zone_star011)"
            query += " values ('" + str(self.pos.getX()) + "','" + str(self.pos.getX())+ "','" + str(self.pos.getY()) + "','" + str(self.pos.getZ())
            query += + "','" + str(self.hpr.getH()) + "','" + str(self.hpr.getP()) + "','" + str(self.hpr.getR())
            query += " ','" +str(self.scale) + "','" + str(self.templateId) + "','" + str(self.zoneId) + "')"
        else:
            query = "UPDATE star068_iteminspace SET star068_posx='" + str(self.pos.getX())
            query += ",star068_posy =  "+ str(self.pos.getY())
            query += ",star068_posz =  "+ str(self.pos.getZ())
            query += ",star068_hprh = " + str(self.hpr.getH())
            query += ",star068_hprp = " + str(self.hpr.getP())
            query += ",star068_hprr = " + str(self.hpr.getR())
            query += ",star068_hullpoints " + str(self.hullpoints)
            query += " WHERE STAR006_id='" + str(self.id) + "'"
        instanceDbConnector = shimDbConnector.getInstance()
        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        if self.id == 0:
            self.id = int(cursor.lastrowid)
        cursor.close()

        instanceDbConnector.commit()
        shimDbConnector.lock.release()


