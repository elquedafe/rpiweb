#!/usr/bin/env python
## Text menu in Python

import am2320
import sys
import time
      
def menu():       ## Your menu design here
    print (30 * "-" , "MENU" , 30 * "-")
    print ("1. Temperature and Humidity")
    print ("2. Temperature")
    print ("3. Humidity")
    print ("0. Salir")
    print (67 * "-")
  

def main(args):
	sensor = am2320.AM2320()  
	
	print ("argumentos", args[1:])
	(t,h) = sensor.leerTemHume()
	print("Humidity: ", h, " %")
	print("Temperature: ", t, "Celsius")
	sensor.close()	
	
if __name__ == "__main__":
    a=main(sys.argv)
    sys.exit(a)
