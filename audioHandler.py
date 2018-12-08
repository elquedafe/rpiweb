import subprocess
from gtts import gTTS
from tempfile import NamedTemporaryFile
import datetime

def audio(msg):
	tts = gTTS(text=str(msg), lang='es')
	play(tts)
 
def playRob():
	path = "audio/rob.mp3"
	return_code = subprocess.call(["mpg123", path])

def playCommandFail():
	path = "audio/failCommand.mp3"
	return_code = subprocess.call(["mpg123", path])

def playTurnOnCalefaccion():
	path = "audio/turnOnCalefaccion.mp3"
	return_code = subprocess.call(["mpg123", path])

def playGoodMorning():
	path = "audio/goodMorning.mp3"
	return_code = subprocess.call(["mpg123", path])

def playTemperature(temp):
	tts = gTTS(text='La temperatura actual es '+str(temp)+' grados', lang='es')
	play(tts)

def thanks():
	tts = gTTS(text='De nada, guapo', lang='es')
	play(tts)

def playHumidity(hum):
	tts = gTTS(text='La humedad es del '+str(hum)+' porciento', lang='es')
	play(tts)

def today():
	tts = gTTS(text='Hoy es '+str(datetime.datetime.now().strftime("%d/%m/%Y")), lang='es')
	play(tts)

def time():
	tts = gTTS(text='Son las '+str(datetime.datetime.now().strftime("%X")), lang='es')
	play(tts)

def play(tts):
	f = NamedTemporaryFile()
	tts.save(f.name)
	return_code = subprocess.call(["mpg123", str(f.name)])
	f.close()
