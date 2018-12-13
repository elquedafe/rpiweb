import sys
import socket
import threading
import datetime
import time

import fileHandler
import notificationHandler
import distanceHandler
import proxy
import userHandler
import audioHandler
import bulbHandler
import webSensor
import micHandlerTest
import display
from webSensor import nfcAddUserList
from MFRC522python import Read
from gpiozero import LED
import signal
import telepot
from telepot.loop import MessageLoop



def end(signal,frame):
	print('CTRL+C catched')
	uH = userHandler.USERHANDLER()

	try:
		uH.logoutAllUsers()
	except Exception as e:
		print(str(e))
	finally:
		uH.close()
		sys.exit(0)

signal.signal(signal.SIGINT, end)


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

def robotStateChange(cond, kill, persona=None):
	#global variables needed
	global alarmSet
	global collected
	global led
	global noti
	global bot
	global telGroup
	global temp
	global mode
	global notification
	global killAlarm
	#print('Temperatura: '+str(temp)+' -- '+'modo: '+str(mode)+' --- ')

	cond.acquire()
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
	elif collected == 'x00x06':
		wEvent.write(format(datetime.datetime.now())+"\tAlarma activada\n")
		noti.sendNotification('La alarma ha sido activada. Puedes ver que esta sucediendo en: http://192.168.1.102:5000/menu/video '+str(datetime.datetime.now()), bot, telGroup)
		if(alarmSet == False):
			alarm()
	elif collected == 'x00x07':
		wEvent.write(format(datetime.datetime.now())+"\tAlarma desactivada\n")
		alarmSet = False
		killAlarm.set()
		noti.sendNotification('La alarma ha sido desactivada. '+str(datetime.datetime.now()), bot, telGroup)
	elif collected == 'x00x08':
		print('*NOTIFICAR ENTRADA CON TARJETA*')
		print(str(persona))
		#wEvent.write(format(datetime.datetime.now())+"\t"+persona+" ha entrado a casa con tarjeta NFC\n")
		noti.sendNotification(persona+' ha entrado en casa con tarjeta nfc. '+str(datetime.datetime.now()), bot, telGroup)
	elif collected == 'x00x09':
		print('*NOTIFICAR SALIDA CON TARJETA*')
		wEvent.write(format(datetime.datetime.now())+"\t"+persona+" ha salido de casa con tarjeta NFC\n")
		noti.sendNotification(persona+' ha salido de casa con tarjeta nfc. '+str(datetime.datetime.now()), bot, telGroup)
	elif collected == 'x00x0A':
		print('*NOTIFICAR ENTRADA CON SMARTP*')
		wEvent.write(format(datetime.datetime.now())+"\t"+persona+" ha entrado a casa con smartphone\n")
		noti.sendNotification(persona+' ha entrado a casa con smartphone. '+str(datetime.datetime.now()), bot, telGroup)
	elif collected == 'x00x0B':
		print('*NOTIFICAR SALIDA CON SMARTP*')
		wEvent.write(format(datetime.datetime.now())+"\t"+persona+" ha salido de casa con smartphone\n")
		noti.sendNotification(persona+' ha salido de casa con smartphone. '+str(datetime.datetime.now()), bot, telGroup)
	elif collected == 'x00x0C':
		led.on()
		wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tencendido\n")
		noti.sendNotification('Auto: se enciende la calefaccion --- temperatura actual: '+str(temp)+' Celsius '+str(datetime.datetime.now()), bot, telGroup)
		notification = True
	elif collected == 'x00x0D':
		led.off()
		wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tapagado\n")
		noti.sendNotification('Auto: se apaga la calefaccion --- temperatura actual: '+str(temp)+' Celsius '+str(datetime.datetime.now()), bot, telGroup)
		notification = False
	wEvent.close()
	#reset collected data
	collected = None
	cond.release()

def robotThread(cond, kill):
	time.sleep(1)
	#global variables needed for the robot to run
	global bot
	global temp
	global led
	global noti
	global collected
	global notification
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
				if (tempMax > temp):
					if (notification == False):
						collected = 'x00x0C'

				
				if (tempMax < temp):
					if notification:
						collected = 'x00x0D'						
				
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

		robotStateChange(cond, kill) #change state
	print('termina hilo robot')

# Logica de comandos de Telegram
def lecturaMensajesBot(msg):
	global bot
	global collected
	global alarmSet
	global kill
	global cond
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
				robotStateChange(cond, None, persona)
			elif (texto == '/off_calefaccion' or texto == '/off_calefaccion@mayordomoetsist_bot'):
				collected = 'x00x02'
				robotStateChange(cond, None, persona)
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
				robotStateChange(cond, None, persona)
			elif (texto == '/activar_alarma' or texto == '/activar_alarma@mayordomoetsist_bot'):
				print('activada alarma en bot')
				collected = 'x00x06'
				#alarmSet = False
				robotStateChange(cond, None, persona)
			elif (texto == '/desactivar_alarma' or texto == '/desactivar_alarma@mayordomoetsist_bot'):
				collected = 'x00x07'
				led.off()
				#alarmSet = False
				robotStateChange(cond, None, persona)
			else:
				bot.sendMessage(telGroup, "Comando: "+texto+" no valido. Accionado por "+persona)

def distanceThread(cond, kill):
	global alarmSet
	global collected
	print('distance thread')
	distanceHand = distanceHandler.DISTANCEHANDLER()
	while not kill.is_set():
		distance = distanceHand.distance()
		if(distance != 0.0):
			print(str(distance)+'m')
			if((distance <= 1.5) and (alarmSet==False)):
				uH = userHandler.USERHANDLER()
				try:
					nConnectedDevices = uH.countDevicesAtHome()
				finally:
					uH.close()
				#If nobody is at home
				if(nConnectedDevices == 0):
					collected = 'x00x06'
					robotStateChange(cond, collected)
			time.sleep(1)

def alarm():
	global alarmSet
	global bot
	global noti
	global killAlarm
	alarmSet = True
	print("alarma activada")
	killAlarm = threading.Event()
	audThr = threading.Thread(target=audioThread, args=(killAlarm,))
	lightThr = threading.Thread(target=alarmLightThread, args=(killAlarm,))

	audThr.start()
	lightThr.start()

def audioThread(killAlarm):
	global alarmSet
	while(not killAlarm.is_set()):
		audioHandler.playRob()

def alarmLightThread(killAlarm):
	global alarmSet
	while(not killAlarm.is_set()):
		bulbHandler.blink(0.3)

	
def servWebThread(cond, kill):
	global serverweb
	serverweb = webSensor.WEBSENSOR()
	if serverweb != None:
		print('webserv instancado')
	else:
		print('webNO instancado')

def nfcThread(cond, kill):
	global serverwebgl
	global collected
	while(not kill.is_set()):
		collected, user = Read.read(webSensor)
		if(collected != None):
			robotStateChange(cond, None, user)

def voiceThread(cond, kill):
	global sensor
	micHandlerTest.recognizer(sensor)

def displayThread(cond, kill):
	time.sleep(3)
	global temp
	print("hilo display, estoy vivo")
	dis = display.DISPLAY()
	while(not kill.is_set()):
		decena = int(temp/10)
		unidad = int(temp) - (decena*10)
		dis.digit2display(decena, 1)
		time.sleep(0.003)
		dis.digit2display(unidad, 2)
		time.sleep(0.003)

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
x00x06 --> alarm activation
x00x07 --> alarm deactivation
x00x08 --> NFC entrance
x00x09 --> NFC exit
x00x0A --> Smartphone entrance
x00x0B --> Smartphone exit
x00x0C --> Enciende calefaccioin auto
x00x0D --> Apaga calefaccion auto
'''
collected = None
led = LED(18) #GPIO
bot = None #telegram
noti = None #all notifications
alarmSet = False
killAlarm = None
kill = None
serverweb = None
sensor = None
notification = False
cond = None
def main (args):
	global collected
	global cond #needed for thread sync
	global noti
	global kill
	global sensor
	global cond
	try:
		led.off()
		fileH = fileHandler.FILEHANDLER() #var to read from config file
		noti = notificationHandler.NOTIFICATIONHANDLER()
		
		#the main thread will be reading temp
		global temp
		sensor = proxy.PROXY() #creating sensor

		kill = threading.Event()
		#initializing telegram thread
		global telToken
		telToken = fileH.readParam('telegramtoken')
		global telGroup
		telGroup = fileH.readParam('telegramidgrupo')
		global bot
		bot = telepot.Bot(telToken)
		
		#initializing the rest of the threads
		#starting the other threads
		cond = threading.Condition()
		#starting telegram thread
		MessageLoop(bot, lecturaMensajesBot).run_as_thread()
		servWeb = threading.Thread(target=servWebThread, args=(cond, kill))
		serv = threading.Thread(target=serverThread, args=(cond, kill,)) #thread which communicates with web server
		robot = threading.Thread(target=robotThread, args=(cond, kill))
		#distance = threading.Thread(target=distanceThread, args=(cond, kill))
		nfc = threading.Thread(target=nfcThread, args=(cond, kill))
		#voice = threading.Thread(target=voiceThread, args=(cond, kill))
		#displayT = threading.Thread(target=displayThread, args=(cond, kill))

		servWeb.start()
		serv.start()
		robot.start()
		#distance.start()
		nfc.start()
		#voice.start()
		#displayT.start()

		
		while (not kill.is_set()):
			temp = sensor.leerTem()
			time.sleep(1)
			
		sensor.close()
		print('sale bucle en el main')
		
		#finish the program
		servWeb.join()
		serv.join()
		robot.join()
		#distance.join()
		nfc.join()
		#voice.join()
		#displayT.join()

	except Exception as e:
		print (e)


if __name__ == "__main__":
    a=main(sys.argv)
    sys.exit(a)