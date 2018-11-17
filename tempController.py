import sys
import socket
import threading
import datetime
import time

import configparser
import proxy
from gpiozero import LED

import telepot


def serverThread():
	socket_s = socket.socket()
	socket_s.bind(('localhost', 65000))
	socket_s.listen(1)
	conn, addr = socket_s.accept()
	while 1:
		data = conn.recv(1024)
		if data=='on' or data=='off':
			lock.adquire()
			collected = data
			lock.release()
			break
	conn.close()	

def robotThread(mode):
	#var to write events
	wEvent = open("eventos.txt", "a")
	#creating sensor
	sensor = proxy.PROXY()
	#creating led
	led = LED(18)
	if (mode == 'automatico'):
		#var to send messages
		bot = telepot.Bot("724236915:AAGB0CVTa9tWxjI66Lk4JEWioR_hPoXwdEM")
		
		#notification control
		notification = False
		while collected == None:
			temp = sensor.leerTem()
			if (tempMax > temp):
				if (notification == False):
					bot.sendMessage(-253583374, 'se enciende la calefaccion --- temperatura actual: '+str(temp)+'ºC'+"\n")
					notification = True
					led.on()
					wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tencendido")
			
			if (tempMax < temp):
				if notification:
					led.off()
					wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tapagado")
					bot.sendMessage(-253583374, 'se apaga la calefaccion --- temperatura actual: '+str(temp)+'ºC'+"\n")
					notification = False
			time.sleep(lec);
	else:
		while collected == None:
			notification = False
		if collected == 'on':
			led.on()
		else:
			led.off()
	#closing sensor at the end
	sensor.close()


def main (args):
	#var to read from config file
	config = configparser.ConfigParser()

	try:
		serv = threading.Thread(target=serverThread)
		serv.start()
		while 1:
			config.read("control.ini")
			
			#reading config parameters
			global tempMin
			tempMin = config.getfloat('Parameters', 'TempMin')
			global tempMax
			tempMax = config.getfloat('Parameters', 'TempMax')
			global hume
			hume = config.getfloat('Parameters', 'Hume')
			global email
			email = config['Parameters']['Email']
			global lec
			lec = config.getfloat('Parameters', 'IntervaloLectura')
			global mode
			mode = config['Parameters']['Modo']
			global collected
			collected = None
			#multithreading app
				#var that controls robot loop
			
			lock = threading.Lock()
			robot = threading.Thread(target=robotThread, args=(mode,))
			robot.start()
			robot.join()

		serv.join()
	except Exception as e:
		print (e)


if __name__ == "__main__":
    a=main(sys.argv)
    sys.exit(a)