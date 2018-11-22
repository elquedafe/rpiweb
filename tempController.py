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
					print(collected)
					cond.notify()
					cond.release()
					break;
		except Exception as e:
			print(e)
		finally:
			conn.close()	

def robotStateChange(persona=None):
	#global variables needed
	global collected
	global led
	global noti
	global bot
	global telGroup
	global temp

	wEvent = open("eventos.txt", "a") #var to write events

	if (collected == 'x00x01' or collected == 'x00x02'):
		fileH = fileHandler.FILEHANDLER()
		fileH.writeParam('Modo', 'manual')
		wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tcambio a modo manual\n")

	elif (collected == 'x00x04'):
		fileH = fileHandler.FILEHANDLER()
		fileH.writeParam('Modo', 'automatico')
		noti.sendNotification('Calefaccion automatica activada --- temperatura actual: '+str(temp)+' Celsius '+str(datetime.datetime.now()), bot, telGroup, persona)
		wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tcambio a modo automatico\n")

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

def robotThread(cond):
	#global variables needed for the robot to run
	global bot
	global temp

	sensor = proxy.PROXY() #creating sensor
	global led
	global noti

	#robot tasks
	if (mode == 'automatico'):
		#robot starts processing information
		bot = telepot.Bot(telToken) #var to send messages
		
		notification = False #number of notifications is limit to 1 per on/off
		cond.acquire()
		while collected == None:
			cond.notify()
			cond.release()
			temp = sensor.leerTem()
			wEvent = open("eventos.txt", "a") #var to write events
			if (tempMax > temp):
				if (notification == False):
					noti.sendNotification('Manual: se enciende la calefaccion --- temperatura actual: '+str(temp)+' Celsius '+str(datetime.datetime.now()), bot, telGroup, persona)
					notification = True
					led.on()
					wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tencendido\n")
			
			if (tempMax < temp):
				if notification:
					led.off()
					wEvent.write(format(datetime.datetime.now())+"\t"+str(temp)+"\tapagado\n")
					noti.sendNotification('Manual: se apaga la calefaccion --- temperatura actual: '+str(temp)+' Celsius '+str(datetime.datetime.now()), bot, telGroup, persona)
					notification = False
			wEvent.close()
			time.sleep(lec);
			cond.acquire()

		cond.notify()
		cond.release()
	else:
		#manual mode
		#wait for user interaction
		cond.acquire()
		while collected == None:
			cond.wait()
		cond.release()

	temp = sensor.leerTem()
	robotStateChange()
	#closing sensor at the end
	sensor.close()


# Logica de comandos de Telegram
def lecturaMensajesBot(msg):
	global bot
	global collected
	#telGroup = int(telGroup)
	firstName = msg['from']['first_name']
	idUser = msg['from']['id']
	lastName = msg['from']['last_name']
	userName = msg['from']['username']
	texto = msg['text'] #Mensaje escrito por el usuario
	persona = firstName+" "+lastName+" --> ("+userName+")"

	if(texto[0] == '/'):
		if (texto == '/on_calefaccion' or texto == '/on_calefaccion@mayordomoetsist_bot'):
			collected = 'x00x01'
			robotStateChange(persona)
		elif (texto == '/off_calefaccion' or texto == '/off_calefaccion@mayordomoetsist_bot'):
			collected = 'x00x02'
			robotStateChange(persona)
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
			robotStateChange(persona)
		else:
			bot.sendMessage(telGroup, "Comando: "+texto+" no valido. Accionado por "+persona)

#params read from control.ini
temp = None
tempMin = None
tempMax = None
hume = None
telToken = None
telGroup = None
email = None
lec = None
mode = None
'''
Collected is used to switch between modes and to store the data transfered from webServer
x00x01 --> turn on led
x00x02 --> turn off led
x00x03 --> read again temp parameters
x00x04 --> change from manual to auto with telegram
'''
collected = None
led = LED(18)
bot = None
noti = None

def main (args):
	#var to read from config file
	fileH = fileHandler.FILEHANDLER()
	global noti
	noti = notificationHandler.NOTIFICATIONHANDLER()

	try:
		global collected
		global cond

		global telToken
		telToken = fileH.readParam('telegramtoken')
		global telGroup
		telGroup = fileH.readParam('telegramidgrupo')
		global bot
		bot = telepot.Bot(telToken)
		#activa lecturas de comandos por parte del bot
		MessageLoop(bot, lecturaMensajesBot).run_as_thread()
		
		cond = threading.Condition()
		serv = threading.Thread(target=serverThread, args=(cond,))
		serv.start()
		while 1:
			try:
				#reading config parameters
				global tempMin
				tempMin = float(fileH.readParam('tempmin'))
				global tempMax
				tempMax = float(fileH.readParam('tempmax'))
				global hume
				hume = float(fileH.readParam('hume'))
				global email
				email = fileH.readParam('email')
				#telegram variables
				telToken = fileH.readParam('telegramtoken')
				telGroup = fileH.readParam('telegramidgrupo')

				global lec
				lec = float(fileH.readParam('intervalolectura'))
				global mode
				mode = fileH.readParam('modo')
				if (mode == 'automatico'):
					collected = None
				
				robot = threading.Thread(target=robotThread, args=(cond,))
				robot.start()
				robot.join()
			except telepot.exception.TelegramError as e:
				print(e)

		serv.join()
	except Exception as e:
		print (e)


if __name__ == "__main__":
    a=main(sys.argv)
    sys.exit(a)