import configparser

class FILEHANDLER:
	def __init__(self):
		self._config = configparser.ConfigParser()

	def readParam(self, param):
		self._config.read("control.ini")
		return self._config['Parameters'][param]

	def writeParam(self, param, value):
		self._config.read("control.ini")
		self._config.set('Parameters', param, value)
		with open('control.ini', 'w') as configfile:
			self._config.write(configfile)