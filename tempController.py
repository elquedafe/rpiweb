import sys
import socket
import threading
import datetime
import time

import fileHandler
import notificationHandler
import proxy
from gpiozero import LED

import telepot
from telepot.loop import MessageLoop


def serverThread(cond, kill):
	time.sleep(1)
	socket_s = socket.socket()
	socket_s.bind(('127.0.0.1', 65000))
	socket_s.listen(1)
	while (not kill.is_set()):
		conn, addr = socket_s.accept()
		global collected

		try:
			while (1):
				data = conn.recv(1024)
				if (data):
					cond.acquire()
					collected = data.decode()
					print(collected)
					print('el server manda despertar')
					cond.notify()
					cond.release()
					break
		except Exception as e:
			print(e)
		finally:
			conn.close()

	print('termina hilo server')	

def robotStateChange(kill, persona=None):
	#global variables needed
	global collected
	global led
	global noti
	global bot
	global telGroup
	global temp
	global mode

	print('Temperatura: '+str(temp)+' -- '+'modo: '+mode+' --- ')

	wEvent = open("eventos.txt", "a") #var to write events
	fileH = fileHandler.FILEHANDLER()

	if (collected == 'x00x01' or collected == 'x00x02'):
		fileH.writeParam('Modo', 'manual')
		wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tcambio a modo manual\n")

	elif (collected == 'x00x04'):
		fileH.writeParam('Modo', 'automatico')
		noti.sendNotification('Calefaccion automatica activada --- temperatura actual: '+str(temp)+' Celsius '+str(datetime.datetime.now()), bot, telGroup, persona)
		wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tcambio a modo automatico\n")
	
	elif (collected == 'x00x05'):
		kill.set()

	if collected == 'x00x01':
		led.on()
		noti.sendNotification('Manual: se enciende la calefaccion --- temperatura actual: '+str(temp)+' Celsius '+str(datetime.datetime.now()), bot, telGroup, persona)
		wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tencendido\n")
	elif collected == 'x00x02':
		led.off()
		noti.sendNotification('Manual: se apaga la calefaccion --- temperatura actual: '+str(temp)+' Celsius '+str(datetime.datetime.now()), bot, telGroup, persona)
		wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tencendido\n")
	elif collected == 'x00x03':
		led.off() #momentaneamente
		noti.sendNotification('Cambio de modo desde el servidor --- temperatura actual: '+str(temp)+' Celsius '+str(datetime.datetime.now()), bot, telGroup, persona)
		wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tcambio de modo desde el servidor web\n")

	wEvent.close()
	#reset collected data
	collected = None

def robotThread(cond, kill):
	time.sleep(1)
	#global variables needed for the robot to run
	global bot
	global temp
	global led
	global noti

	#var to read from config file
	fileH = fileHandler.FILEHANDLER()

	while (not kill.is_set()):
		#read parameters
		tempMin = float(fileH.readParam('tempmin'))
		tempMax = float(fileH.readParam('tempmax'))
		hume = float(fileH.readParam('hume'))
		#reading notification variables
		global telToken
		telToken = fileH.readParam('telegramtoken')
		global telGroup
		telGroup = fileH.readParam('telegramidgrupo')
		noti.readParameters()
		#reading time interval
		lec = float(fileH.readParam('intervalolectura'))
		#reading mode
		global mode
		mode = fileH.readParam('modo')
		
		#robot tasks
		if (mode == 'automatico'):
			#robot starts processing information
			bot = telepot.Bot(telToken) #var to send messages
			
			notification = False #number of notifications is limit to 1 per on/off
			cond.acquire()
			while collected == None:
				cond.notify()
				cond.release()
				wEvent = open("eventos.txt", "a") #var to write events
				if (tempMax > temp):
					if (notification == False):
						noti.sendNotification('Auto: se enciende la calefaccion --- temperatura actual: '+str(temp)+' Celsius '+str(datetime.datetime.now()), bot, telGroup)
						notification = True
						led.on()
						wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tencendido\n")
				
				if (tempMax < temp):
					if notification:
						led.off()
						wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tapagado\n")
						noti.sendNotification('Auto: se apaga la calefaccion --- temperatura actual: '+str(temp)+' Celsius '+str(datetime.datetime.now()), bot, telGroup)
						notification = False
				wEvent.close()
				time.sleep(lec)
				cond.acquire()

			cond.notify()
			cond.release()
		else:
			#manual mode
			#wait for user interaction
			cond.acquire()
			while collected == None:
				print('voy a dormir')
				cond.wait()
			print('estoy despierto')
			cond.release()

		robotStateChange(kill) #change state
	print('termina hilo robot')

# Logica de comandos de Telegram
def lecturaMensajesBot(msg, kill):
	global bot
	global collected
	#telGroup = int(telGroup)
	firstName = msg['from']['first_name']
	idUser = msg['from']['id']
	lastName = msg['from']['last_name']
	userName = msg['from']['username']
	texto = msg['text'] #Mensaje escrito por el usuario
	persona = firstName+" "+lastName+" --> ("+userName+")"
	if (not kill.is_set()):
		if(texto[0] == '/'):
			if (texto == '/on_calefaccion' or texto == '/on_calefaccion@mayordomoetsist_bot'):
				collected = 'x00x01'
				robotStateChange(None, persona)
			elif (texto == '/off_calefaccion' or texto == '/off_calefaccion@mayordomoetsist_bot'):
				collected = 'x00x02'
				robotStateChange(None, persona)
			elif (texto == '/obtener_estadisticas' or texto == '/obtener_estadisticas@mayordomoetsist_bot'):
				try:
					bot.sendPhoto(telGroup, open('templates/img/temperatura.png','rb'))
				except Exception as e:
					bot.sendMessage(telGroup, 'No se han podido enviar las estadisticas de temperatura')
					print(str(e))
				try:
					bot.sendPhoto(telGroup, open('templates/img/humedad.png','rb'))
				except Exception as e:
					bot.sendMessage(telGroup, 'No se han podido enviar las estadisticas de humedad')
					print(str(e))
			elif (texto == '/obtener_registros' or texto == '/obtener_registros@mayordomoetsist_bot'):
				try:
					bot.sendDocument(telGroup, open('eventos.txt','rb'))
				except Exception as e:
					bot.sendMessage(telGroup, 'No se han podido enviar los registros de los eventos')
					print(str(e))
			elif (texto == '/calefaccion_auto' or texto == '/calefaccion_auto@mayordomoetsist_bot'):
				collected = 'x00x04'
				robotStateChange(None, persona)
			else:
				bot.sendMessage(telGroup, "Comando: "+texto+" no valido. Accionado por "+persona)

mode = None
temp = None
#params read from control.ini needed in children threads
telToken = None
telGroup = None
'''
Collected is used to switch between modes and to store the data transfered from webServer
x00x01 --> turn on led
x00x02 --> turn off led
x00x03 --> read again temp parameters
x00x04 --> change from manual to auto with telegram
x00x05 --> kill the program
'''
collected = None
led = LED(18) #GPIO
bot = None #telegram
noti = None #all notifications

def main (args):
	global collected
	global cond #needed for thread sync
	global noti
	
	try:
		fileH = fileHandler.FILEHANDLER() #var to read from config file
		noti = notificationHandler.NOTIFICATIONHANDLER()

		kill = threading.Event()
		#initializing telegram thread
		global telToken
		telToken = fileH.readParam('telegramtoken')
		global telGroup
		telGroup = fileH.readParam('telegramidgrupo')
		global bot
		bot = telepot.Bot(telToken)
		#starting telegram thread
		MessageLoop(bot, lecturaMensajesBot).run_as_thread(kill)
		
		#initializing the rest of the threads
		#starting the other threads
		cond = threading.Condition()
		serv = threading.Thread(target=serverThread, args=(cond, kill,)) #thread which communicates with web server
		robot = threading.Thread(target=robotThread, args=(cond, kill))

		serv.start()
		robot.start()

		#the main thread will be reading temp
		global temp
		sensor = proxy.PROXY() #creating sensor

		while (not kill.is_set()):
			temp = sensor.leerTem()
			time.sleep(1)
		sensor.close()
		print('sale bucle en el main')
		#finish the program
		serv.join()
		robot.join()
	except Exception as e:
		print (e)


if __name__ == "__main__":
    a=main(sys.argv)
    sys.exit(a)