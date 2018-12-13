import sys
import time
import gpiozero as gpi

class DISPLAY:
	def __init__(self):
		'''
		self._array4digit = [
			[0,0,1,1,1,1,1,1],
			[0,0,0,0,0,1,1,0],
			[0,1,0,1,1,0,1,1],
			[0,1,0,0,1,1,1,1],
			[0,1,1,0,0,1,1,0],
			[0,1,1,0,1,1,0,1],
			[0,1,1,1,1,1,0,1],
			[0,0,0,0,0,1,1,1],
			[0,1,1,1,1,1,1,1],
			[0,1,1,0,1,1,1,1]
		]
		'''
		self._array4digit = [
			[0,0,1,1,1,1,1,1],
			[0,0,0,0,0,1,1,0],
			[0,1,0,1,1,0,1,1],
			[0,1,0,0,1,1,1,1],
			[0,1,1,0,0,1,1,0],
			[0,1,1,0,1,1,0,1],
			[0,1,1,1,1,1,0,1],
			[0,0,0,0,0,1,1,1],
			[0,1,1,1,1,1,1,1],
			[0,1,1,0,0,1,1,1]
		]
		"""
		self._array4digit = [
			[1,0,0,0,0,0,1,0],
			[0,1,0,0,0,1,1,1],
			[1,0,0,1,1,1,0,1],
			[1,1,0,1,0,1,0,1],
			[1,1,0,0,0,1,1,0],
			[1,1,0,1,0,0,1,1],
			[1,1,0,1,1,0,1,1],
			[0,1,0,0,0,1,0,1],
			[1,1,0,1,1,1,1,1],
			[1,1,0,0,0,1,1,1]
		"""
		self._d1 = gpi.LED(17)
		self._d2 = gpi.LED(27)
		#self._d3 = gpi.LED(22)
		#self._d4 = gpi.LED(23)
		self._a = gpi.LED(22)
		self._b = gpi.LED(6)
		self._c = gpi.LED(26)
		self._d = gpi.LED(13)
		self._e = gpi.LED(12)
		self._f = gpi.LED(5)
		self._g = gpi.LED(23)
		self._dp = gpi.LED(16)
		self._digits = [self._d1, self._d2]
		self._segments = [self._dp, self._g, self._f, self._e, self._d, self._c, self._b, self._a]
		#self._segments = [self._a, self._b, self._c, self._d, self._e, self._f, self._g, self._dp]
		i=0
		for i in range(len(self._digits)):
			self._digits[i].on()
		i=0
		for i in range(len(self._segments)):
			self._segments[i].off()

	def digit2display(self, digit, dis):
		if (digit > -1 and digit < 10):
			if dis == 1:
				self._d1.off()
				self._d2.on()
				#self._d3.on()
				#self._d4.on()
			elif dis == 2:
				self._d1.on()
				self._d2.off()
				#self._d3.on()
				#self._d4.on()
			elif dis == 3:
				self._d1.on()
				self._d2.on()
				#self._d3.off()
				#self._d4.on()
			elif dis == 4:
				self._d1.on()
				self._d2.on()
				#self._d3.on()
				#self._d4.off()
			i = 0
			for i in range(len(self._array4digit[digit])):
				#self._segments[i].on()
				#time.sleep(2)
				if self._array4digit[digit][i] == 0:
					self._segments[i].off()
				elif self._array4digit[digit][i] == 1:
					self._segments[i].on()
				
	def minusSign(self):
		self._g.on()



