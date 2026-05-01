#import RPi.GPIO as GPIO
#from mfrc522 import MFRC522
import time


class RFIDReader:
    def __init__(self):
        self.reader = MFRC522()
        self.last_uid = None

    def read_uid(self):

        (status, TagType) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)

        if status == self.reader.MI_OK:
            (status, uid) = self.reader.MFRC522_Anticoll()

            if status == self.reader.MI_OK:
                uid_hex = ''.join([format(x, '02X') for x in uid])

                # Hindari terbaca berulang
                if uid_hex != self.last_uid:
                    self.last_uid = uid_hex

                    self.reader.MFRC522_StopCrypto1()

                    return uid_hex

                self.reader.MFRC522_StopCrypto1()

        else:
            # reset kalau tidak ada kartu
            self.last_uid = None

        return None

    def cleanup(self):
        GPIO.cleanup()