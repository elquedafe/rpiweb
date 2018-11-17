import mysql.connector as mariadb
import pprint
class USERHANDLER:
	def __init__(self):
		try:
			self._mariadb_connection = mariadb.connect(user='mayordomo', password='mayordomo', database='MayordomoETSIST')
			self._cursor = self._mariadb_connection.cursor()
		except Exception as e:
			print(str(e))
			print('No se ha podido conectar a la BBDD')

	def getAccess(self, user, passwd):
		result = False
		query = "SELECT Username, Password FROM User WHERE Username='"+user+"' AND Password='"+passwd+"'"
		self._cursor.execute(query)
		for userDatabase, passwdDatabase in self._cursor:
			if(userDatabase==user and passwdDatabase==passwd):
				result = True
		return result