import RPi.GPIO as GPIO
import time

# start GPS 

GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)


GPIO.output(25, GPIO.HIGH)  
time.sleep(1) 
GPIO.output(25, GPIO.LOW) 
time.sleep(2) 
GPIO.output(25, GPIO.HIGH) 


GPIO.cleanup()
