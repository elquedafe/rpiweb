import sys
import time
import configparser
import proxy
import datetime

def escribirLecturas(p):
	wEvent = open("lecturas.txt", "a") #w=sobreescribir
	i=0
	t = None
	h = None
	try:
		try:
			(t,h) = p.leerTemHume()
		except Exception as e:
			print(str(e))
		if ( (t!=None) and (h!=None) ):
			wEvent.write(format(datetime.datetime.now())+"\t"+str(t)+"\t"+str(h)+"\n")
			#print("Escritura correcta")
		else:
			print("ERROR: Lectura fallida")
	finally:
		if wEvent is not None:
			wEvent.close()

def main (args):
	p = proxy.PROXY()
	escribirLecturas(p)

if __name__ == "__main__":
    a=main(sys.argv)
    sys.exit(a)