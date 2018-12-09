import mysql.connector as mariadb
import pprint
import hashlib
import traceback, sys
import audioHandler
class USERHANDLER:
	def __init__(self):
		try:
			self._mariadb_connection = mariadb.connect(user='mayordomo', password='mayordomo', database='MayordomoETSIST')
			self._cursor = self._mariadb_connection.cursor()
		except Exception as e:
			print(str(e))
			print('No se ha podido conectar a la BBDD')

	def getAccess(self, user, passwd, ip):
		result = False
		self._cursor.execute("SELECT Username, Password FROM User WHERE Username=%s", (user,))
		for userDatabase, passwdDatabase in self._cursor:
			result = self._checkPassword(passwdDatabase, passwd)
			if(result == True):
				self._addIp(user, ip)
		return result

	def getNfcAccess(self, user):
		ip = None
		entrar = None
		try:
			self._cursor.execute("SELECT Username, MasterHomeHostname, Attached FROM User WHERE Username=%s", (user,))
			for userDatabase, homeHostameDatabase, attachedDatabase in self._cursor:
				user = userDatabase
				ip = homeHostameDatabase
				if(attachedDatabase == 0):
					self._addIp(user, homeHostameDatabase)
					audioHandler.audio('Bienvenido a casa. '+user)
					entrar = True
				if(attachedDatabase == 1):
					self.logoutHome(user)
					audioHandler.audio('Hasta pronto '+user+' que tenga un buen día')
					entrar = False

			return user, ip, entrar
		except mariadb.Error as error:
			print(str(error))
			print('NFC access denied')
			return user, None

	def getSmartphoneAccess(self, uid):
		ip = None
		user = None
		descrption = None
		entrar = None
		try:
			self._cursor.execute("SELECT u.Username, u.MasterHomeHostname, u.Attached, s.SmartphoneDescription, s.SmartphoneHostname, s.UseSmartphoneIP FROM User AS u INNER JOIN User2Smartphone AS u2s ON u.IdUser=u2s.IdUser INNER JOIN Smartphone AS s ON u2s.IdSmartphone=s.IdSmartphone WHERE s.UID=%s", (uid,))
			for userDatabase, homeHostameDatabase, attachedDatabase, smartphoneDescriptionDatabase, smartphoneHostnameDatabase, useSmartphoneIPDatabase in self._cursor:
				user = userDatabase
				if(useSmartphoneIPDatabase == 1):
					ip = smartphoneHostnameDatabase
				elif(useSmartphoneIPDatabase == 0):
					ip = homeHostameDatabase
				if(attachedDatabase == 0):
					self._addIp(user, ip)
					audioHandler.audio('Bienvenido a casa. '+userDatabase)
					entrar = True
				elif(attachedDatabase == 1):
					self.logoutHome(user)
					audioHandler.audio('Hasta pronto '+userDatabase+'. que tenga un buen día')
					entrar = False
			return user, ip, entrar
		except mariadb.Error as error:
			print(str(error))
			print('NFC access denied')
			return user, None

	def addSmartphoneAndRelate(self, user, uid, smartphoneDescription, smartphoneHostname, useSmartphoneIP):
		returned1 = self.addSmartphone(uid, smartphoneDescription, smartphoneHostname, useSmartphoneIP)
		returned2 = self.relateSmartphone(user, uid)
		return (returned1 and returned2)
	
	def relateSmartphone(self, username, uid):
		idUser = None
		idSmartphone = None
		try:
			self._cursor.execute("SELECT IdUser From User WHERE Username=%s", (username,))
			idUser = self._cursor.fetchone()[0]
			self._cursor.execute("SELECT IdSmartphone From Smartphone WHERE UID=%s", (uid,))
			idSmartphone = self._cursor.fetchone()[0]
			self._cursor.execute("SELECT COUNT(*) From User2Smartphone WHERE IdSmartphone=%s", (idSmartphone,))
			nAssociations = self._cursor.fetchone()[0]
			print(str(idUser) +' '+ str(idSmartphone)+' '+str(nAssociations))
			if(str(nAssociations)=='0'):
				self._cursor.execute("INSERT INTO User2Smartphone (IdUser, IdSmartphone) VALUES (%s,%s)", (idUser, idSmartphone))
				self._mariadb_connection.commit()
				return "Telefono asociado con exito",True
			else:
				print('Error Telfono ya asociado')
				return "El telefono ya esta asociado a un usuario",False
		except mariadb.Error as error:
			print("Error: {}".format(error))
			print("Error al enlazar telefono")
			traceback.print_exc(file=sys.stdout)
			return "Error al asociar",False

	def addSmartphone(self, uid, smartphoneDescription, smartphoneHostname, useSmartphoneIP):
		try:
			self._cursor.execute("INSERT INTO Smartphone (UID,SmartphoneDescription,SmartphoneHostname,UseSmartphoneIP) VALUES (%s,%s,%s,%s)", (uid,smartphoneDescription, smartphoneHostname, useSmartphoneIP))
			self._mariadb_connection.commit()
			return True
		except mariadb.Error as error:
			print("Error: {}".format(error))
			return False

	def updateSmartphone(self, uid, smartphoneDescription, smartphoneHostname, useSmartphoneIP):
		try:
			self._cursor.execute("""UPDATE Smartphone SET SmartphoneDescription=%s, SmartphoneHostname=%s, UseSmartphoneIP=%s WHERE UID=%s""", (smartphoneDescription,smartphoneHostname,useSmartphoneIP,uid))
			self._mariadb_connection.commit()
			return True
		except mariadb.Error as error:
			print("Error: {}".format(error))
			return False

	def newUser(self, user, passwd, description, ip):
		passwordEncrypted = self._encryptPassword(passwd)
		try:
			self._cursor.execute("INSERT INTO User (Username,Password,Description) VALUES (%s,%s,%s)", (user,passwordEncrypted, description))
			self._mariadb_connection.commit()
			print("The last inserted id was: ", self._cursor.lastrowid)
			self._addIp(user, ip)
			return True
		except mariadb.Error as error:
			print("Error: {}".format(error))
			return False

	def changePassword(self, username, newPassword):
		passwordEncrypted = self._encryptPassword(newPassword)
		self._cursor.execute("""UPDATE User SET Password=%s WHERE Username=%s""", (passwordEncrypted, username))
		self._mariadb_connection.commit()

	def logoutAllUsers(self):
		self._cursor.execute("""UPDATE User SET ClientHostname=%s, Attached=%s""", (None, '0'))
		self._mariadb_connection.commit()

	def logout(self, user):
		self._cursor.execute("""UPDATE User SET ClientHostname=%s WHERE Username=%s""", (None, user))
		self._mariadb_connection.commit()

	def logoutHome(self, user):
		self._cursor.execute("""UPDATE User SET ClientHostname=%s, Attached=%s WHERE Username=%s""", (None, 0, user))
		self._mariadb_connection.commit()

	def countDevicesAtHome(self):
		try:
			count = None
			self._cursor.execute("SELECT COUNT(*) FROM User WHERE Attached=%s", (1,))
			count = self._cursor.fetchone()[0]
			return count
		except mariadb.Error as error:
			return None

	def close(self):
		self._mariadb_connection.close()

	#private functions
	def _encryptPassword(self, password):
		sha_signature = hashlib.sha256(password.encode()).hexdigest()
		return sha_signature

	def _checkPassword(self, dbPass, userPass):
		return dbPass == hashlib.sha256(userPass.encode()).hexdigest()
	
	def _addIp(self, user, ip):
		self._cursor.execute("""UPDATE User SET ClientHostname=%s, Attached=%s WHERE Username=%s""", (ip, '1', user))
		self._mariadb_connection.commit()

	
