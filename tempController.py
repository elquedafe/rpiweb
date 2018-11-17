import sys
import socket
import threading
import datetime
import time

import fileHandler
import proxy
from gpiozero import LED

import telepot


def serverThread(cond):
	socket_s = socket.socket()
	socket_s.bind(('127.0.0.1', 65000))
	socket_s.listen(1)
	while (1):
		conn, addr = socket_s.accept()
		global collected

		try:
			while (1):
				data = conn.recv(1024)
				if (data):
					cond.acquire()
					collected = data.decode()
					cond.notify()
					cond.release()
					break;
		except Exception as e:
			print(e)
		finally:
			conn.close()	

def robotThread(cond):
	global collected
	global telToken
	global telGroup
	#var to write events
	wEvent = open("eventos.txt", "a")
	#creating sensor
	sensor = proxy.PROXY()
	#led
	global led
	if (mode == 'automatico'):
		#var to send messages
		#bot = telepot.Bot(telToken)
		
		#notification control
		notification = False
		cond.acquire()
		while collected == None:
			cond.notify()
			cond.release()
			temp = sensor.leerTem()
			if (tempMax > temp):
				if (notification == False):
					#bot.sendMessage(telGroup, 'se enciende la calefaccion --- temperatura actual: '+str(temp)+'ºC'+"\n")
					notification = True
					led.on()
					wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tencendido")
			
			if (tempMax < temp):
				if notification:
					led.off()
					wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tapagado")
					#bot.sendMessage(telGroup, 'se apaga la calefaccion --- temperatura actual: '+str(temp)+'ºC'+"\n")
					notification = False
			time.sleep(lec);
			cond.acquire()

		cond.notify()
		cond.release()
	else:
		cond.acquire()
		while collected == None:
			cond.wait()

		if collected == 'x00x01':
			led.on()
		elif collected == 'x00x02':
			led.off()

		#reset collected data
		collected = None
		#collected = None
		cond.release()
	#closing sensor at the end
	sensor.close()

tempMin = None
tempMax = None
hume = None
telToken = None
telGroup = None
email = None
lec = None
mode = None
collected = None
led = LED(18)

def main (args):
	#var to read from config file
	fileH = fileHandler.FILEHANDLER()

	try:
		global collected
		global cond

		cond = threading.Condition()

		serv = threading.Thread(target=serverThread, args=(cond,))
		serv.start()
		while 1:
			try:
			#update params in control.ini file
			if (collected[:6] == 'x00x03'):
				fileH.writeParam('TempMin', collected[10:11])
				fileH.writeParam('TempMax', collected[15:16])
			#reading config parameters
			global tempMin
			tempMin = float(fileH.readParam('TempMin'))
			global tempMax
			tempMax = float(fileH.readParam('TempMax'))
			global hume
			hume = float(fileH.readParam('Hume'))
			global email
			email = fileH.readParam('Email')
			global telToken
			telToken = fileH.readParam('TelegramToken')
			global telGroup
			telGroup = fileH.readParam('TelegramIDGrupo')
			global lec
			lec = float(fileH.readParam('IntervaloLectura'))
			global mode
			mode = fileH.readParam('Modo')
			if (mode == 'automatico'):
				collected = None
			
			#multithreading app
				#var that controls robot loop
			
			robot = threading.Thread(target=robotThread, args=(cond,))
			robot.start()
			robot.join()

		serv.join()
	except Exception as e:
		print (e)


if __name__ == "__main__":
    a=main(sys.argv)
    sys.exit(a)