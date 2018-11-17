import configparser

class PROXY:
	def __init__(self):
		config = configparser.ConfigParser()
		config.read('config.ini')
		try:
			paquete = config['Parameters']['Paquete']
			modulo = config['Parameters']['Modulo']
			i = __import__(paquete+"."+modulo, fromlist=[''])
			class_ = getattr(i, modulo.upper())
			self._sensor = class_()
		except:
			raise Exception("Error lectura config") 
	def leerTemHume(self):
		return self._sensor.leerTemHume()
	def leerHume(self):
		return self._sensor.leerHume()
	def leerTem(self):
		return self._sensor.leerTem()
	def close(self):
		self._sensor.close()