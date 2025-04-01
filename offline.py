from hx711 import HX711
from nfc import NFC
from servo import Servo
from buzzer import Buzzer, Note
from machine import Pin
from ubinascii import hexlify, b2a_base64
from time import sleep

"""SENSORES ======================================================================================================= """

# NFC
SDA      = 19
SCK      = 18
MOSI     = 26
MISO     = 25
BAUDRATE = 100000
DEFAULT_BLOCK = 8
nfc = NFC(SDA, SCK, MOSI, MISO, BAUDRATE);

# HX711
dt = Pin(22, Pin.OUT)
sck = Pin(23, Pin.OUT)
hx = HX711(dt, sck)
hx.tare(10)

# Servos
servo1 = Servo(21)
servo2 = Servo(5)
servo1.move(90)
servo2.move(0)

# Buzzer
buzzer = Buzzer(15)

megalovania = [
    Note(Buzzer.D4, Note.SIXTEENTH, Note.STACCATO),
    Note(Buzzer.D4, Note.SIXTEENTH, Note.STACCATO),
    Note(Buzzer.D5, Note.EIGHTH, Note.STACCATO),
    Note(Buzzer.A4, Note.EIGHTH),
    Note(0, Note.SIXTEENTH),
    Note(Buzzer.G4s, Note.EIGHTH, Note.STACCATO),
    Note(Buzzer.G4, Note.EIGHTH, Note.STACCATO),
    Note(Buzzer.F4, Note.EIGHTH),
    Note(Buzzer.D4, Note.SIXTEENTH, Note.STACCATO),
    Note(Buzzer.F4, Note.SIXTEENTH, Note.STACCATO),
    Note(Buzzer.G4, Note.SIXTEENTH, Note.STACCATO),
]
buzzer.set_tune(megalovania)
buzzer.set_tempo(130)

WAIT = 5

while True:
    sleep(1)
    servo1.move(90)
    servo2.move(0)
    
    print("Esperando por tag NFC...")
    
    if (nfc.is_card_present()):
        print("Tag nfc detectada!")
        
        status, tag_type, uid, data = nfc.read_block(DEFAULT_BLOCK)
            
        if status == nfc.OK:
            cow_id = b2a_base64(hexlify(bytearray(data))).decode().rstrip("\n")
            cow_weight = round(hx.weight(10))
            
            print("Tipo de Tag: 0x%02x" % tag_type)
            print("UID: 0x%02x%02x%02x%02x" % (uid[0], uid[1], uid[2], uid[3]))
            print(f"ID: {cow_id}")
            print(f"Peso medido na balanca: {cow_weight}")
            
            # Abre porteiras
            servo1.move(0)
            servo2.move(90)
            
            buzzer.play_tune()

            sleep(WAIT)

buzzer.deinit()

