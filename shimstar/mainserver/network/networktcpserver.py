import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
import sys, imp, os, string
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from shimstar.mainserver.network.networkmessage import *
from shimstar.mainserver.network.netmessage import *
from shimstar.core.constantes import *
from shimstar.user.user import *
from shimstar.world.zone.zonemainserver import *


class NetworkTCPServer():
    instance = None

    def __init__(self):
        instance = self

        # ~ networkmessage()
        self.listOfMessage = []
        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)
        self.Connections = {}
        self.activeConnections = []  # We'll want to keep track of these later

        self.portAddressTCP = 7777  #No-other TCP/IP services are using this port
        backlog = 1000  #If we ignore 1,000 connection attempts, something is wrong!
        self.tcpSocket = self.cManager.openTCPServerRendezvous(self.portAddressTCP, backlog)

        self.cListener.addConnection(self.tcpSocket)

        taskMgr.add(self.tskListenerPolling, "Poll the connection listener", -39)
        #~ taskMgr.add(self.tskListenerPolling,"Poll the connection listener")
        taskMgr.add(self.tskReaderPolling, "Poll the connection reader", -40)
        taskMgr.add(self.tskNetworkMessage, "Poll the messages", -38)


    def tskNetworkMessage(self, task):
        """
            This method send message in another task than the reader, to avoid nuggle
        """
        msgs = NetworkMessage.getInstance().getListOfMessage()

        if len(msgs) > 0:
            for msg in msgs:
                ret = self.cWriter.send(msg.getMsg(), msg.getConnexion(), True)

        return Task.cont

    def tskListenerPolling(self, taskdata):
        """
            Listener on connexion
        """
        # ~ print self.cListener.newConnectionAvailable()
        if self.cListener.newConnectionAvailable():
            rendezvous = PointerToConnection()
            netAddress = NetAddress()
            newConnection = PointerToConnection()

            if self.cListener.getNewConnection(rendezvous, netAddress, newConnection):
                newConnection = newConnection.p()
                newConnection.setNoDelay(True)
                self.activeConnections.append(newConnection)  # Remember connection
                self.cReader.addConnection(newConnection)  # Begin reading connection
                self.Connections[str(newConnection.this)] = rendezvous
        if self.cManager.resetConnectionAvailable():
            conn = PointerToConnection()

            self.cManager.getResetConnection(conn)
            c = conn.p()

            if self.activeConnections.count(c) > 0:
                self.activeConnections.remove(c)
                usrToDelete = None
                User.lock.acquire()
                for usr in User.listOfUser:
                    if User.listOfUser[usr].getConnexion() == c:
                        usrToDelete = User.listOfUser[usr]
                User.lock.release()
                if usrToDelete != None:
                    #~ usrToDelete.saveToBDD()
                    #~ print "aaaaaaaaaaaaaaaaa"
                    usrToDelete.destroy()
                #~ for usr in User.listOfUser:
                #~ if usr!=usrToDelete:
                #~ NetworkMessage.getInstance().addMessage(C_USER_OUTGOING,str(usrToDelete.getId()),usr.getConnexion())
                if usrToDelete != None:
                    #~ if User.listOfUser.index(usrToDelete.getId())>=0:
                    #~ User.listOfUser.remove(usrToDelete)
                    usrToDelete.destroy()
                User.lock.release()
            if self.Connections.has_key(str(c)):
                del self.Connections[str(c)]
            self.cReader.removeConnection(c)
            self.cManager.closeConnection(c)

        return Task.cont

    def tskReaderPolling(self, taskdata):
        """
            Read the network data
        """
        if self.cReader.dataAvailable():
            datagram = NetDatagram()  # catch the incoming data in this instance
            # Check the return value; if we were threaded, someone else could have
            # snagged this data before we did
            # ~ print datagram
            if self.cReader.getData(datagram):
                self.myProcessDataFunction(datagram, taskdata.time)
        return Task.cont

        # ~ @updated

    def myProcessDataFunction(self, netDatagram, timer):
        """
            Process messages incoming from network
        """
        myIterator = PyDatagramIterator(netDatagram)
        connexion = netDatagram.getConnection()
        msgTab = []
        msgID = myIterator.getUint32()
        print msgID
        if msgID == C_NETWORK_CONNECT:
            name = myIterator.getString()
            password = myIterator.getString()
            if User.userExists(name) == True:
                tempUser = User.getUserInstantiatedByName(name)
                print User.listOfUser
                if tempUser == None:
                    tempUser = User(name=name)

                    if (tempUser.getPwd() == password):
                        nm = netMessage(C_NETWORK_CONNECT, connexion)
                        nm.addInt(C_CONNEXION_OK)
                        tempUser.sendInfo(nm)
                        NetworkMessage.getInstance().addMessage(nm)
                        tempUser.setConnexion(connexion)
                    #~ User.listOfUser
                    else:
                        nm = netMessage(C_NETWORK_CONNECT, connexion)
                        nm.addInt(C_CONNEXION_WRONGPWD)
                        NetworkMessage.getInstance().addMessage(nm)
                        tempUser.destroy()
                else:
                    nm = netMessage(C_NETWORK_CONNECT, connexion)
                    nm.addInt(C_CONNEXION_ALREADYCONNECTED)
                    NetworkMessage.getInstance().addMessage(nm)
                #~ tempUser.destroy()
            else:
                nm = netMessage(C_NETWORK_CONNECT, connexion)
                nm.addInt(C_CONNEXION_NOACCOUNT)
                NetworkMessage.getInstance().addMessage(nm)
        elif msgID == C_NETWORK_CONFIG_ZONE:
            id = myIterator.getUint32()
            ip = myIterator.getString()
            port = myIterator.getUint32()
            portudp = myIterator.getUint32()
            portudp2 = myIterator.getUint32()
            pp = ZoneMainServer.getZone(id)
            temp = ZoneMainServer(id, ip, port, portudp, portudp2, connexion)
            nm = netMessage(C_NETWORK_ACKNOWLEDGEMENT, connexion)
            NetworkMessage.getInstance().addMessage(nm)
        elif msgID == C_NETWORK_INFO_ZONE:
            id = myIterator.getUint32()
            zm = ZoneMainServer.getZone(id)
            if zm != None:
                ip, port, portUdp, portUdp2 = zm.getConfig()
                nm = netMessage(C_NETWORK_INFO_ZONE, connexion)
                nm.addString(ip)
                nm.addInt(port)
                nm.addInt(portUdp)
                nm.addInt(portUdp2)
                NetworkMessage.getInstance().addMessage(nm)
        elif msgID == C_NETWORK_USER_CHOOSE_HERO:
            iduser = myIterator.getUint32()
            idchar = myIterator.getUint32()
            tempUser = User.getUserById(iduser)
            if tempUser != None:
                nm = netMessage(C_NETWORK_CHOOSE_CHAR, connexion)
                tempUser.setCurrent(idchar, nm)
                NetworkMessage.getInstance().addMessage(nm)
        elif msgID == C_NETWORK_USER_CHANGE_ZONE:
            iduser = int(myIterator.getUint32())
            idzone = myIterator.getUint32()
            tempUser = User.getUserById(iduser)
            if tempUser != None:
                tempUser.changeZone(idzone)

        elif msgID == C_NETWORK_CHARACTER_SELL_ITEM:
            idUser = int(myIterator.getUint32())
            idIt = int(myIterator.getUint32())
            inv= int(myIterator.getUint32())
            User.lock.acquire()
            for u in User.listOfUser:
                if u == int(idUser):
                    User.listOfUser[u].getCurrentCharacter().sellItem(idIt,inv)
                    nm = netMessage(C_NETWORK_CHARACTER_SELL_ITEM, connexion)
                    nm.addInt(idIt)
                    nm.addInt(User.listOfUser[u].getCurrentCharacter().getCoin())
                    nm.addInt(inv)
                    NetworkMessage.getInstance().addMessage(nm)
        elif msgID == C_NETWORK_CHARACTER_INV2STATION:
            iduser = myIterator.getUint32()
            iditem = myIterator.getUint32()
            idstation = myIterator.getUint32()
            for u in User.listOfUser:
                if u == int(iduser):
                    User.listOfUser[u].getCurrentCharacter().moveItemInvToStation(iditem,idstation,toStation=True)
                    nm = netMessage(C_NETWORK_CHARACTER_INV2STATION, connexion)
                    nm.addInt(iditem)
                    NetworkMessage.getInstance().addMessage(nm)
        elif msgID == C_NETWORK_CHARACTER_STATION2INV:
            iduser = myIterator.getUint32()
            iditem = myIterator.getUint32()
            idstation = myIterator.getUint32()
            for u in User.listOfUser:
                if u == int(iduser):
                    User.listOfUser[u].getCurrentCharacter().moveItemInvToStation(iditem,idstation,toStation=False)
                    nm = netMessage(C_NETWORK_CHARACTER_STATION2INV, connexion)
                    nm.addInt(iditem)
                    NetworkMessage.getInstance().addMessage(nm)
        elif msgID == C_NETWORK_CHARACTER_BUY_ITEM:
            idUser = int(myIterator.getUint32())
            idIt = int(myIterator.getUint32())
            inv = int(myIterator.getUint32())
            User.lock.acquire()
            for u in User.listOfUser:
                if u == int(idUser):
                    it = User.listOfUser[u].getCurrentCharacter().buyItem(idIt,inv)
                    if it is not None :
                        nm = netMessage(C_NETWORK_CHARACTER_BUY_ITEM, connexion)
                        nm.addInt(it.getTypeItem())
                        nm.addInt(it.getTemplate())
                        nm.addInt(it.getId())
                        nm.addInt(User.listOfUser[u].getCurrentCharacter().getCoin())
                        nm.addInt(inv)
                        NetworkMessage.getInstance().addMessage(nm)
        elif msgID == C_NETWORK_CHARACTER_UNINSTALL_SLOT:
            idUser = int(myIterator.getUint32())
            User.lock.acquire()
            for u in User.listOfUser:
                if u == int(idUser):
                    User.listOfUser[u].getCurrentCharacter().getShip().uninstallItemBySlotId(int(myIterator.getUint32()))
                    User.listOfUser[u].getCurrentCharacter().getShip().saveToBDD()

        elif msgID == C_NETWORK_CHARACTER_INSTALL_SLOT:
            idUser = int(myIterator.getUint32())
            User.lock.acquire()
            for u in User.listOfUser:
                if u == int(idUser):
                    User.listOfUser[u].getCurrentCharacter().getShip().installItem(int(myIterator.getUint32()),
                        int(myIterator.getUint32()))
                    User.listOfUser[u].getCurrentCharacter().getShip().saveToBDD()
        elif msgID == C_NETWORK_DEATH_CHAR:
            idUser = int(myIterator.getUint32())
            User.lock.acquire()
            for u in User.listOfUser:
                if u == int(idUser):
                    User.listOfUser[u].getCurrentCharacter().manageDeathFromMainServer()
                    nm = netMessage(C_NETWORK_DEATH_CHAR_STEP2, connexion)
                    User.listOfUser[u].getCurrentCharacter().sendCompleteInfo(nm)
                    NetworkMessage.getInstance().addMessage(nm)
            User.lock.release()
        elif msgID == C_USER_ADD_CHAR:
            id = int(myIterator.getUint32())
            name = myIterator.getString()
            face = myIterator.getString()
            userFound = None
            User.lock.acquire()
            for u in User.listOfUser:
                if u == int(id):
                    userFound = User.listOfUser[u]
                    break
            if userFound != None:
                tempChar = userFound.addCharacter(name, face)
                nm = netMessage(C_USER_ADD_CHAR, connexion)
                tempChar.sendInfo(nm)
                NetworkMessage.getInstance().addMessage(nm)
            User.lock.release()
        elif msgID == C_USER_DELETE_CHAR:
            idUser = int(myIterator.getUint32())
            idChar = int(myIterator.getUint32())
            userFound = None
            for u in User.listOfUser:
                if u == int(idUser):
                    userFound = User.listOfUser[u]
                    break
            if userFound != None:
                userFound.deleteCharacter(idChar)
                nm = netMessage(C_USER_DELETE_CHAR, connexion)
                nm.addInt(idChar)
                NetworkMessage.getInstance().addMessage(nm)

        elif msgID == C_CREATE_USER:
            user = myIterator.getString()
            pwd = myIterator.getString()
            self.createNewUser(user, pwd, connexion)
        elif msgID == C_NETWORK_ASK_READ_DIALOG:
            idUser = int(myIterator.getUint32())
            idChar = int(myIterator.getUint32())
            userFound = None
            for u in User.listOfUser:
                if u == int(idUser):
                    userFound = User.listOfUser[u]
            if userFound != None:
                ch = userFound.getCharacterById(idChar)
                if ch != None:
                    nm = netMessage(C_NETWORK_ASK_READ_DIALOG, connexion)
                    ch.sendReadDialogs(nm)
                    NetworkMessage.getInstance().addMessage(nm)
        elif msgID == C_NETWORK_ASKING_CHAR:
            usrId = int(myIterator.getUint32())
            usr = User.getUserById(usrId)
            if usr != None:
                nm = netMessage(C_NETWORK_CURRENT_CHAR_INFO, connexion)
                usr.sendInfoCharForStation(nm)
                NetworkMessage.getInstance().addMessage(nm)
        elif msgID == C_NETWORK_APPEND_READ_DIALOG:
            idUser = int(myIterator.getUint32())
            idChar = int(myIterator.getUint32())
            userFound = None
            for u in User.listOfUser:
                if u == int(idUser):
                    userFound = User.listOfUser[u]
            if userFound != None:
                ch = userFound.getCharacterById(idChar)
                if ch != None:
                    ch.appendReadDialog(int(myIterator.getUint32()))
        elif msgID == C_NETWORK_CHARACTER_ACCEPT_MISSION:
            idUser = int(myIterator.getUint32())
            idMission = int(myIterator.getUint32())
            userFound = None
            for u in User.listOfUser:
                if u == int(idUser):
                    ch = User.listOfUser[u].getCurrentCharacter()
                    ch.acceptMission(idMission)


    def createNewUser(self, usr, pwd, connexion):
        """
        create a new user(xml) if it doesn't exist
        """
        alreadyExist = User.userExists(usr)
        if alreadyExist == True:
            nm = netMessage(C_CREATE_USER, connexion)
            nm.addInt(0)
            NetworkMessage.getInstance().addMessage(nm)
        else:
            tempUser = User(name=usr, new=True)
            tempUser.setPwd(pwd)
            tempUser.saveToBDD()
            tempUser.destroy()
            User.destroyUserById(0)
            nm = netMessage(C_CREATE_USER, connexion)
            nm.addInt(1)
            NetworkMessage.getInstance().addMessage(nm)


    def sendMessage(self, idMessage, message, connexion):
        """
        method allowing to send directly a msg
        """
        print "MESSAGE SORTANT ============" + str(idMessage) + "/" + str(message)
        self.cWriter.send(self.myNewPyDatagram(id, message), connexion)


    def myNewPyDatagram(self, id, message):
        # send a test message
        myPyDatagram = PyDatagram()
        myPyDatagram.addUint8(id)
        myPyDatagram.addString(message)
        return myPyDatagram


    def getListOfMessageById(self, id):
        msgToReturn = []
        for msg in self.listOfMessage:
            iop = msg.getId()
            if (msg.getId() == id):
                msgToReturn.append(msg)

        return msgToReturn