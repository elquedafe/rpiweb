import configparser

class FILEHANDLER:
	def __init__(self):
		self._config = configparser.ConfigParser()

	def readParam(self, param):
		self._config.read("control.ini")
		return self._config['Parameters'][param]

	def writeParam(self, param):
		self._config.set('Parameters', param)
		with open('control.ini', 'wb') as configfile:
				self._config.write(configfile)
