import os, sys
import MySQLdb
from direct.stdpy import threading

class shimDbConnector:
    instance = None
    lock = threading.Lock()

    def __init__(self):
        self.host = "localhost"
        # ~ self.host="62.147.217.96"
        #~ self.host="192.168.0.254"
        #~ self.host="thyshimrod.praesepe.net"

        self.user = "shimstar"
        self.pwd = "shimstar"
        self.db = "shimstar"
        # shimDbConnector.instance = self
        self.connect()

    def connect(self):
        self.connection = MySQLdb.connect(host=self.host, user=self.user, passwd=self.pwd, db=self.db)
        self.connection.autocommit(True)
        cursor = self.connection.cursor()
        query = " SET GLOBAL tx_isolation = 'READ-COMMITTED';"
        cursor.execute(query)
        query = " SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED ;"
        cursor.execute(query)
        cursor.close()

    @staticmethod
    def getNewInstance():
        newInstance = shimDbConnector()
        return newInstance

    @staticmethod
    def getInstance():
        if shimDbConnector.instance is None:
            shimDbConnector.instance = shimDbConnector()
        return shimDbConnector.instance

    def getConnection(self):
        return self.connection

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

    def resetConnection(self):
        shimDbConnector.lock.acquire()
        self.connection.close()
        self.connect()
        shimDbConnector.lock.release()
		
