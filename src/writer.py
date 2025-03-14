from nfc import NFC
import time
from random import randint
from ubinascii import hexlify, b2a_base64

SDA      = 5
SCK      = 18
MOSI     = 23
MISO     = 19
BAUDRATE = 100000

DEFAULT_BLOCK = 8

nfc = NFC(SDA, SCK, MOSI, MISO, BAUDRATE);

while True:
    try:
        print("Esperando tag NFC...")
        
        if nfc.is_card_present():
            print("Tag NFC detectada!")
            
            status, tag_type, uid, data = nfc.read_block(DEFAULT_BLOCK)
            
            if status == nfc.OK:
                print("Tipo de Tag: 0x%02x" % tag_type)
                print("UID: 0x%02x%02x%02x%02x" % (uid[0], uid[1], uid[2], uid[3]))
                print(f"ID: {b2a_base64(hexlify(bytearray(data))).decode()}")
            
            option = input("Você deseja gerar um novo ID e escrevê-lo no bloco 8? (S|N): ")
            
            if option == "S" or option == "s":
                print("Escrevendo dados...")
                
                data = []
                
                for i in range(16):
                    data.append(randint(0, 255))
                
                status, tag_type, uid = nfc.write_block(DEFAULT_BLOCK, data)
                
                if status == nfc.OK:
                    print("Dados escritos com sucesso!")
                    
                else:
                    print("ERRO: Não foi possível escrever os dados.")
                    
            elif option == "N" or option == "n":
                print("Ok. Continuando leitura...")
                
        time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nSaindo...")
        break