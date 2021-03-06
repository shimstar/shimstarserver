from direct.stdpy import threading
from panda3d.bullet import *

from shimstar.zoneserver.network.netmessage import *
from shimstar.zoneserver.network.networkzonetcpserver import *
from shimstar.core.constantes import *
from shimstar.user.user import *
from shimstar.core.constantes import *
from shimstar.bdd.dbconnector import *
from shimstar.world.zone.asteroid import *
from shimstar.world.zone.station import *
from shimstar.npc.npc import *
from shimstar.items.mineral import *
from shimstar.items.junk import *

C_STEP_SIZE = 1.0 / 60.0


class Zone(threading.Thread):
    instance = None

    def __init__(self, id):
        threading.Thread.__init__(self)
        self.lockListNpc=threading.Lock()
        self.stopThread = False
        self.id = id
        self.listOfAsteroid = []
        self.listOfStation = []
        self.npc = []
        self.lastGlobalTicks = 0
        self.lastNpcSendTicks = 0
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, 0))
        self.worldNP = render.attachNewNode(self.name)

        self.loadZoneFromBdd()

    def runNewUser(self):
        tempMsg = NetworkTCPServer.getInstance().getListOfMessageById(C_NETWORK_ASKING_NPC)
        if len(tempMsg) > 0:
            for msg in tempMsg:
                netMsg = msg.getMessage()
                usrId = int(netMsg[0])
                usr = User.getUserById(usrId)
                if usr != None:
                    for temp in self.npc:
                        if temp.ship != None and temp.ship.getHullPoints() > 0:
                            nm = netMessage(C_NETWORK_NPC_INCOMING, usr.getConnexion())
                            temp.sendInfo(nm)
                            NetworkMessage.getInstance().addMessage(nm)
                    nm = netMessage(C_NETWORK_NPC_SENT, usr.getConnexion())
                    NetworkMessage.getInstance().addMessage(nm)
                NetworkTCPServer.getInstance().removeMessage(msg)

        tempMsg = NetworkTCPServer.getInstance().getListOfMessageById(C_NETWORK_ASKING_CHAR)
        if len(tempMsg) > 0:
            for msg in tempMsg:
                netMsg = msg.getMessage()
                usrId = int(netMsg[0])
                usr = User.getUserById(usrId)
                if usr != None:
                    nm = netMessage(C_NETWORK_CURRENT_CHAR_INFO, usr.getConnexion())
                    usr.sendInfoChar(nm)
                    NetworkMessage.getInstance().addMessage(nm)

                NetworkTCPServer.getInstance().removeMessage(msg)

        tempMsg = NetworkTCPServer.getInstance().getListOfMessageById(C_NETWORK_ASKING_OTHER_CHAR)
        if len(tempMsg) > 0:
            for msg in tempMsg:
                netMsg = msg.getMessage()
                usrId = int(netMsg[0])
                usr = User.getUserById(usrId)

                if usr != None:
                    for othrUsr in User.listOfUser:
                        if othrUsr != usrId:
                            nm = netMessage(C_NETWORK_CHAR_INCOMING, usr.getConnexion())
                            User.listOfUser[othrUsr].sendInfoOtherPlayer(nm)
                            NetworkMessage.getInstance().addMessage(nm)
                            nm = netMessage(C_NETWORK_CHAR_INCOMING, User.listOfUser[othrUsr].getConnexion())
                            usr.sendInfoOtherPlayer(nm)
                            NetworkMessage.getInstance().addMessage(nm)

                    nm = netMessage(C_NETWORK_CHAR_SENT, usr.getConnexion())
                    NetworkMessage.getInstance().addMessage(nm)

                NetworkTCPServer.getInstance().removeMessage(msg)

        tempMsg = NetworkTCPServer.getInstance().getListOfMessageById(C_NETWORK_ASKING_JUNK)
        if len(tempMsg) > 0:
            for msg in tempMsg:
                netMsg = msg.getMessage()
                usrId = int(netMsg[0])
                usr = User.getUserById(usrId)
                if usr != None:
                    nbJunk=0
                    idChar=usr.getCurrentCharacter().getId()
                    for tempJunk in junk.junks:
                        if tempJunk.mustSendToUser(idChar):
                            nm = netMessage(C_NETWORK_ADD_JUNK, usr.getConnexion())
                            tempJunk.sendInfo(nm,idChar)
                            NetworkMessage.getInstance().addMessage(nm)
                            nbJunk+=1

                    nm = netMessage(C_NETWORK_JUNK_SENT, usr.getConnexion())
                    NetworkMessage.getInstance().addMessage(nm)
                NetworkTCPServer.getInstance().removeMessage(msg)

    def run(self):
        while not self.stopThread:
            # print len(Bullet.listOfBullet)
            User.lock.acquire()
            # ~ print User.listOfUser
            for usr in User.listOfUser:
                usrObj = User.listOfUser[usr]
                chr = usrObj.getCurrentCharacter()
                if chr != None:
                    if chr.ship != None and chr.ship.getNode() == None and chr.ship.getState() == 0:
                        chr.ship.loadEgg(self.world, self.worldNP)

                    if chr.ship != None and chr.ship.getNode() != None and chr.ship.getNode().isEmpty() == False:
                        if chr.ship.mustSentPos(globalClock.getRealTime()) == True:
                            for u in User.listOfUser:
                                usrToSend = User.listOfUser[u]
                                # ~ nm=netMessageUDP(C_NETWORK_CHARACTER_UPDATE_POS,usrToSend.getIp(),usrToSend.getUdpPort())
                                nm = netMessage(C_NETWORK_CHARACTER_UPDATE_POS, usrToSend.getConnexion())
                                nm.addInt(usrObj.getId())
                                nm.addInt(chr.getId())
                                nm.addFloat(chr.ship.bodyNP.getQuat().getR())
                                nm.addFloat(chr.ship.bodyNP.getQuat().getI())
                                nm.addFloat(chr.ship.bodyNP.getQuat().getJ())
                                nm.addFloat(chr.ship.bodyNP.getQuat().getK())
                                nm.addFloat(chr.ship.getPos().getX())
                                nm.addFloat(chr.ship.getPos().getY())
                                nm.addFloat(chr.ship.getPos().getZ())
                                nm.addInt(chr.ship.getPoussee())
                                nm.addInt(chr.ship.getHullPoints())
                                listOfShield = chr.ship.hasItems(C_ITEM_SHIELD)
                                nm.addInt(len(listOfShield))
                                for shi in listOfShield:
                                    nm.addInt(shi.getId())
                                    nm.addInt(shi.getActualHitPoints())
                                #~ NetworkMessageUdp.getInstance().addMessage(nm)
                                NetworkMessage.getInstance().addMessage(nm)

            if globalClock.getRealTime() - self.lastNpcSendTicks > C_SENDTICKS:
                self.lastNpcSendTicks = globalClock.getRealTime()
                for u in User.listOfUser:
                    if len(self.npc) > 0:
                        NPC.lock.acquire()
                        # ~ nm=netMessageUDP(C_NETWORK_NPC_UPDATE_POS,User.listOfUser[u].getIp(),User.listOfUser[u].getUdpPort())
                        nm = netMessage(C_NETWORK_NPC_UPDATE_POS, User.listOfUser[u].getConnexion())
                        nm.addInt(len(self.npc))
                        for n in self.npc:
                            nm.addInt(n.getId())
                            nm.addFloat(n.ship.bodyNP.getQuat().getR())
                            nm.addFloat(n.ship.bodyNP.getQuat().getI())
                            nm.addFloat(n.ship.bodyNP.getQuat().getJ())
                            nm.addFloat(n.ship.bodyNP.getQuat().getK())
                            nm.addFloat(n.ship.getPos().getX())
                            nm.addFloat(n.ship.getPos().getY())
                            nm.addFloat(n.ship.getPos().getZ())
                            nm.addInt(n.ship.getHullPoints())
                            listOfShield = n.ship.hasItems(C_ITEM_SHIELD)
                            nm.addInt(len(listOfShield))
                            for itShield in listOfShield:
                                nm.addInt(itShield.getId())
                                nm.addInt(itShield.getHitPoints())
                        #~ NetworkMessageUdp.getInstance().addMessage(nm)
                        NetworkMessage.getInstance().addMessage(nm)
                        NPC.lock.release()

            User.lock.release()
            self.runPhysics()

            self.runUpdateCharShot()
            self.runUpdateChar()
            self.runBulletCollision()
            self.runNewUser()
            self.runOutUser()
            self.runJunk()
        print "thread zone is ending"

    def runJunk(self):
        tempMsg = NetworkTCPServer.getInstance().getListOfMessageById(C_NETWORK_DESTROY_JUNK)
        if len(tempMsg) > 0:
            for msg in tempMsg:
                netMsg = msg.getMessage()
                usr = int(netMsg[0])
                junkId = int(netMsg[1])
                print "Junk to Destroy "
                if User.listOfUser.has_key(usr):
                    User.lock.acquire()
                    nm = netMessage(C_NETWORK_DESTROY_JUNK, User.listOfUser[usr].getConnexion())
                    nm.addInt(junkId)
                    NetworkMessage.getInstance().addMessage(nm)

                    tempJunk = junk.getJunkById(junkId)
                    if tempJunk is not None :
                        tempJunk.destroyFromUser(User.listOfUser[usr].getCurrentCharacter().getId())
                    User.lock.release()
                NetworkTCPServer.getInstance().removeMessage(msg)

    def runOutUser(self):
        tempMsg = NetworkTCPServer.getInstance().getListOfMessageById(C_NETWORK_USER_CHANGE_ZONE)
        if len(tempMsg) > 0:
            for msg in tempMsg:
                netMsg = msg.getMessage()
                usr = int(netMsg[0])
                print "user is leaving zone " + str(usr)
                if User.listOfUser.has_key(usr):
                    User.lock.acquire()
                    for us in User.listOfUser:
                        nm = netMessage(C_NETWORK_USER_OUTGOING, User.listOfUser[us].getConnexion())
                        nm.addInt(usr)
                        NetworkMessage.getInstance().addMessage(nm)
                    User.lock.release()
                    if User.listOfUser.has_key(usr) == True:
                        print "runoutUser want destroy " + str(usr)
                        User.listOfUser[usr].destroy()
                        print "runoutUser TTT " + str(User.listOfUser)
                NetworkTCPServer.getInstance().removeMessage(msg)

    def runUpdateChar(self):
        tempMsg = NetworkTCPServer.getInstance().getListOfMessageById(C_NETWORK_CHARACTER_ADD_TO_INVENTORY_FROM_JUNK)
        if len(tempMsg) > 0:
            for msg in tempMsg:
                netMsg = msg.getMessage()
                usrId = int(netMsg[0])
                junkId = int(netMsg[1])
                itemId = int(netMsg[2])
                if User.listOfUser.has_key(usrId):
                    ch = User.listOfUser[usrId].getCurrentCharacter()
                    User.lock.acquire()
                    ship = ch.getShip()

                    junkSelected = junk.getJunkById(junkId)

                    if junkSelected is not None and ship is not None:
                        itemToTransfert = junkSelected.removeItemFromJunk(ch.getId(),itemId)
                        if itemToTransfert is not None:
                            ship.addToInventory(itemToTransfert)
                            nm = netMessage(C_NETWORK_CHARACTER_ADD_TO_INVENTORY_FROM_JUNK, User.listOfUser[usrId].getConnexion())
                            nm.addInt(usrId)
                            nm.addInt(junkId)
                            nm.addInt(itemId)
                            NetworkMessage.getInstance().addMessage(nm)
                    User.lock.release()
                NetworkTCPServer.getInstance().removeMessage(msg)


        tempMsg = NetworkTCPServer.getInstance().getListOfMessageById(C_NETWORK_START_MINING)
        if len(tempMsg) > 0:
            for msg in tempMsg:
                netMsg = msg.getMessage()
                usr = int(netMsg[0])
                if User.listOfUser.has_key(usr):
                    ch = User.listOfUser[usr].getCurrentCharacter()
                    User.lock.acquire()
                    ch.setIsMining(True)
                    for a in self.listOfAsteroid:
                        if a.getId() == int(netMsg[1]):
                            ch.setMiningAsteroid(a)
                            break
                    User.lock.release()
                NetworkTCPServer.getInstance().removeMessage(msg)

        tempMsg = NetworkTCPServer.getInstance().getListOfMessageById(C_NETWORK_STOP_MINING)
        if len(tempMsg) > 0:
            for msg in tempMsg:
                netMsg = msg.getMessage()
                usr = int(netMsg[0])
                if User.listOfUser.has_key(usr):
                    ch = User.listOfUser[usr].getCurrentCharacter()
                    User.lock.acquire()
                    ch.setIsMining(False)
                    ch.saveToBDD()
                    User.lock.release()
                NetworkTCPServer.getInstance().removeMessage(msg)

        User.lock.acquire()
        for u in User.listOfUser:
            ch = User.listOfUser[u].getCurrentCharacter()
            if ch != None:
                if ch.getIsMining() == True:
                    aste = ch.getMiningAsteroid()
                    if aste != None:
                        minerals = aste.getMinerals()
                        if len(minerals) > 0:
                            idmineral = 0
                            for i in minerals:
                                idmineral = i
                                break
                            if idmineral > 0:
                                nbMineral = ch.grabMining()
                                if nbMineral > 0:
                                    hasItem = ch.getShip().hasInInventory(idmineral)
                                    idItem = 0
                                    if hasItem != None:
                                        idItem = hasItem.getId()
                                        hasItem.setNb(hasItem.getNb() + nbMineral)
                                    else:
                                        hasItem = Mineral(0, idmineral)
                                        hasItem.setNb(nbMineral)
                                        hasItem.saveToBDD()
                                        idItem = hasItem.getId()
                                        ch.getShip().addToInventory(hasItem)
                                    nm = netMessage(C_NETWORK_CHARACTER_ADD_TO_INVENTORY,
                                                    User.listOfUser[u].getConnexion())
                                    nm.addInt(C_ITEM_MINERAL)
                                    nm.addInt(idmineral)
                                    nm.addInt(idItem)
                                    nm.addInt(nbMineral)
                                    NetworkMessage.getInstance().addMessage(nm)

        User.lock.release()

    def runBulletCollision(self):

        Bullet.lock.acquire()
        bulletToRemove = []
        for b in Bullet.listOfBullet:
            if Bullet.listOfBullet[b].stateBullet() == 1:
                bulletToRemove.append(b)

            result = self.world.contactTest(Bullet.listOfBullet[b].bodyNP.node())
            for contact in result.getContacts():
                node1 = contact.getNode1()
                objCollided = contact.getNode1().getPythonTag("obj")
                # ~ print objCollided
                if isinstance(objCollided, Station) == True:
                    for u in User.listOfUser:
                        nm = netMessage(C_NETWORK_EXPLOSION_SHIELD, User.listOfUser[u].getConnexion())
                        pos = Bullet.listOfBullet[b].getPos()
                        nm.addFloat(pos.getX())
                        nm.addFloat(pos.getY())
                        nm.addFloat(pos.getZ())
                        NetworkMessage.getInstance().addMessage(nm)
                    bulletToRemove.append(b)
                elif isinstance(objCollided, Asteroid) == True:
                    for u in User.listOfUser:
                        nm = netMessage(C_NETWORK_EXPLOSION, User.listOfUser[u].getConnexion())
                        pos = Bullet.listOfBullet[b].getPos()
                        nm.addFloat(pos.getX())
                        nm.addFloat(pos.getY())
                        nm.addFloat(pos.getZ())
                        NetworkMessage.getInstance().addMessage(nm)
                    bulletToRemove.append(b)
                elif isinstance(objCollided, Ship) == True:
                    objCollided.takeDamage(Bullet.listOfBullet[b].getDamage(), Bullet.listOfBullet[b].getShipOwner(),
                        isinstance(Bullet.listOfBullet[b].getShipOwner(), character))
                    # User.lock.acquire()
                    # for u in User.listOfUser:
                    #     # ~ print "zone::run collision " + str(isinstance(objCollided.getOwner(),Character))
                    #     if isinstance(objCollided.getOwner(), character) != True:
                    #         nm = netMessage(C_NETWORK_TAKE_DAMAGE_NPC, User.listOfUser[u].getConnexion())
                    #     else:
                    #         nm = netMessage(C_NETWORK_TAKE_DAMAGE_CHAR, User.listOfUser[u].getConnexion())
                    #     #~ print "zone::run objCollided.getOwner.getID == " + str(objCollided.getOwner().getId())
                    #     nm.addInt(objCollided.getOwner().getId())
                    #     send hitpoints, and send hitpoints per shield
                    #     nm.addInt(Bullet.listOfBullet[b].getDamage())
                    #     nm.addInt(objCollided.getHullPoints())
                    #     listOfShield = objCollided.hasItems(C_ITEM_SHIELD)
                    #     nm.addInt(len(listOfShield))
                    #     for sh in listOfShield:
                    #         nm.addInt((sh.getId()))
                    #         nm.addFloat((sh.))
                    #     NetworkMessage.getInstance().addMessage(nm)
                    #
                    # User.lock.release()
                    if objCollided.getHullPoints() <= 0:
                        tempJunk=junk(0,objCollided.getPos(),self.id,4)
                        tempJunk.populateFromShip(objCollided)
                        User.lock.acquire()
                        for u in User.listOfUser:
                            # ~ print "zone::run collision " + str(isinstance(objCollided.getOwner(),character))
                            if isinstance(objCollided.getOwner(), character) != True:
                                nm = netMessage(C_NETWORK_REMOVE_NPC, User.listOfUser[u].getConnexion())
                                self.lockListNpc.acquire()
                                if objCollided.getOwner() in self.npc:
                                    self.npc.remove(objCollided.getOwner())
                                objCollided.getOwner().destroy()
                                self.lockListNpc.release()
                            else:
                                if objCollided.getOwner().getId() == User.listOfUser[u].getCurrentCharacter().getId():
                                    nm2 = netMessage(C_NETWORK_DEATH_CHAR, User.listOfUser[u].getConnexion())
                                    nm2.addInt(objCollided.getOwner().getLastStation())
                                    NetworkMessage.getInstance().addMessage(nm2)
                                nm = netMessage(C_NETWORK_REMOVE_CHAR, User.listOfUser[u].getConnexion())
                            nm.addInt(objCollided.getOwner().getId())
                            NetworkMessage.getInstance().addMessage(nm)

                            ch=User.listOfUser[u].getCurrentCharacter()
                            if tempJunk.mustSendToUser(ch.getId()):
                                nm = netMessage(C_NETWORK_ADD_JUNK, User.listOfUser[u].getConnexion())
                                tempJunk.sendInfo(nm,ch.getId())
                                NetworkMessage.getInstance().addMessage(nm)

                        User.lock.release()
                    User.lock.acquire()
                    for u in User.listOfUser:
                        nm = netMessage(C_NETWORK_REMOVE_SHOT, User.listOfUser[u].getConnexion())
                        nm.addInt(Bullet.listOfBullet[b].getId())
                        NetworkMessage.getInstance().addMessage(nm)
                        nm = netMessage(C_NETWORK_EXPLOSION, User.listOfUser[u].getConnexion())
                        pos = Bullet.listOfBullet[b].getPos()
                        nm.addFloat(pos.getX())
                        nm.addFloat(pos.getY())
                        nm.addFloat(pos.getZ())
                        NetworkMessage.getInstance().addMessage(nm)
                    User.lock.release()
                    bulletToRemove.append(b)

        for b in bulletToRemove:
            User.lock.acquire()
            for u in User.listOfUser:
                if Bullet.listOfBullet.has_key(b):
                    nm = netMessage(C_NETWORK_REMOVE_SHOT, User.listOfUser[u].getConnexion())
                    nm.addInt(Bullet.listOfBullet[b].getId())
                    NetworkMessage.getInstance().addMessage(nm)
                    Bullet.removeBullet(b)
            User.lock.release()
        Bullet.lock.release()

    def runUpdateCharShot(self):
        # ~ tempMsg=NetworkZoneUDPServer.getInstance().getListOfMessageById(C_NETWORK_CHAR_SHOT)
        tempMsg = NetworkTCPServer.getInstance().getListOfMessageById(C_NETWORK_CHAR_SHOT)
        if len(tempMsg) > 0:
            for msg in tempMsg:
                netMsg = msg.getMessage()
                usr = int(netMsg[0])
                charact = int(netMsg[1])
                pos = Point3(float(netMsg[2]), float(netMsg[3]), float(netMsg[4]))
                quat = (float(netMsg[5]), float(netMsg[6]), float(netMsg[7]), float(netMsg[8]))
                if User.listOfUser.has_key(usr):
                    ch = User.listOfUser[usr].getCurrentCharacter()
                    Bullet.lock.acquire()
                    if ch.getShip() is not None and ch.getShip().getWeapon() is not None and ch.getShip().getWeapon().isEnabled():
                        b = ch.getShip().getWeapon().addBullet(pos, quat)
                        Bullet.lock.release()
                        User.lock.acquire()
                        for u in User.listOfUser:
                            nm = netMessage(C_NETWORK_NEW_CHAR_SHOT, User.listOfUser[u].getConnexion())
                            nm.addInt(usr)
                            nm.addInt(b.getId())
                            nm.addFloat(b.getPos().getX())
                            nm.addFloat(b.getPos().getY())
                            nm.addFloat(b.getPos().getZ())
                            nm.addFloat(b.getQuat().getR())
                            nm.addFloat(b.getQuat().getI())
                            nm.addFloat(b.getQuat().getJ())
                            nm.addFloat(b.getQuat().getK())
                            NetworkMessage.getInstance().addMessage(nm)
                        User.lock.release()
            # ~ NetworkZoneUDPServer.getInstance().removeMessage(msg)
            NetworkTCPServer.getInstance().removeMessage(msg)

    def runPhysics(self):
        """
            run bullet Physics
        """
        actualTime = globalClock.getRealTime()
        if self.lastGlobalTicks == 0:
            self.lastGlobalTicks = actualTime
        dt = actualTime - self.lastGlobalTicks

        if dt > C_STEP_SIZE:
            self.lastGlobalTicks = actualTime
            User.lock.acquire()
            for usr in User.listOfUser:
                if User.listOfUser[usr].getCurrentCharacter() != None:
                    User.listOfUser[usr].getCurrentCharacter().getShip().runPhysics()
            User.lock.release()
            NPC.lock.acquire()
            for npc in self.npc:
                npc.runPhysics()
            NPC.lock.release()
            self.world.doPhysics(dt, 10)

    @staticmethod
    def getInstance(id):
        if Zone.instance == None:
            Zone.instance = Zone(id)

        return Zone.instance

    def loadZoneJunkFromBdd(self):
        query="SELECT star015_id FROM star015_junk WHERE star015_zone_star011 ='" + str(self.id) + "'"
        instanceDbConnector=shimDbConnector.getInstance()

        cursor=instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall ()
        for row in result_set:
            junkLoaded=junk(row[0])
        cursor.close()

    def loadZoneFromBdd(self):
        query = "SELECT star011_name, star011_typezone_star012 FROM star011_zone WHERE star011_id ='" + str(
            self.id) + "'"
        shimDbConnector.lock.acquire()
        instanceDbConnector = shimDbConnector.getInstance()

        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()
        for row in result_set:
            self.zoneName = row[0]
            self.typeZone = row[1]
        cursor.close()
        shimDbConnector.lock.release()
        self.loadZoneAsteroidFromBdd()
        self.loadZoneStationFromBdd()
        self.loadZoneNPCFromBDD()
        self.loadZoneJunkFromBdd()


    def loadZoneNPCFromBDD(self):
        # temp = NPC(0, 3, self)
        # temp.ship.setPos((1500, 1000, 1000))
        # temp.saveToBDD()  # ~ temp=NPC(0,3,self)
        # ~ temp.ship.setPos((1000,1200,1200))
        #~ temp.saveToBDD()
        # temp=NPC(0,3,self)
        # temp.ship.setPos((1500,1500,1000))
        # temp.saveToBDD()
        # temp=NPC(0,3,self)
        #~ temp.ship.setPos((2000,1000,2000))
        #~ temp.saveToBDD()

        query = "SELECT star034_id FROM star034_npc WHERE star034_zone_star011zone ='" + str(self.id) + "'"
        shimDbConnector.lock.acquire()
        instanceDbConnector = shimDbConnector.getInstance()
        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()
        for row in result_set:
            temp = NPC(int(row[0]), 0, self)

            self.npc.append(temp)
            temp.ship.loadEgg(self.world, self.worldNP)
            temp.loadXml()
        shimDbConnector.lock.release()


    def loadZoneAsteroidFromBdd(self):
        query = "SELECT star014_id FROM star014_asteroid WHERE star014_zone_star011 ='" + str(self.id) + "'"
        shimDbConnector.lock.acquire()
        instanceDbConnector = shimDbConnector.getInstance()

        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()
        for row in result_set:
            astLoaded = Asteroid(row[0], self.world, self.worldNP)
            self.listOfAsteroid.append(astLoaded)
        cursor.close()
        shimDbConnector.lock.release()


    def loadZoneStationFromBdd(self):
        query = "SELECT star022_zone_star011 FROM star022_station WHERE star022_inzone_star011 ='" + str(self.id) + "'"
        shimDbConnector.lock.acquire()
        instanceDbConnector = shimDbConnector.getInstance()

        cursor = instanceDbConnector.getConnection().cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()
        for row in result_set:
            stationLoaded = Station(row[0], self.world, self.worldNP)
            self.listOfStation.append(stationLoaded)
        cursor.close()
        shimDbConnector.lock.release()