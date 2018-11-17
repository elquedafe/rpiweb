from flask import Flask, render_template, send_file, redirect, request
import proxy
import socket
import dataHandler
import fileHandler

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/menu')
def menu():
	return render_template('menu.html')

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

@app.route('/temp/<opcion>')
def tempHum(opcion):
	p = proxy.PROXY()
	h = None
	t = None
	if opcion == 'th':
		(t, h) = p.leerTemHume()
	elif opcion =='t':
		t = p.leerTem()
	elif opcion =='h':
		h = p.leerHume()
	p.close()

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

@app.route('/img/<opcion>')
def raspImg(opcion):
	return send_file('templates/img/'+opcion, mimetype='img/png')

@app.route('/menu/calefaccion')
def calefaccion():
	return render_template('menuCalefaccion.html')

@app.route('/menu/calefaccion/on')
def calefaccionOn():
	try:
		s = socket.socket()
		s.connect(('127.0.0.1', 65000))
		s.send(b'x00x01')
		s.close()
	except Exception as e:
		raise e
	return redirect("/menu/calefaccion", code=302)
	
@app.route('/menu/calefaccion/off')
def calefaccionOff():
	try:
		s = socket.socket()
		s.connect(('127.0.0.1', 65000))
		s.send(b'x00x02')
		s.close()
	except Exception as e:
		raise e
	return redirect("/menu/calefaccion", code=302)

@app.route('/menu/calefaccion/valores', methods=['GET', 'POST'])
def valores():
	fHandler = fileHandler.FILEHANDLER()
	minTemp = None
	maxTemp = None
	try:
		minTemp = fHandler.readParam('TempMin')
		maxTemp = fHandler.readParam('TempMax')
	except Exception as e:
		print('No se ha podido leer el fichero bien')
	if request.method == 'POST':
		minTemp = request.form.get('minTemp')
		fHandler.writeParam('TempMin',minTemp)
		maxTemp = request.form.get('maxTemp')
		fHandler.writeParam('TempMax',maxTemp)
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
		'maxTemp' : maxTemp
	}
	return render_template("cambioValores.html", **tempData)

@app.route('/menu/calefaccion/modoM')
def calefaccionModoManual():
	try:
		fHandler = fileHandler.FILEHANDLER()
		fHandler.writeParam('Modo','manual')

		s = socket.socket()
		s.connect(('127.0.0.1', 65000))
		s.send(b'x00x03')
		s.close()
	except Exception as e:
		print(e)
	return redirect("/menu/calefaccion", code=302)

@app.route('/menu/calefaccion/modoA')
def calefaccionModoAutomatico():
	try:
		fHandler = fileHandler.FILEHANDLER()
		fHandler.writeParam('Modo','automatico')
		
		s = socket.socket()
		s.connect(('127.0.0.1', 65000))
		s.send(b'x00x03')
		s.close()
	except Exception as e:
		print(e)
	return redirect("/menu/calefaccion", code=302)

@app.route('/menu/calefaccion/est')
def estadisticas():
	#modulo dataHandler.py
	numeroItemsPLot = 0

	dates,temps,hums = dataHandler.obtenerDatos()
	#print(temps)
	#print(dates)
	#print(hums)
	temps, hums, dates = dataHandler.agruparMinutos(temps, hums, dates)
	print(temps)
	
	#numero de valores en la grafica para que se vea adecuadamente
	if (len(temps) <= 12):
		numeroItemsPlot = len(temps)
	else:
		numeroItemsPlot = 12

	if(os.path.isfile('templates/img/temperatura.png')):
		print('elimnartemp')
		os.remove("templates/img/temperatura.png")
	if(os.path.isfile('templates/img/humedad.png')):
		print('elimnarhume')
		os.remove("templates/img/humedad.png")
	dataHandler.stats(temps, dates, hums, numeroItemsPlot)
	return render_template("estadisticas.html")

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)