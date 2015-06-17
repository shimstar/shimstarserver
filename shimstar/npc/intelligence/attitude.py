import os, sys
import os.path
import xml.dom.minidom
from shimstar.core.constantes import *
from shimstar.npc.intelligence.commons.commons import *
from shimstar.npc.intelligence.behaviors.behavior import *
from shimstar.npc.intelligence.behaviors.behaviorpatrol import *
from shimstar.npc.intelligence.behaviors.behaviorattack import *
from shimstar.npc.intelligence.behaviors.behaviorfactory import *
from shimstar.user.user import *
# from shimstar.npc.npc import *
# ~ from shimstar.core.function import *
class AttitudeProperties:
    def __init__(self, typeAttitude=0, level=0, faction=0):
        self.level = level
        self.typeAttitude = typeAttitude
        self.faction = faction

    def getFaction(self):
        return self.faction

    def getTypeAttitude(self):
        return self.typeAttitude

    def getLevel(self):
        return self.level


class Attitude:
    def __init__(self, npc):
        self.behavior = {}
        self.currentBehavior = -1
        self.attitude = []
        self.npc = npc

    def loadBehavior(self, id, zone):
        print "Attitude::loadBehavior " + str(id) + "/" + str(zone)
        if os.path.exists("./config/behaviour/" + str(zone) + "/" + str(id) + ".xml"):
            dom = xml.dom.minidom.parse("./config/behaviour/" + str(zone) + "/" + str(id) + ".xml")
            pp = dom.getElementsByTagName('patrolpoint')
            beh = self.setBehavior(C_BEHAVIOR_PATROL)
            for p in pp:
                pos = p.firstChild.data
                tabpos = pos.split(",")
                beh.addPatrolPoint(Vec3(float(tabpos[0]), float(tabpos[1]), float(tabpos[2])))
            atti = dom.getElementsByTagName('attitude')
            for a in atti:
                typeAtti = int(a.getElementsByTagName('typeattitude')[0].firstChild.data)
                lvlAtti = int(a.getElementsByTagName('levelattitude')[0].firstChild.data)
                faction = int(a.getElementsByTagName('faction')[0].firstChild.data)
                temp = AttitudeProperties(typeAtti, lvlAtti, faction)
                self.attitude.append(temp)

    def getBehaviors(self):
        return self.behavior

    def getAttitude(self):
        return self.attitude

    def run(self):
        if self.currentBehavior >= 0:
            if self.behavior.has_key(self.currentBehavior):
                if self.behavior[self.currentBehavior].getStatus() == C_BEHAVIOR_STATUS_CURRENT:
                    self.behavior[self.currentBehavior].run()
                else:
                    if len(self.behavior) > 1:
                        del self.behavior[self.currentBehavior]
                        self.currentBehavior = len(self.behavior) - 1
        else:
            if len(self.behavior) > 0:
                self.currentBehavior = 0

        for att in self.attitude:
            if att.getTypeAttitude() == C_ATTITUDE_AGGRESSIVITE:
                if att.getLevel() > 2:
                    alreadyAttack = False
                    for behav in self.behavior:
                        if isinstance(self.behavior[behav], BehaviorAttack):
                            alreadyAttack = True
                            break
                    #~ print User.listOfUser

                    if not alreadyAttack:
                        nearer = None
                        nearerDist = 100000000
                        ships = []
                        nnn = []
                        User.lock.acquire()
                        for u in User.listOfUser:
                            ship = User.listOfUser[u].getCurrentCharacter().ship
                            ships.append(ship)
                            nnn.append(u)
                        User.lock.release()

                        self.npc.lock.acquire()
                        self.npc.zone.lockListNpc.acquire()
                        for n in self.npc.zone.npc:
                            # print "attitude::run " + str(self.npc) + "//" + str(self.npc.faction) + "//" + str(self.npc.id) + "//" + str(n) + "//" + str(n.faction)
                            if n != self.npc and self.npc.faction!=n.faction:
                                ship = n.ship
                                ships.append(ship)
                                nnn.append(n)

                        self.npc.zone.lockListNpc.release()
                        self.npc.lock.release()

                        for s in ships:
                            s.lock.acquire()
                            if s.bodyNP is not None and not s.bodyNP.isEmpty():
                                # print "attitude::run " + str(s.owner.faction) + "/" + str(att.getFaction())
                                # if s.owner.faction == att.getFaction() or att.getFaction()==0:
                                if s.owner.faction == att.getFaction():
                                    dist = calcDistance(self.npc.ship.bodyNP, s.bodyNP)
                                    if dist < nearerDist:
                                        nearerDist = dist
                                        nearer = ship
                            s.lock.release()
                        if nearer is not None:
                            #~ print "attitude::run acquiring new target " + str(nearer)
                            behav = self.setBehavior(C_BEHAVIOR_ATTACK)
                            behav.setTarget(nearer.bodyNP)

    def runPhysics(self):
        if self.currentBehavior >= 0:
            if self.behavior.has_key(self.currentBehavior):
                self.behavior[self.currentBehavior].runPhysics()

    def setBehavior(self, beh):
        if not self.behavior.has_key(beh):
            self.behavior[beh] = behaviorFactory.getBehavior(beh, self.npc)
            self.currentBehavior = beh
        return self.behavior[beh]

    def addAttitude(self, typeAttitude, level, faction):
        temp = AttitudeProperties(typeAttitude, level, faction)
        self.attitude.append(temp)