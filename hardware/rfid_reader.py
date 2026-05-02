import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import time


class RFIDReader:
    DEBOUNCE_TIME = 1.5

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.reader = MFRC522(spd=1000000)  # 1 MHz, lebih stabil dari default 8 MHz

        self.last_uid = None
        self.last_read_time = 0
        self.card_present = False

    def read_uid(self):

        # --- Step 1: Request / deteksi kartu ---
        status, _ = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)

        if status != self.reader.MI_OK:
            # Tidak ada kartu terdeteksi, reset last_uid agar
            # kartu yang sama bisa dibaca lagi setelah diangkat
            self.card_present = False
            self.last_uid = None
            return None
        
        if self.card_present:
            return None

        # --- Step 2: Anti-collision (ambil UID) ---
        status, uid_bytes = self.reader.MFRC522_Anticoll()

        if status != self.reader.MI_OK:
            # Gagal baca UID (bisa karena 2 kartu sekaligus / noise)
            return None

        # --- Step 3: Konversi bytes UID ke string HEX kapital ---
        # uid_bytes adalah list [b1, b2, b3, b4, checksum]
        # Ambil 4 byte pertama saja (checksum tidak termasuk UID)
        uid_hex = ''.join(format(b, '02X') for b in uid_bytes)

        # --- Step 4: Debounce ---
        # Cegah UID yang sama terkirim berulang kali selama kartu
        # masih ditempel di reader
        current_time = time.time()
        if (uid_hex == self.last_uid and
                (current_time - self.last_read_time) < self.DEBOUNCE_TIME):
            # Kartu sama, belum melewati debounce time → abaikan
            self.reader.MFRC522_StopCrypto1()
            return None

        # --- Step 5: UID valid dan lolos debounce ---
        self.last_uid = uid_hex
        self.last_read_time = current_time
        self.card_present = True

        # Selalu stop crypto setelah selesai baca
        self.reader.MFRC522_StopCrypto1()

        return uid_hex

    def cleanup(self):
        GPIO.cleanup()