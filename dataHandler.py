import sys
import time
import configparser
import proxy
from apliConsola import am2320
import datetime
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def obtenerDatos():
	temps=[]
	hums=[]
	dates=[]
	with open('lecturas.txt', 'r') as f:
		try:
			for line in f:
				words = line.split('\t')
				dates.append(words[0])
				temps.append(words[1])
				hums.append(words[2])
		finally:
			f.close()
	return dates, temps, hums	

#automata que lee el fichero de texto para obtener datos y agrupar
def agruparMinutos(temps, hums, dates):
	tempAux = []
	dateAux = []
	humAux = []
	tempAgrupada = []
	datesAgrupada = []
	humAgrupada = []
	temperatura = None
	humedad = None
	tempAuxi = 0.0
	humeAuxi = 0
	date = None
	primero = True
	
	for i in range(0, len(temps)):
		if primero==True:
			tempAux.append(temps[i])
			dateAux.append(dates[i])
			humAux.append(hums[i])
			print('PRIMERO:')
			print(tempAux)
			primero=False
		else:
			#Si es de la misma hora que la entrada anterior
			feAct = datetime.strptime(dates[i],'%Y-%m-%d %H:%M:%S.%f')
			feAnt = datetime.strptime(dates[i-1],'%Y-%m-%d %H:%M:%S.%f')

			#print(str(feAct.year)+'-'+str(feAct.month)+'-'+str(feAct.day)+' '+str(feAct.hour)+':'+str(feAct.minute))
			#print(str(feAnt.year)+'-'+str(feAnt.month)+'-'+str(feAnt.day)+' '+str(feAnt.hour)+':'+str(feAnt.minute))
			if ( (feAct.year==feAnt.year) and  (feAct.month==feAnt.month) and (feAct.day==feAnt.day) and (feAct.hour==feAnt.hour) ):
				#Si minuto entre 0 y 15
				if ( ((feAnt.minute>=0) and (feAnt.minute<15)) and (feAct.minute>=15) ):
					print(str(feAct.year)+'-'+str(feAct.month)+'-'+str(feAct.day)+' '+str(feAct.hour)+':'+str(feAct.minute)+'-->'+str(feAnt.year)+'-'+str(feAnt.month)+'-'+str(feAnt.day)+' '+str(feAnt.hour)+':'+str(feAnt.minute))
					print(tempAux)
					
					tempAux, humAux, tempAgrupada, datesAgrupada, humAgrupada = agrupacionMinutos(tempAux, humAux, tempAgrupada, datesAgrupada, humAgrupada, i, dates)

					primero = True
					#primero de la iteracion
					tempAux.append(temps[i])
					dateAux.append(dates[i])
					humAux.append(hums[i])
					print(tempAux)

				#Si minuto entre 15 y 30
				elif ((feAnt.minute>=15) and (feAnt.minute<30) and (feAct.minute>=30) ):
					print(str(feAct.year)+'-'+str(feAct.month)+'-'+str(feAct.day)+' '+str(feAct.hour)+':'+str(feAct.minute)+'-->'+str(feAnt.year)+'-'+str(feAnt.month)+'-'+str(feAnt.day)+' '+str(feAnt.hour)+':'+str(feAnt.minute))
					print(tempAux)
					
					tempAux, humAux, tempAgrupada, datesAgrupada, humAgrupada = agrupacionMinutos(tempAux, humAux, tempAgrupada, datesAgrupada, humAgrupada, i, dates)

					primero = True
					#primero de la iteracion
					tempAux.append(temps[i])
					dateAux.append(dates[i])
					humAux.append(hums[i])
					print(tempAux)

					
				#Si minuto entre 30 y 45
				elif ((feAnt.minute>=30) and (feAnt.minute<45) and (feAct.minute>=45) ):
					print(str(feAct.year)+'-'+str(feAct.month)+'-'+str(feAct.day)+' '+str(feAct.hour)+':'+str(feAct.minute)+'-->'+str(feAnt.year)+'-'+str(feAnt.month)+'-'+str(feAnt.day)+' '+str(feAnt.hour)+':'+str(feAnt.minute))
					print(tempAux)
					
					tempAux, humAux, tempAgrupada, datesAgrupada, humAgrupada = agrupacionMinutos(tempAux, humAux, tempAgrupada, datesAgrupada, humAgrupada, i, dates)

					primero = True
					#primero de la iteracion
					tempAux.append(temps[i])
					dateAux.append(dates[i])
					humAux.append(hums[i])
					print(tempAux)
					
				#Si minuto entre 45 y 60
				elif ((feAnt.minute>=45) and (feAnt.minute<60) and ((feAct.minute>=0) and ((feAct.minute<45)))):
					print(str(feAct.year)+'-'+str(feAct.month)+'-'+str(feAct.day)+' '+str(feAct.hour)+':'+str(feAct.minute)+'-->'+str(feAnt.year)+'-'+str(feAnt.month)+'-'+str(feAnt.day)+' '+str(feAnt.hour)+':'+str(feAnt.minute))
					print(tempAux)
					
					tempAux, humAux, tempAgrupada, datesAgrupada, humAgrupada = agrupacionMinutos(tempAux, humAux, tempAgrupada, datesAgrupada, humAgrupada, i, dates)

					primero = True
					#primero de la iteracion
					tempAux.append(temps[i])
					dateAux.append(dates[i])
					humAux.append(hums[i])
					print(tempAux)

				else:
					tempAux.append(temps[i])
					dateAux.append(dates[i])
					humAux.append(hums[i])
					print('ELSE elsif:')
					print(tempAux)



			else:
				tempAux.append(temps[i])
				dateAux.append(dates[i])
				humAux.append(hums[i])
				print('ELSE RAIZ:')
				print(tempAux)

	return tempAgrupada, humAgrupada, datesAgrupada

def agruparHoras(tempAux, humAux, tempAgrupada, datesAgrupada, humAgrupada):
	tempAuxi = 0.0
	humAuxi = 0

	for t in tempAux:

		tempAuxi += float(t)
		#print(str(tempAuxi))
	for h in humAux:
		h = h.replace('\n', '')
		humAuxi += int(h)

	temperatura = float(tempAuxi)/len(tempAux)
	humedad = int(humAuxi)/len(humAux)
	fecha = datetime.strptime(dates[i-1],'%Y-%m-%d %H:%M:%S.%f')
	date = str(fecha.year)+'-'+str(fecha.month)+'-'+str(fecha.day)+' '+str(fecha.hour)+':00'
	
	tempAgrupada.append(temperatura)
	datesAgrupada.append(date)
	humAgrupada.append(humedad)

	tempAux = []
	dateAux = []

	return tempAux, humAux, tempAgrupada, datesAgrupada, humAgrupada

#agrupa cada 15 minutos
def agrupacionMinutos(tempAux, humAux, tempAgrupada, datesAgrupada, humAgrupada, i, dates):
	tempAuxi = 0.0
	humAuxi = 0.0
	for t in tempAux:
		tempAuxi += float(t)
		#print(str(tempAuxi))
	for h in humAux:
		humAuxi += float(h)
	temperatura = float(tempAuxi)/len(tempAux)
	humedad = float(humAuxi)/len(humAux)

	fecha = datetime.strptime(dates[i-1],'%Y-%m-%d %H:%M:%S.%f')
	date = str(fecha.year)+'-'+str(fecha.month)+'-'+str(fecha.day)+' '+str(fecha.hour)+':'+str(fecha.minute)
	
	print('fecha guardada')
	print(date)

	tempAgrupada.append(temperatura)
	datesAgrupada.append(date)
	humAgrupada.append(humedad)

	tempAux = []
	dateAux = []

	return tempAux, humAux, tempAgrupada, datesAgrupada, humAgrupada

def stats(temp, time, hum, numeroItemsPlot):
	x = []
	
	for i in range(0, len(time)):
		x.append(i)
	
	#plot temp
	plt.ylim([-40, 80])
	plt.plot(x[-numeroItemsPlot:], temp[-numeroItemsPlot:])
	plt.gcf().autofmt_xdate()
	plt.xticks(x[-numeroItemsPlot:], time[-numeroItemsPlot:])
	#plt.show()
	plt.savefig('templates/img/temperatura.png')
	#plot humedad
	plt.ylim([0, 100])
	plt.plot(x[-numeroItemsPlot:], hum[-numeroItemsPlot:])
	plt.gcf().autofmt_xdate()
	plt.xticks(x[-numeroItemsPlot:], time[-numeroItemsPlot:])
	#plt.show()
	plt.savefig('templates/img/humedad.png')