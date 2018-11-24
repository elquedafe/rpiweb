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

	def changePassword(self, username, newPassword):
		passwordEncrypted = self._encryptPassword(newPassword)
		self._cursor.execute("""UPDATE User SET Password=%s WHERE Username=%s""", (passwordEncrypted, username))
		self._mariadb_connection.commit()


	def _encryptPassword(self, password):
		sha_signature = hashlib.sha256(password.encode()).hexdigest()
		return sha_signature

	def _checkPassword(self, dbPass, userPass):
		return dbPass == hashlib.sha256(userPass.encode()).hexdigest()
	
	def _addIp(self, user, ip):
		self._cursor.execute("""UPDATE User SET ClientHostname=%s, Attached=%s WHERE Username=%s""", (ip, '1', user))
		self._mariadb_connection.commit()

	def logout(self, user):
		self._cursor.execute("""UPDATE User SET ClientHostname=%s, Attached=%s WHERE Username=%s""", (None, '0', user))
		self._mariadb_connection.commit()

	def close(self):
		self._mariadb_connection.close()
