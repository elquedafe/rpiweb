from gpiozero import DistanceSensor
from time import sleep

class DISTANCEHANDLER:
	def __init__(self):
		self._sensor = DistanceSensor(15,14, max_distance=4)

	def distance(self):
		try:
			return self._sensor.distance
		except Exception as e:
			print(str(e))
			return None