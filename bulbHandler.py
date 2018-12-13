from gpiozero import LED
import time

led = LED(21)
led.on()

def blink(seconds):
	global led
	led.off()
	time.sleep(seconds)
	led.on()
	time.sleep(seconds)
