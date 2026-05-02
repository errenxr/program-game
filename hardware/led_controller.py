import RPi.GPIO as GPIO

GREEN_PIN = 5
RED_PIN = 6

class LEDController:
    def __init__(self):
        GPIO.setwarnings(False)
        
        if GPIO.getmode() is None:
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(GREEN_PIN, GPIO.OUT)
        GPIO.setup(RED_PIN, GPIO.OUT)

        # pastikan mati di awal
        GPIO.output(GREEN_PIN, GPIO.LOW)
        GPIO.output(RED_PIN, GPIO.LOW)

    def green_on(self):
        GPIO.output(GREEN_PIN, GPIO.HIGH)
        GPIO.output(RED_PIN, GPIO.LOW)

    def red_on(self):
        GPIO.output(GREEN_PIN, GPIO.LOW)
        GPIO.output(RED_PIN, GPIO.HIGH)

    def off(self):
        GPIO.output(GREEN_PIN, GPIO.LOW)
        GPIO.output(RED_PIN, GPIO.LOW)

    def cleanup(self):
        GPIO.cleanup()