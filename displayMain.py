import sys
import time
import display

def main (args):
	'''
	try:
		d1 = gpi.LED(17)
		d2 = gpi.LED(27)
		d3 = gpi.LED(22)
		d4 = gpi.LED(23)
		a = gpi.LED(24)
		b = gpi.LED(5)
		c = gpi.LED(6)
		d = gpi.LED(12)
		e = gpi.LED(13)
		f = gpi.LED(16)
		g = gpi.LED(26)
		dp = gpi.LED(25)
		digits = {d1, d2, d3, d4}
		segments = {a, b, c, d, e, f, g, dp}
		print('init: pongo a uno los digitos')
		for digit in digits:
			digit.on()
		print('init: pongo a cero los segmentos')
		for segment in segments:
			segment.off()
		print('entro en el bucle')
		while True:
			for digit in digits:
				print('aviso al display y enciendo todos los segmentos')
				digit.off()
				for segment in segments:
					segment.on()
				time.sleep(1)
				digit.on()
	except KeyboardInterrupt:
		print('fin del programa')
	'''
	dis = display.DISPLAY()
	try:
		while True:
			for i in range(0,10):
				print(i)
				dis.digit2display(i, 2)
				time.sleep(1)
	except KeyboardInterrupt:
		print('fin programa')

if __name__ == "__main__":
	a=main(sys.argv)
	sys.exit(a)