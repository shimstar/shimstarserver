from shimstar.bdd.dbconnector import *
		
class CheckConsistency:
	def __init__(self):
		self.connexion=shimDbConnector.getInstance()
		
	def run(self):
		#~ pass
		self.runItemNpc()
		self.runItemPlayer()
		self.runItemJunk()
		self.runItemWOOwner()
		self.runShip()
		self.runSlot()
		self.runItemWOSlot()
		self.runItemShip()
		self.connexion.close()
	
	def runItemNpc(self):
		print "Suppression des objets lies directement aux NPCs"
		query="select star006_id,star004_name from star006_item join star004_item_template on star006_template_star004 = star004_id where star006_containertype='star034_npc' and star006_container_starnnn not in (select star034_id from star034_npc)"
		cursor=self.connexion.getConnection().cursor()
		
		cursor.execute(query)
		result_set = cursor.fetchall ()
		
		listOfIdToDelete=[]
		nbObj=0
		for row in result_set:
			print str(row[0] ) + " / " + str(row[1])
			listOfIdToDelete.append(int(row[0]))
			nbObj+=1
		cursor.close()
		
		if len(listOfIdToDelete) > 0:
			listOfId=""
			for id in listOfIdToDelete:
				if listOfId=="":
					listOfId="'" + str(id) + "'"
				else:
					listOfId+="," + "'" + str(id) + "'"
				
			query="delete from star006_item where star006_id in (" + str(listOfId) + ")"
			cursor=self.connexion.getConnection().cursor()
			cursor.execute(query)
			cursor.close()
			self.connexion.commit()
			
		print str(nbObj) + " objets supprimes"
		print "#################################"
		
	def runItemPlayer(self):
		print "Suppression des objets lies directement aux Players"
		query="select star006_id,star004_name from star006_item join star004_item_template on star006_template_star004 = star004_id where star006_containertype='star002_character' and star006_container_starnnn not in (select star002_id from star002_character)"
		cursor=self.connexion.getConnection().cursor()
		
		cursor.execute(query)
		result_set = cursor.fetchall ()
		
		listOfIdToDelete=[]
		nbObj=0
		for row in result_set:
			print str(row[0] ) + " / " + str(row[1])
			listOfIdToDelete.append(int(row[0]))
			nbObj+=1
		cursor.close()
		
		if len(listOfIdToDelete) > 0:
			listOfId=""
			for id in listOfIdToDelete:
				if listOfId=="":
					listOfId="'" + str(id) + "'"
				else:
					listOfId+="," + "'" + str(id) + "'"
				
			query="delete from star006_item where star006_id in (" + str(listOfId) + ")"
			cursor=self.connexion.getConnection().cursor()
			cursor.execute(query)
			cursor.close()
			self.connexion.commit()
			
		print str(nbObj) + " objets supprimes"
		print "#################################"
		
	def runItemJunk(self):
		print "Suppression des objets lies directement aux Junks"
		query="select star006_id,star004_name from star006_item join star004_item_template on star006_template_star004 = star004_id where star006_containertype='star015_junk' and star006_container_starnnn not in (select star015_id from star015_junk)"
		cursor=self.connexion.getConnection().cursor()
		
		cursor.execute(query)
		result_set = cursor.fetchall ()
		
		listOfIdToDelete=[]
		nbObj=0
		for row in result_set:
			print str(row[0] ) + " / " + str(row[1])
			listOfIdToDelete.append(int(row[0]))
			nbObj+=1
		cursor.close()
		
		if len(listOfIdToDelete) > 0:
			listOfId=""
			for id in listOfIdToDelete:
				if listOfId=="":
					listOfId="'" + str(id) + "'"
				else:
					listOfId+="," + "'" + str(id) + "'"
				
			query="delete from star006_item where star006_id in (" + str(listOfId) + ")"
			cursor=self.connexion.getConnection().cursor()
			cursor.execute(query)
			cursor.close()
			self.connexion.commit()
			
		print str(nbObj) + " objets supprimes"
		print "#################################"
		
	def runItemWOOwner(self):
		print "Suppression des objets sans attaches"
		query="select star006_id,star004_name from star006_item join star004_item_template on star006_template_star004 = star004_id where star006_containertype=''"
		cursor=self.connexion.getConnection().cursor()
		
		cursor.execute(query)
		result_set = cursor.fetchall ()
		
		listOfIdToDelete=[]
		nbObj=0
		for row in result_set:
			print str(row[0] ) + " / " + str(row[1])
			listOfIdToDelete.append(int(row[0]))
			nbObj+=1
		cursor.close()
		
		if len(listOfIdToDelete) > 0:
			listOfId=""
			for id in listOfIdToDelete:
				if listOfId=="":
					listOfId="'" + str(id) + "'"
				else:
					listOfId+="," + "'" + str(id) + "'"
				
			query="delete from star006_item where star006_id in (" + str(listOfId) + ")"
			cursor=self.connexion.getConnection().cursor()
			cursor.execute(query)
			cursor.close()
			self.connexion.commit()
			
		print str(nbObj) + " objets supprimes"
		print "#################################"
		
	def runItemShip(self):
		print "Suppression des objets dans des soutes de vaisseau non existants"
		query="select star006_id,star004_name from star006_item join star004_item_template on star006_template_star004 = star004_id where star006_containertype='star007_ship' and star006_container_starnnn not in (select star007_id from star007_ship)"
		cursor=self.connexion.getConnection().cursor()
		
		cursor.execute(query)
		result_set = cursor.fetchall ()
		
		listOfIdToDelete=[]
		nbObj=0
		for row in result_set:
			print str(row[0] ) 
			listOfIdToDelete.append(int(row[0]))
			nbObj+=1
		cursor.close()
		
		if len(listOfIdToDelete) > 0:
			listOfId=""
			for id in listOfIdToDelete:
				if listOfId=="":
					listOfId="'" + str(id) + "'"
				else:
					listOfId+="," + "'" + str(id) + "'"
				
			query="delete from star006_item where star006_id in (" + str(listOfId) + ")"
			cursor=self.connexion.getConnection().cursor()
			cursor.execute(query)
			cursor.close()
			self.connexion.commit()
			
		print str(nbObj) + " objets supprimes"
		print "#################################"
		
	def runShip(self):
		print "suppression des vaisseaux sans item"
		query="select star007_id from star007_ship where star007_item_star006 not in (select star006_id from star006_item)"
		cursor=self.connexion.getConnection().cursor()
		
		cursor.execute(query)
		result_set = cursor.fetchall ()
		
		listOfIdToDelete=[]
		nbObj=0
		for row in result_set:
			print str(row[0] ) 
			listOfIdToDelete.append(int(row[0]))
			nbObj+=1
		cursor.close()
		
		if len(listOfIdToDelete) > 0:
			listOfId=""
			for id in listOfIdToDelete:
				if listOfId=="":
					listOfId="'" + str(id) + "'"
				else:
					listOfId+="," + "'" + str(id) + "'"
				
			query="delete from star007_ship where star007_id in (" + str(listOfId) + ")"
			cursor=self.connexion.getConnection().cursor()
			cursor.execute(query)
			cursor.close()
			self.connexion.commit()
			
		print str(nbObj) + " objets supprimes"
		print "#################################"
		
	def runSlot(self):
		print "suppression des slot sans vaisseaux"
		query="select star009_id from star009_slot where star009_ship_star007 not in (select star007_id from star007_ship)"
		query+=" AND star009_ship_star005 NOT IN (SELECT star005_id FROM star005_ship_template)"
		cursor=self.connexion.getConnection().cursor()
		
		cursor.execute(query)
		result_set = cursor.fetchall ()
		
		listOfIdToDelete=[]
		nbObj=0
		for row in result_set:
			print str(row[0] ) 
			listOfIdToDelete.append(int(row[0]))
			nbObj+=1
		cursor.close()
		
		if len(listOfIdToDelete) > 0:
			listOfId=""
			for id in listOfIdToDelete:
				if listOfId=="":
					listOfId="'" + str(id) + "'"
				else:
					listOfId+="," + "'" + str(id) + "'"
				
			query="delete from star009_slot where star009_id in (" + str(listOfId) + ")"
			cursor=self.connexion.getConnection().cursor()
			cursor.execute(query)
			cursor.close()
			self.connexion.commit()
			
		print str(nbObj) + " slots supprimes"
		print "#################################"
		
		query="SELECT count(*) FROM star021_slot_typeitem WHERE star021_slot_star009 NOT IN (SELECT star009_id FROM star009_slot)"
		cursor=self.connexion.getConnection().cursor()
		
		cursor.execute(query)
		result_set = cursor.fetchall ()
		nbObj=0
		for row in result_set:
			nbObj=int(row[0])
		cursor.close()
		
		query="delete FROM star021_slot_typeitem WHERE star021_slot_star009 NOT IN (SELECT star009_id FROM star009_slot)"
				
		cursor=self.connexion.getConnection().cursor()
		
		cursor.execute(query)
		cursor.close()
		self.connexion.commit()
		
		print str(nbObj) + " slots type supprimes"
		print "#################################"
		
	def runItemWOSlot(self):
		print "suppression des items sans slot="
		query="select star006_id from star006_item where star006_containertype='star009_slot' and star006_container_starnnn not in (select star009_id from star009_slot)"
		cursor=self.connexion.getConnection().cursor()
		
		cursor.execute(query)
		result_set = cursor.fetchall ()
		
		listOfIdToDelete=[]
		nbObj=0
		for row in result_set:
			print str(row[0] ) 
			listOfIdToDelete.append(int(row[0]))
			nbObj+=1
		cursor.close()
		
		if len(listOfIdToDelete) > 0:
			listOfId=""
			for id in listOfIdToDelete:
				if listOfId=="":
					listOfId="'" + str(id) + "'"
				else:
					listOfId+="," + "'" + str(id) + "'"
				
			query="delete from star006_item where star006_id in (" + str(listOfId) + ")"
			cursor=self.connexion.getConnection().cursor()
			cursor.execute(query)
			cursor.close()
			self.connexion.commit()
			
		print str(nbObj) + " objets supprimes"
		print "#################################"
		#~ result_set = cursor.fetchall ()
		#~ id=301000
		#~ querySelectTooHigh="select id from demande_se_trouve_dans_etat where id > 4000000000"
		#~ cursor=connexionAlas.getConnection().cursor()
		#~ cursor.execute(querySelectTooHigh)
		#~ result_set = cursor.fetchall ()
		#~ listOfId=""
		#~ idToUpdate={}
		#~ for row in result_set:
			#~ idDemande=int(row[0])
			#~ idToUpdate[idDemande]=id
			#~ id+=1
		#~ cursor.close()
		
		#~ cursor=connexionAlas.getConnection().cursor()
		#~ for idToMody in idToUpdate:
			#~ queryUpdate="update demande_se_trouve_dans_etat set id = " + str(idToUpdate[idToMody]) + " where id = " + str(idToMody)
			#~ cursor.execute(queryUpdate)
		
		#~ connexionAlas.commit()
		#~ cursor.close()
		#~ connexionAlas.close()
			
