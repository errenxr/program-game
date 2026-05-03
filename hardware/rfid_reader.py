import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

class RFIDReader:
    DEBOUNCE_TIME = 2.0         
    REINIT_INTERVAL = 500
    MAX_CONSECUTIVE_FAIL = 15

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.reader = None
        self.last_uid = None
        self.last_read_time = 0
        self.card_present = False

        self._iter_count = 0
        self._consecutive_fail = 0

        self._init_reader()

    def _init_reader(self):
        try:
            if self.reader is not None:
                try:
                    self.reader.MFRC522_StopCrypto1()
                except Exception:
                    pass

            self.reader = MFRC522(spd=1000000)
            self._iter_count = 0
            self._consecutive_fail = 0
            logging.info("MFRC522 berhasil (re)inisialisasi.")
        except Exception as e:
            logging.error(f"Gagal inisialisasi MFRC522: {e}")
            self.reader = None

    def _halt_card(self):
        try:
            self.reader.MFRC522_StopCrypto1()
            if hasattr(self.reader, 'MFRC522_Halt'):
                self.reader.MFRC522_Halt()
            else:
                self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
        except Exception as e:
            logging.warning(f"Gagal halt kartu: {e}")

    def read_uid(self):
        if self.reader is None:
            self._init_reader()
            return None

        self._iter_count += 1
        if self._iter_count >= self.REINIT_INTERVAL:
            logging.info("Reinisialisasi periodik MFRC522...")
            self._init_reader()
            return None

        if self._consecutive_fail >= self.MAX_CONSECUTIVE_FAIL:
            logging.warning(f"Gagal {self._consecutive_fail}x berturut. Reinisialisasi paksa...")
            self._init_reader()
            return None

        try:
            # STEP 1: Request
            status, _ = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)

            if status != self.reader.MI_OK:
                # Hanya reset card_present, JANGAN reset last_uid
                # last_uid tetap ada agar debounce waktu tetap aktif
                # meskipun kartu sempat "tidak terdeteksi" 1-2 cycle
                self.card_present = False
                self._consecutive_fail += 1
                return None

            self._consecutive_fail = 0

            # Kartu fisik masih menempel, skip tanpa perlu baca ulang
            if self.card_present:
                return None

            # STEP 2: Anti-collision
            status, uid_bytes = self.reader.MFRC522_Anticoll()
            if status != self.reader.MI_OK:
                logging.warning("Anticoll gagal.")
                self._halt_card()
                return None

            # STEP 3: SelectTag
            select_status = self.reader.MFRC522_SelectTag(uid_bytes)
            if select_status == 0:
                logging.warning("SelectTag gagal.")
                self._halt_card()
                return None

            # STEP 4: Konversi UID
            uid_hex = ''.join(format(b, '02X') for b in uid_bytes[:4])

            # ============================================================
            # STEP 5: Debounce berbasis WAKTU saja (kunci perbaikan)
            #
            # Logika:
            # - Jika UID sama DAN belum lewat DEBOUNCE_TIME → tolak
            # - Ini aktif bahkan saat kartu sempat diangkat lalu ditap lagi
            #   karena last_uid TIDAK direset saat kartu tidak terdeteksi
            # ============================================================
            current_time = time.time()
            time_since_last = current_time - self.last_read_time

            if uid_hex == self.last_uid and time_since_last < self.DEBOUNCE_TIME:
                logging.debug(
                    f"Debounce aktif untuk {uid_hex} "
                    f"({time_since_last:.2f}s < {self.DEBOUNCE_TIME}s)"
                )
                self._halt_card()
                self.card_present = True  # Tandai masih ada kartu
                return None

            # UID valid dan lolos debounce
            self.last_uid = uid_hex
            self.last_read_time = current_time
            self.card_present = True

            logging.info(f"UID diterima: {uid_hex} (jeda dari baca sebelumnya: {time_since_last:.2f}s)")

            self._halt_card()
            return uid_hex

        except Exception as e:
            logging.error(f"Exception saat baca RFID: {e}")
            self._consecutive_fail += 1
            try:
                self._halt_card()
            except Exception:
                pass
            return None

    def cleanup(self):
        try:
            self._halt_card()
        except Exception:
            pass
        GPIO.cleanup()
        logging.info("GPIO cleanup selesai.")