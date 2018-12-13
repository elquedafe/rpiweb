#System imports
import sys
from flask import Flask, render_template, send_file, redirect, request, Response
import socket
import time
import os
from flask_socketio import SocketIO, send, disconnect, emit
#User imports
import proxy
import userHandler
import dataHandler
import fileHandler
import threading
from MFRC522python import Write, Read
from cameraHandlerTest import Camera

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)
currentTagSocketio = None
currentSmartphoneSocketio = None
killTagThread = None
p = None #Proxy as global variable
#vH = cameraHandler.CAMERAHANDLER() #video handler
usersLogged = {} #dictionary with users currently logged
timers = {}
uid = None
tag = None
tagEscrita = False
tagThread = None
#callback function for timeout
def logoutUser(*args):
	global usersLogged
	ip = str(args[0])

	try:
		user = usersLogged[ip]
		if ip in usersLogged:
			uH = userHandler.USERHANDLER()
			uH.logout(user)
			usersLogged.pop(ip)
			print(ip+' session closed')
	except Exception as e:
		pass
	finally:
		uH.close()
		
def resetTimeout(ip):
	global usersLogged
	global timers
	fH = fileHandler.FILEHANDLER() 

	timers[ip].cancel()#parar el timeout
	timers[ip] = threading.Timer(int(fH.readParam('usertimeout')), logoutUser, [ip]) #crear nuevo timeout
	timers[ip].start() #iniciar timeout

def barraTemp(t):
		tableTemp = '<table><tr>'
		count = 0
		primero = True
		contadorInterno = 0
		while count < 100:
			if (count<(t+40)*100/120):
				tableTemp += '<td style="background-color:#ff6666">&nbsp;</td>'
			else:
				if (t<=70):
					if(primero):
						primero = False
						tableTemp += '<td id="tempNumBarra" style="font-size:13px"><i>'+str(t)+'&deg</i></td>'
					else:
						if (t >= 10.0):
							if(contadorInterno > 4):
								tableTemp += '<td>&nbsp;</td>'
							else:
								contadorInterno=contadorInterno+1
						elif((t > -10.0) & (t < 10.0)):
							if (contadorInterno > 3):
								tableTemp += '<td>&nbsp;</td>'
							else:
								contadorInterno=contadorInterno+1
						elif(t <= -10.0):
							if (contadorInterno > 4):
								tableTemp += '<td>&nbsp;</td>'
							else:
								contadorInterno=contadorInterno+1
				else:
					tableTemp += '<td>&nbsp;</td>'
			count = count+1
		tableTemp += '</tr></table>'
		if(t > 70):
			if t <= 80:
				tableTemp += '<div style="font-size:14px; margin-left:'+str((t+40)*100/120)+'%"><i>'+str(t)+'&deg;C</i></div>'
			else:
				tableTemp += '<div style="font-size:14px; margin-left:100%"><i>'+str(t)+'&deg;C</i></div>'
		return tableTemp

def barraHum(h):
	tableHum = '<table><tr>'
	primero = True
	contadorInterno = 0
	count = 0
	while count < 100:
		if (count<(h)):
			tableHum += '<td style="background-color:#2D3CAA">&nbsp;</td>'
		else:
			if (h<=90):
				if(primero):
					primero = False
					tableHum += '<td id="tempNumBarra" style="font-size:14px"><i>'+str(h)+'%</i></td>'
				else:
					if (h >= 10):
						if(contadorInterno > 5):
							tableHum += '<td>&nbsp;</td>'
						else:
							contadorInterno=contadorInterno+1
					else:
						if(contadorInterno > 4):
							tableHum += '<td>&nbsp;</td>'
						else:
							contadorInterno=contadorInterno+1
			else:
				tableHum += '<td>&nbsp;</td>'
		count = count+1
	tableHum += '</tr></table>'
	if (h>90):
		tableHum += '<div style="font-size:14px; margin-left:'+str(h)+'%"><i>'+str(h)+'%</i></div>'
	return tableHum

def nfcAddUserList(user, ip):
		print('addinf nfc user')
		global usersLogged
		global timers
		if (ip not in usersLogged):
			fH = fileHandler.FILEHANDLER()
			usersLogged[ip] = user
			print(usersLogged)
			timers[ip] = threading.Timer(int(fH.readParam('usertimeout')), logoutUser, [ip])
			timers[ip].start()

def envioNFC_UID(uidFromReader):
	global uid
	uid = uidFromReader
	print('WebServer: obtenido uid del movil' + uid)


def writeTagThread(kill):
	global tag
	global tagEscrita
	global killTagThread
	while (not killTagThread.is_set()):
		print('writeTagThread: Tag que quiero : '+ str(tag))
		tagEscrita = Write.writeTag(tag)
		time.sleep(1)
		print('Tag escrita por el hilo: '+ str(tag))



class WEBSENSOR:			
	def nfcLogoutUserList():
		global usersLogged
		global timers
		usersLogged.pop(ip)
		print(ip+' session closed')
	
	def __init__(self):
		print('init')
		socketio.run(app, host='0.0.0.0')

	#INTERNAL METHODS
	

	#reset function for timeout
	def resetTimeout(ip):
		global usersLogged
		global timers
		fH = fileHandler.FILEHANDLER() 

		timers[ip].cancel()#parar el timeout
		timers[ip] = threading.Timer(int(fH.readParam('usertimeout')), logoutUser, [ip]) #crear nuevo timeout
		timers[ip].start() #iniciar timeout


	#END INTERNAL METHODS

	#ROUTES
	@app.route('/logout')
	def logout():
		global usersLogged
		uH = userHandler.USERHANDLER()
		try:
			user = usersLogged[request.remote_addr]
			ip = request.remote_addr
			if ip in usersLogged:
				uH.logout(user)
				usersLogged.pop(ip)
		except Exception as e:
			pass
		finally:
			uH.close()
		return redirect('/')

	@app.route('/', methods = ['POST', 'GET'])
	def index():
		global usersLogged
		global timers
		accessGranted= False
		if(request.remote_addr in usersLogged):
			accessGranted = True
		if request.method == 'POST':
			print('***POST***')
			user = request.form.get('user')
			passwd = request.form.get('passwd')
			ip = request.remote_addr
			try:
				uH = userHandler.USERHANDLER()
				accessGranted = uH.getAccess(user, passwd, ip)
			except Exception as e:
				print(str(e))
			finally:
				uH.close()
			if (accessGranted):
				fH = fileHandler.FILEHANDLER()
				timers[ip] = threading.Timer(int(fH.readParam('usertimeout')), logoutUser, [ip])
				timers[ip].start()
				usersLogged[ip] = user
				templateData = {
				'warningAccess' : False,
				'accesGranted' : accessGranted,
				'user' : user
				}
				return render_template('index.html', **templateData)
			else:
				templateData = {
				'warningAccess' : True,
				'accesGranted' : accessGranted
				}
				return render_template('index.html', **templateData)
		templateData = {
				'warningAccess' : False,
				'accesGranted' : accessGranted
		}
		return render_template('index.html', **templateData)

	@app.route('/menu')
	def menu():
		global usersLogged
		if request.remote_addr in usersLogged:
			resetTimeout(request.remote_addr)
			return render_template('menu.html')
		else:
			return redirect('/')

	@app.route('/temp/<opcion>')
	def tempHum(opcion):
		global p
		global usersLogged
		if request.remote_addr in usersLogged:
			resetTimeout(request.remote_addr)
			p = proxy.PROXY()
			h = None
			t = None
			if opcion == 'th':
				(t, h) = p.leerTemHume()
			elif opcion =='t':
				t = p.leerTem()
			elif opcion =='h':
				h = p.leerHume()

			tableTemp = None
			tableHum = None

			if (t != None):
				tableTemp = barraTemp(t)
			if (h != None):
				tableHum = barraHum(h)
			

			templateData = {
				'temp' : t,
				'hum' : h,
				'tableTemp': tableTemp,
				'tableHum': tableHum
			}
			return render_template('temperatura.html', **templateData)
		else:
			return redirect('/')

	@app.route('/img/<opcion>')
	def raspImg(opcion):
		return send_file('templates/img/'+opcion, mimetype='img/png')

	@app.route('/menu/calefaccion')
	def calefaccion():
		global usersLogged
		if request.remote_addr in usersLogged:
			resetTimeout(request.remote_addr)
			return render_template('menuCalefaccion.html')
		else:
			return redirect('/')

	@app.route('/menu/calefaccion/on')
	def calefaccionOn():
		global usersLogged
		if request.remote_addr in usersLogged:
			resetTimeout(request.remote_addr)
			try:
				s = socket.socket()
				s.connect(('127.0.0.1', 65000))
				s.send(b'x00x01')
				s.close()
			except Exception as e:
				raise e
			return redirect("/menu/calefaccion", code=302)
		else:
			return redirect('/')
		
	@app.route('/menu/calefaccion/off')
	def calefaccionOff():
		global usersLogged
		if request.remote_addr in usersLogged:
			resetTimeout(request.remote_addr)
			try:
				s = socket.socket()
				s.connect(('127.0.0.1', 65000))
				s.send(b'x00x02')
				s.close()
			except Exception as e:
				raise e
			return redirect("/menu/calefaccion", code=302)
		else:
			return redirect('/')

	@app.route('/menu/calefaccion/valores', methods=['GET', 'POST'])
	def valores():
		global usersLogged
		if request.remote_addr in usersLogged:
			resetTimeout(request.remote_addr)
			fHandler = fileHandler.FILEHANDLER()
			minTemp = None
			maxTemp = None
			try:
				minTemp = fHandler.readParam('tempmin')
				maxTemp = fHandler.readParam('tempmax')
				hume = fHandler.readParam('hume')
				email = fHandler.readParam('email')
				emaillogin = fHandler.readParam('emaillogin')
				emailpasswd = fHandler.readParam('emailpasswd')
				telegramtoken = fHandler.readParam('telegramtoken')
				telegramidgrupo = fHandler.readParam('telegramidgrupo')
				twitterconsumerkey = fHandler.readParam('twitterconsumerkey')
				twitterconsumersecret = fHandler.readParam('twitterconsumersecret')
				twitteraccesstoken = fHandler.readParam('twitteraccesstoken')
				twitteraccesstokensecret = fHandler.readParam('twitteraccesstokensecret')
				intervalolectura = fHandler.readParam('intervalolectura')
				modo = fHandler.readParam('modo')
			except Exception as e:
				print('No se ha podido leer el fichero bien')
			if request.method == 'POST':
				minTemp = request.form.get('minTemp')
				if (minTemp is not ''):
					fHandler.writeParam('TempMin',minTemp)
				maxTemp = request.form.get('maxTemp')
				if (maxTemp is not ''):
					fHandler.writeParam('TempMax',maxTemp)
				hume = request.form.get('hume')
				if (hume is not ''):
					fHandler.writeParam('hume', hume)
				email = request.form.get('email')
				if (email is not ''):
					fHandler.writeParam('email', email)
				emaillogin = request.form.get('emaillogin')
				if (emaillogin is not ''):
					fHandler.writeParam('emaillogin', emaillogin)
				emailpasswd = request.form.get('emailpasswd')
				if (emailpasswd is not ''):
					fHandler.writeParam('emailpasswd', emailpasswd)
				telegramtoken = request.form.get('telegramtoken')
				if (telegramtoken is not ''):
					fHandler.writeParam('telegramtoken', telegramtoken)
				telegramidgrupo = request.form.get('telegramidgrupo')
				if (telegramidgrupo is not ''):
					fHandler.writeParam('telegramidgrupo', telegramidgrupo)
				twitterconsumerkey = request.form.get('twitterconsumerkey')
				if (twitterconsumerkey is not ''):
					fHandler.writeParam('twitterconsumerkey', twitterconsumerkey)
				twitterconsumersecret = request.form.get('twitterconsumersecret')
				if (twitterconsumersecret is not ''):
					fHandler.writeParam('twitterconsumersecret', twitterconsumersecret)
				twitteraccesstoken = request.form.get('twitteraccesstoken')
				if (twitteraccesstoken is not ''):
					fHandler.writeParam('twitteraccesstoken', twitteraccesstoken)
				twitteraccesstokensecret = request.form.get('twitteraccesstokensecret')
				if (twitteraccesstokensecret is not ''):
					fHandler.writeParam('twitteraccesstokensecret', twitteraccesstokensecret)
				intervalolectura = request.form.get('intervalolectura')
				if (intervalolectura is not ''):
					fHandler.writeParam('intervalolectura', intervalolectura)
				modo = request.form.get('modo')
				if (modo is not ''):
					fHandler.writeParam('modo', modo)
				#tell the robot to read again the params from file
				try:
					s = socket.socket()
					s.connect(('127.0.0.1', 65000))
					s.send(b'x00x03')
					s.close()
				except Exception as e:
					raise e
			#print('tempMax: '+ str(maxTemp))
			#print('tempMin: '+ str(minTemp))

			tempData = {
				'minTemp' : minTemp,
				'maxTemp' : maxTemp,
				'hume' : hume,
				'email': email,
				'emaillogin': emaillogin,
				'emailpasswd': emailpasswd,
				'telegramtoken': telegramtoken,
				'telegramidgrupo': telegramidgrupo,
				'twitterconsumerkey': twitterconsumerkey,
				'twitterconsumersecret': twitterconsumersecret,
				'twitteraccesstoken': twitteraccesstoken,
				'twitteraccesstokensecret': twitteraccesstokensecret,
				'intervalolectura': intervalolectura,
				'modo': modo
			}
			return render_template("cambioValores.html", **tempData)
		else:
			return redirect('/')

	@app.route('/menu/calefaccion/modoM')
	def calefaccionModoManual():
		global usersLogged
		if request.remote_addr in usersLogged:
			resetTimeout(request.remote_addr)
			try:
				fHandler = fileHandler.FILEHANDLER()
				fHandler.writeParam('Modo','manual')

				s = socket.socket()
				s.connect(('127.0.0.1', 65000))
				s.send(b'x00x03')
				s.close()
			except Exception as e:
				print(str(e))
			return redirect("/menu/calefaccion", code=302)
		else:
			return redirect('/')

	@app.route('/menu/calefaccion/modoA')
	def calefaccionModoAutomatico():
		global usersLogged
		if request.remote_addr in usersLogged:
			resetTimeout(request.remote_addr)
			try:
				fHandler = fileHandler.FILEHANDLER()
				fHandler.writeParam('Modo','automatico')
				
				s = socket.socket()
				s.connect(('127.0.0.1', 65000))
				s.send(b'x00x03')
				s.close()
			except Exception as e:
				print(str(e))
			return redirect("/menu/calefaccion", code=302)
		else:
			return redirect('/')

	#TEMP HUM STATISTICS
	@app.route('/menu/calefaccion/est')
	def estadisticas():
		global usersLogged
		if request.remote_addr in usersLogged:
			resetTimeout(request.remote_addr)
			
			fHandler = fileHandler.FILEHANDLER()
			numeroItemsPlot = int(fHandler.readParam('numberxaxis'))
			interval = float(fHandler.readParam('plotintervaltime'))

			dataHandler.readDataFile('lecturas.txt', interval)
			dataHandler.plotStatistics(numeroItemsPlot)

			return render_template("estadisticas.html")
		else:
			return redirect('/')

	def envioSocket(ip, puerto, datos):
		s = socket.socket()
		s.connect((ip, puerto))
		s.send(datos)
		s.close()

	@app.route('/menu/calefaccion/fin')
	def finPrograma():
		global usersLogged
		if request.remote_addr in usersLogged:
			resetTimeout(request.remote_addr)
			uH = userHandler.USERHANDLER()
			uH.logoutAllUsers()
			try:
				
				s = socket.socket()
				s.connect(('127.0.0.1', 65000))
				s.send(b'x00x05')
				s.close()
			except Exception as e:
				print(str(e))
			return redirect("/menu/calefaccion", code=302)
		else:
			return redirect('/')
	#LOG
	@app.route('/menu/calefaccion/log')
	def log():
		global usersLogged
		if request.remote_addr in usersLogged:
			resetTimeout(request.remote_addr)
			logger = '';
			with open('eventos.txt', 'r') as f:
				try:
					for line in f:
						logger = logger+line+"</br>"
				finally:
					f.close()

			return render_template("log.html", logger=logger)
		else:
			return redirect('/')

	#REGISTRO
	@app.route('/registro', methods = ['POST', 'GET'])
	def registro():
		global usersLogged
		accessGranted = False
		if request.remote_addr in usersLogged:
			accessGranted = True
		else:
			if request.method == 'POST':
				user = request.form.get('user')
				passwd = request.form.get('passwd')
				description = request.form.get('description')
				try:
					uH = userHandler.USERHANDLER()
					accessGranted = uH.newUser(user, passwd, description, request.remote_addr)
					if accessGranted:
						fH = fileHandler.FILEHANDLER()
						timers[request.remote_addr] = threading.Timer(int(fH.readParam('usertimeout')), logoutUser, [request.remote_addr])
						timers[request.remote_addr].start()
						usersLogged[request.remote_addr] = user
						return redirect('/')
				except Exception as e:
					print(str(e))
				finally:
					uH.close()
			print(str(usersLogged))
		return render_template("register.html", accessGranted=accessGranted)

	@app.route('/menu/menuNFC', methods = ['POST', 'GET'])
	def menunfc():
		global usersLogged
		if request.remote_addr in usersLogged:
			resetTimeout(request.remote_addr)
			return render_template('menuNFC.html')
		else:
			return redirect('/')



	@app.route('/menu/menuNFC/writetag', methods = ['POST', 'GET'])
	def writeTag():
		global usersLogged
		global killTagThread
		global tagThread
		if request.remote_addr in usersLogged:
			resetTimeout(request.remote_addr)
			tag = usersLogged[request.remote_addr]
			print('Escribir etiqueta para el usuario: '+str(tag))
			killTagThread = threading.Event()
			tagThread = threading.Thread(target=writeTagThread, args=(killTagThread,))
			return render_template('tag.html', tag=tag)
		else:
			return redirect('/')

	#Asociar smartphone
	@app.route('/menu/menuNFC/asociarSmartphone', methods = ['POST', 'GET'])
	def asociarSmartphone():
		global usersLogged
		global uid
		uid = None
		Read.changeEnableRegister(False)
		accessGranted = False
		mensaje = None
		if request.remote_addr in usersLogged:
			resetTimeout(request.remote_addr)
			if request.method == 'POST':
				uid = request.form.get('uid')
				description = request.form.get('descripcion')
				hostname = request.form.get('hostname')
				authSmart = request.form.get('master')
				print(str(usersLogged[request.remote_addr])+' '+str(uid)+' '+str(hostname)+' '+str(description)+' '+str(authSmart))
				try:
					uH = userHandler.USERHANDLER()
					added = uH.addSmartphone(uid, description, hostname, authSmart)
					if(added == False):
						uH.updateSmartphone(uid, description, hostname, authSmart)
					mensaje,related = uH.relateSmartphone(usersLogged[request.remote_addr], uid)
				except Exception as e:
					print(str(e))
				finally:
					uH.close()
		else:
			return redirect('/')
			print(str(usersLogged))
		return render_template("asociarSmartphone.html", mensaje=mensaje)

		# CAMARA
	@app.route('/menu/video')
	def video():
	    return render_template('video.html')

	def gen(camera):
	    while True:
	        frame = camera.get_frame()
	        yield (b'--frame\r\n'
	               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

	@app.route('/video_feed')
	def video_feed():
		return Response(gen(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')

	    #END CAMARA
	#END OF ROUTES

	#REAL-TIME READING
	@socketio.on('desconectar')
	def handlerCloseing(arg):
		disconnect()

	@socketio.on('lectura')
	def handleReader(lectura):
		global p
		global usersLogged
		if request.remote_addr in usersLogged:
			h = None
			t = None
			tableTemp = None
			tableHum = None
			if lectura == '/temp/th':
				(t, h) = p.leerTemHume()
			elif lectura =='/temp/t':
				t = p.leerTem()
			elif lectura =='/temp/h':
				h = p.leerHume()
			"""Creacion de barras""" 
			if (t != None):
				tableTemp = barraTemp(t)
			if (h != None):
				tableHum = barraHum(h)

			templateData = {
				'temp' : t,
				'hum' : h,
				'tableTemp': tableTemp,
				'tableHum': tableHum
			}

			#Espera para leer cada 1 segundo
			time.sleep(0.5)
			socketio.emit('lect', templateData)
		else:
			return redirect('/')

	@socketio.on('requestUIDtoServer')
	def envioNFCSmartphone(lectura):
		global uid
		global currentSmartphoneSocketio
		currentSmartphoneSocketio = request.sid
		templateData = {}
		if(uid != None):
			print('UID listo para enviar'+uid)
			auxuid = uid
			uid = None
			try:
				templateData = { 'uid' : auxuid }
				time.sleep(0.5)
				
			except Exception as e:
				print('error de emit al html')
				print(str(e))
		socketio.emit('recibirUID', templateData)


	@socketio.on('requestTagtoServer')
	def enviotag(taghtml):
		global currentTagSocketio
		global tag
		global tagEscrita
		global tagThread
		tag = taghtml
		print('ServerWeb tag a escribir: '+str(tag))
		if(not tagThread.isAlive()):
			tagThread.start()
		currentTagSocketio = request.sid
		templateData = {}
		Read.changeStopped(True)
		try:
			templateData = { 'tag' : tag }
			if(tagEscrita == True):
				templateData = { 'tag' : tag, 'tagEscrita' : True }
				print('ServerWeb: tag escrita con exito: '+str(tag))	
				killTagThread.set()
				tagThread.join()
				Read.changeStopped(False)
		except Exception as e:
			print('error de emit al html')
			print(str(e))
		time.sleep(0.5)
		socketio.emit('recibirTag', templateData)

	@socketio.on('disconnect')
	def disconnection():
		global currentTagSocketio
		global currentSmartphoneSocketio
		global killTagThread
		global tagEscrita
		global tagThread
		print('******DESCONEXION******* de:'+str(request.sid))
		if(currentSmartphoneSocketio == request.sid):
			print("*_*_*_*cierre socket de smartphone asociacion")
			Read.changeEnableRegister(True)
		elif(currentTagSocketio == request.sid):
			print("*_*_*_*cierre socket de tag")
			tagEscrita = False
	#END REAL-TIME READING

	