import speech_recognition as sr
import audioHandler
# Record Audio
r = sr.Recognizer()
#r.energy_threshold = 500
#r.dynamic_energy_threshold = False
r.pause_threshold = 0.6
assitantName = 'asistente'
def recognizer(sensor):
	while True:
		with sr.Microphone() as source:
			#print("Ajustando ruido")
			#r.adjust_for_ambient_noise(source, 0.6)
			print("Hable:")
			audio = r.listen(source, None, 2.0)
		transcripton = ''
		# Speech recognition using Google Speech Recognition
		try:
		    # for testing purposes, we're just using the default API key
		    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
		    # instead of `r.recognize_google(audio)`
		    transcripton = r.recognize_google(audio, language="es-ES")
		    print("You said: " + transcripton)
		    if(assitantName in transcripton):
			    if ((any(word in transcripton for word in ['pon', 'enciende'])) and (any(word in transcripton for word in ['calefacción', 'aire']))):
			    	audioHandler.playTurnOnCalefaccion()
			    if ((any(word in transcripton for word in ['quita', 'apaga'])) and (any(word in transcripton for word in ['calefacción', 'aire']))):
			    	audioHandler.playTurnOffCalefaccion()
			    elif(any(word in transcripton for word in ['buenos días', 'hola', 'qué tal'])):
			    	audioHandler.playGoodMorning()
			    elif(any(word in transcripton for word in ['temperatura', 'grados'])):
			    	
			    	audioHandler.playTemperature(sensor.leerTem())
			    elif('humedad' in transcripton):
			    	audioHandler.playHumidity(sensor.leerHume())
			    elif('gracias' in transcripton):
			    	audioHandler.thanks()
			    elif(all(map(lambda w: w in transcripton, ('día', 'hoy'))) or all(map(lambda w: w in transcripton, ('día', 'es')))):
			    	audioHandler.today()
			    elif('hora' in transcripton):
			    	audioHandler.time()
			    else:
			    	audioHandler.playCommandFail()

		except sr.UnknownValueError:
		    print("Google Speech Recognition could not understand audio")
		    if(assitantName in transcripton):
		    	audioHandler.playCommandFail()

		except sr.RequestError as e:
		    print("Could not request results from Google Speech Recognition service; {0}".format(e))
		except Exception as e:
			print(str(e))