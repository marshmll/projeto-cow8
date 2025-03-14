from nfc import NFC
import time
from ubinascii import hexlify, b2a_base64

SDA      = 5
SCK      = 18
MOSI     = 23
MISO     = 19
BAUDRATE = 100000

nfc = NFC(SDA, SCK, MOSI, MISO, BAUDRATE);

while True:
    try:     
        (stat, tag_type, uid, data) = nfc.read_block(8)
        
        if stat == nfc.OK:
            print("Tipo de Tag: 0x%02x" % tag_type)
            print("UID: 0x%02x%02x%02x%02x" % (uid[0], uid[1], uid[2], uid[3]))
            print(f"ID: {b2a_base64(hexlify(bytearray(data))).decode()}")

        time.sleep(1)
        
    except KeyboardInterrupt:
        break
