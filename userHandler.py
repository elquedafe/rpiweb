import mysql.connector as mariadb
import pprint
import hashlib
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
		try:
			self._cursor.execute("SELECT Username, MasterHomeHostname, Attached FROM User WHERE Username=%s", (user,))
			for userDatabase, homeHostameDatabase, attachedDatabase in self._cursor:
				ip = homeHostameDatabase
				if(attachedDatabase == 0):
					self._addIp(user, homeHostameDatabase)
				if(attachedDatabase == 1):
					self.logout(user)
			return user, ip
		except mariadb.Error as error:
			print(str(error))
			print('NFC access denied')
			return user, None

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
		self._cursor.execute("""UPDATE User SET ClientHostname=%s, Attached=%s WHERE Username=%s""", (None, '0', user))
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

	
