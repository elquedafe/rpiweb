from gpiozero import LED
import time

led = LED(21)

def blink(seconds):
	global led
	led.on()
	time.sleep(seconds)
	led.off()
	time.sleep(seconds)
