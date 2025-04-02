from hx711 import HX711
from nfc import NFC
from servo import Servo
from buzzer import Buzzer, Note
from machine import Pin
from ubinascii import hexlify, b2a_base64
from time import sleep
import ujson
import network
from umqtt.simple import MQTTClient

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

WIFI_SSID = "Visitantes"
WIFI_PASSWORD = ""

# Dados para conexão ao broker
MQTT_CLIENT_ID = "bolsonaro81j2bdiausdo"
MQTT_BROKER    = "broker.emqx.io"
MQTT_PORT      = 1883
MQTT_USER      = ""
MQTT_PASSWORD  = ""

# Tópicos para envio e recebimento de dados
MQTT_TOPIC = "dadoscow8ai/"

# Estação/cliente para rede
sta_if = network.WLAN(network.STA_IF)

# Cliente MQTT com configurações de conexão
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT)

# Callback (função que é chamada quando o cliente recebe uma mensagem de um tópico em que está subscrito)
def callback(topic, msg):
    print(f"{topic.decode()}: {msg.decode()}")
    

# Função que realiza a tentativa de conexão com uma rede wifi.
def do_connect_wifi():
    print("Conectando ao Wi-Fi", end="")
    try:
        sta_if.active(True)
        sta_if.connect(WIFI_SSID, WIFI_PASSWORD)

        while not sta_if.isconnected():
            print(".", end="")
            sleep(1)

        print("\nConectado à internet!")
    except OSError as error:
        print(error)


# Função que realiza a conexão com o broker MQTT
def do_connect_mqtt():    
    print("Conectando ao servidor MQTT...")

    # Configura callback
    client.set_callback(callback)

    # Faz a conexão
    client.connect()

    # Subscreve nos tópicos de comandos e configurações
    client.subscribe(MQTT_TOPIC) 

    print("Conectado!")


do_connect_wifi()
do_connect_mqtt()

while True:
    sleep(1)
    client.check_msg()
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
            
            data = {
                "id": cow_id,
                "weight": cow_weight
            }
            
            json = ujson.dumps(data)
            client.publish(MQTT_TOPIC, json)
            
            # Abre porteiras
            servo1.move(0)
            servo2.move(90)
            
            buzzer.play_tune()

            sleep(WAIT)

buzzer.deinit()
