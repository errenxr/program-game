import RPi.GPIO as GPIO
import threading

GREEN_PIN = 17
RED_PIN = 27

class LEDController:
    def __init__(self):
        GPIO.setwarnings(False)

        if GPIO.getmode() is None:
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(GREEN_PIN, GPIO.OUT)
        GPIO.setup(RED_PIN, GPIO.OUT)

        self.off()  # pastikan mati di awal

    def _auto_off(self, delay):
        """Matikan LED setelah delay detik (di thread terpisah)"""
        def turn_off():
            GPIO.output(GREEN_PIN, GPIO.LOW)
            GPIO.output(RED_PIN, GPIO.LOW)

        timer = threading.Timer(delay, turn_off)
        timer.start()

    def green_on(self, duration=2):
        GPIO.output(GREEN_PIN, GPIO.HIGH)
        GPIO.output(RED_PIN, GPIO.LOW)
        self._auto_off(duration)

    def red_on(self, duration=2):
        GPIO.output(GREEN_PIN, GPIO.LOW)
        GPIO.output(RED_PIN, GPIO.HIGH)
        self._auto_off(duration)

    def off(self):
        GPIO.output(GREEN_PIN, GPIO.LOW)
        GPIO.output(RED_PIN, GPIO.LOW)

    def cleanup(self):
        GPIO.cleanup()