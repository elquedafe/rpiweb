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
import os
import pandas as pd

def printDataFrame(dataFrame):
	with pd.option_context('display.max_rows', None, 'display.max_columns', None):
		print(dataFrame)

def addToArrays(date, temp, hum):
	global dates
	global temps
	global hums
	dates.append(date)
	temps.append(temp)
	hums.append(hum)

def emptyArrays():
	global dates
	global temps
	global hums
	dates = []
	temps = []
	hums = []

def computeAvg():
	global dates
	global temps
	global hums
	global outDates
	global outTemps
	global outHums
	tempAuxi = 0.0
	humAuxi = 0.0

	for t in temps:
		tempAuxi += float(t)
	for h in hums:
		humAuxi += float(h)
	temperature = float(tempAuxi)/len(temps)
	humidity = float(humAuxi)/len(hums)
	date = str(dates[-1].year)+'-'+str(dates[-1].month)+'-'+str(dates[-1].day)+' '+str(dates[-1].hour)+':'
	if( (dates[-1].minute >= 0) and (dates[-1].minute < 10) ):
		date = date+'0'+str(dates[-1].minute)
	else:
		date = date+str(dates[-1].minute)

	outDates.append(date)
	outTemps.append(temperature)
	outHums.append(humidity)

def processRows(row):
	global dates
	global temps
	global hums
	global firstRowDate
	global firstRead
	global interval
	minutes = 15
	seconds = minutes*60

	#Lectura del dataframe
	currentRowDate = row['date']
	currentRowDate = datetime.strptime(currentRowDate,'%Y-%m-%d %H:%M:%S.%f') # New format: 2018-11-01 hh:mm:ss:ms
	currentRowTemp = row['temperature']
	currentRowHum = row['humidity']
	if(firstRead == False):
		#Si se diferencia en menos de x segundos de la primera lectura
		if( (currentRowDate-firstRowDate).total_seconds() < interval):
			addToArrays(currentRowDate, currentRowTemp, currentRowHum)
		else:
			computeAvg()
			emptyArrays()
			addToArrays(currentRowDate, currentRowTemp, currentRowHum)
			firstRowDate = currentRowDate
	else:
		firstRead = False
		firstRowDate = currentRowDate
		addToArrays(currentRowDate, currentRowTemp, currentRowHum)
	#print(dates)

def computeLast():
	global dates
	global temps
	global hums
	global firstRowDate
	global firstRead
	minutes = 15
	seconds = minutes*60

	currentRowDate = dates[-1]
	currentRowTemp = temps[-1]
	currentRowHum = hums[-1]

	computeAvg()
	emptyArrays()




def readDataFile(file, intervaltime):
	global interval
	interval = intervaltime
	df = pd.read_csv(file, sep="\t", header=None, names = ['date','temperature','humidity'])
	df.apply(processRows, axis=1)
	computeLast()

def plotStatistics(numeroItemsPlot):
	global outDates
	global outTemps
	global outHums
	x = []
	
	for i in range(0, len(outDates)):
		x.append(i)
	#plot temp
	print(outTemps)
	print(outDates)
	print(outHums)
	plt.ylim([-40, 80])
	plt.grid(True)
	plt.title('House Temperature')
	plt.xlabel('Time')
	plt.ylabel('Temperature (ºC)')
	plt.plot(x[-numeroItemsPlot:], outTemps[-numeroItemsPlot:], '-or')
	plt.gcf().autofmt_xdate()
	plt.xticks(x[-numeroItemsPlot:], outDates[-numeroItemsPlot:])
	plt.tight_layout()
	#plt.show()
	plt.savefig('templates/img/temperatura.png')
	plt.close()
	
	#plot humedad
	plt.ylim([0, 100])
	plt.grid(True)
	plt.title('House Humidity')
	plt.xlabel('Time')
	plt.ylabel('RH (%)')
	plt.plot(x[-numeroItemsPlot:], outHums[-numeroItemsPlot:], '-ob')
	plt.gcf().autofmt_xdate()
	plt.xticks(x[-numeroItemsPlot:], outDates[-numeroItemsPlot:])
	plt.tight_layout()
	#plt.show()
	plt.savefig('templates/img/humedad.png')
	plt.close()

# Variables globales
dates = []
temps = []
hums = []
outDates = []
outTemps = []
outHums = []
firstRowDate = 0
firstRead = True
interval = 0
userslogged = {}