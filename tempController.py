import sys
import socket
import threading
import datetime
import time

import fileHandler
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


# Logica de comandos de Telegram
def lecturaMensajesBot(msg):
	global telGroup
	firstName = msg['from']['first_name']
	idUser = msg['from']['id']
	lastName = msg['from']['last_name']
	userName = msg['from']['username']
	texto = msg['text'] #Mensaje escrito por el usuario
	persona = firstName+" "+lastName+" --> ("+userName+")"

	if(texto[0] == '/'):
		if (texto == '/on_calefaccion'):
			bot.sendMessage(telGroup, 'Calefaccion encendida por '+ persona)
		elif (texto == '/off_calefaccion'):
			bot.sendMessage(telGroup, 'Calefaccion apagada por '+ persona)
		elif (texto == '/obtener_estadisticas'):
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
		elif (texto == '/obtener_registros'):
			try:
				bot.sendDocument(telGroup, open('eventos.txt','rb'))
			except Exception as e:
				bot.sendMessage(telGroup, 'No se han podido enviar los registros de los eventos')
				print(str(e))
		else:
			bot.sendMessage(telGroup, "Comando: "+texto+" no valido. Accionado por "+persona)


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
bot = None

def main (args):
	#var to read from config file
	fileH = fileHandler.FILEHANDLER()

	try:
		global collected
		global cond

		global telToken
		telToken = fileH.readParam('TelegramToken')
		global telGroup
		telGroup = fileH.readParam('TelegramIDGrupo')
		 #used to cast string to int
		bot = telepot.Bot(telToken)
		#activa lecturas de comandos por parte del bot
		MessageLoop(bot, lecturaMensajesBot).run_as_thread()
		
		cond = threading.Condition()
		serv = threading.Thread(target=serverThread, args=(cond,))
		serv.start()
		while 1:
			try:
				#update params in control.ini file
				#if (collected[:6] == 'x00x03'):
				#	fileH.writeParam('TempMin', collected[10:11])
				#	fileH.writeParam('TempMax', collected[15:16])
				#reading config parameters
				global tempMin
				tempMin = float(fileH.readParam('TempMin'))
				global tempMax
				tempMax = float(fileH.readParam('TempMax'))
				global hume
				hume = float(fileH.readParam('Hume'))
				global email
				email = fileH.readParam('Email')
				telToken = fileH.readParam('TelegramToken')
				telGroup = fileH.readParam('TelegramIDGrupo')
				global lec
				lec = float(fileH.readParam('IntervaloLectura'))
				global mode
				mode = fileH.readParam('Modo')
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