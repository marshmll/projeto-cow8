from hx711 import HX711
from nfc import NFC
from servo import Servo
from buzzer import Buzzer, Note
from machine import Pin
from ubinascii import hexlify, b2a_base64
from time import sleep
import ujson
import network
import sys
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

# Flag de desabilitação
disable = False

# Servos
servo1 = Servo(21)
servo2 = Servo(5)
servo1.move(90)
servo2.move(0)

# Buzzer
buzzer = Buzzer(15)

startup = [
    Note(Buzzer.E4, Note.EIGHTH),
    Note(Buzzer.B4, Note.EIGHTH),
    Note(Buzzer.E5, Note.EIGHTH),
]
info = [
    Note(Buzzer.B4, Note.EIGHTH),
]
warning = [
    Note(Buzzer.D5s, Note.SIXTEENTH, Note.STACCATO),
    Note(Buzzer.D5, Note.SIXTEENTH, Note.STACCATO),
    Note(Buzzer.C5s, Note.SIXTEENTH, Note.STACCATO),
    Note(Buzzer.C5, Note.SIXTEENTH, Note.STACCATO),
]
error = [
    Note(Buzzer.D5, Note.SIXTEENTH),
    Note(Buzzer.A4, Note.SIXTEENTH),
    Note(Buzzer.D5, Note.SIXTEENTH),
    Note(Buzzer.A4, Note.SIXTEENTH),
    Note(Buzzer.D5, Note.SIXTEENTH),
    Note(Buzzer.A4, Note.SIXTEENTH),
    Note(Buzzer.D5, Note.SIXTEENTH),
    Note(Buzzer.A4, Note.SIXTEENTH),
]

def startup_sound():
    buzzer.set_tune(startup)
    buzzer.set_tempo(110)
    buzzer.play_tune()
    
def info_sound():
    buzzer.set_tune(info)
    buzzer.set_tempo(80)
    buzzer.play_tune()    

def warning_sound():
    buzzer.set_tune(warning)
    buzzer.set_tempo(180)
    buzzer.play_tune()
    
def error_sound():
    buzzer.set_tune(error)
    buzzer.set_tempo(100)
    buzzer.play_tune()

WAIT = 5

WIFI_SSID = "LondrinenseLogistica"
WIFI_PASSWORD = "131003240706"

# Dados para conexão ao broker
MQTT_CLIENT_ID = "f654"
MQTT_BROKER    = "broker.emqx.io"
MQTT_PORT      = 1883
MQTT_USER      = ""
MQTT_PASSWORD  = ""

# Tópicos para envio e recebimento de dados
MQTT_MEASUREMENTS = "cow8/measurement"
MQTT_STATUS = "cow8/status"
MQTT_COMMANDS = "cow8/commands"

# Estação/cliente para rede
sta_if = network.WLAN(network.STA_IF)

# Cliente MQTT com configurações de conexão
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT)

# Callback (função que é chamada quando o cliente recebe uma mensagem de um tópico em que está subscrito)
def callback(topic, msg):
    print(f"{topic.decode()}: {msg.decode()}")
    
    if topic.decode() == 'cow8/commands':
        handle_commands(topic, msg)
        

def handle_commands(topic, msg):
    data = ujson.loads(msg.decode())
        
    if "uid" not in data or "command" not in data:
        print(f"Ill formed command received: {data}")
        return
    
    if data['uid'] == MQTT_CLIENT_ID:
        if data['command'] == 'TARE':
            print('Command received: TARE')
            info_sound()
            hx.tare(10)
        elif data['command'] == 'DISABLE':
            print('Command received: DISABLE')
            info_sound()
            global disable
            disable = True
            send_status('Desabilitado')
        elif data['command'] == 'ENABLE':
            print('Command received: ENABLE')
            info_sound()
            global disable
            disable = False
            send_status('Online')
        elif data['command'] == 'POWEROFF':
            print('Command received: POWEROFF')
            info_sound()
            global disable
            disable = False
            send_status('Offline')
            raise KeyboardInterrupt
        else:
            print(f"Unknown command: {data['command']}")
            warning_sound()

def send_status(status):
    data = {
        'uid': MQTT_CLIENT_ID,
        'status': status
    }
    
    json = ujson.dumps(data)    
    client.publish(MQTT_STATUS, json)    

# Função que realiza a tentativa de conexão com uma rede wifi.
def do_connect_wifi(retries=3):
    for _ in range(retries):
        try:
            print("Conectando ao Wi-Fi", end="")
    
            sta_if.active(True)
            sta_if.connect(WIFI_SSID, WIFI_PASSWORD)

            while not sta_if.isconnected():
                print(".", end="")
                sleep(1)

            print("\nConectado à internet!")
            return
        except Exception as e:
            print("Erro na conexão Wi-FI, tentando novamente...")
            warning_sound()
    
    print("Falha na conexão Wi-FI. Abortando...")
    error_sound()
    sys.exit(1)


# Função que realiza a conexão com o broker MQTT
def do_connect_mqtt(retries=3):
    for _ in range(retries):
        try:
            print("Conectando ao servidor MQTT...")

            # Configura callback
            client.set_callback(callback)

            # Faz a conexão
            client.connect()

            # Subscreve nos tópicos de comandos e configurações
            client.subscribe(MQTT_COMMANDS) 

            print("Conectado!")
            send_status('Online')
            return
        except Exception as e:
            print("Erro na conexão com o MQTT, tentando novamente...")
            warning_sound()
            sleep(2)

    
    print("Falha na conexão com o MQTT. Abortando...")
    error_sound()
    sys.exit(1)

counter = 0
refresh = 10
def refresh_status():
    global counter
    counter += 1
    
    if counter >= refresh:
        counter = 0
        print("Refreshing status...")
        if not disable:
            send_status('Online')
        else:
            send_status('Desabilitado')

startup_sound()
do_connect_wifi()
do_connect_mqtt()

try:
    while True:
        sleep(1)
        client.check_msg()
        refresh_status()
    
        if disable:
            # Quando desabilitado, apenas abre as porteiras e não faz medição
            servo1.move(0)
            servo2.move(90)
            continue
    
        servo1.move(90)
        servo2.move(0)
    
        print("Esperando por tag NFC...")
    
        if (nfc.is_card_present()):
            print("Tag nfc detectada!")
        
            status, tag_type, uid, data = nfc.read_block(DEFAULT_BLOCK)
            
            if status == nfc.OK:
                cow_uid = b2a_base64(hexlify(bytearray(data))).decode().rstrip("\n")
                cow_weight = round(hx.weight(10))
            
                print("Tipo de Tag: 0x%02x" % tag_type)
                print("UID: 0x%02x%02x%02x%02x" % (uid[0], uid[1], uid[2], uid[3]))
                print(f"ID: {cow_uid}")
                print(f"Peso medido na balanca: {cow_weight}")
            
                data = {
                    "scaleUid": MQTT_CLIENT_ID,
                    "cowUid": cow_uid,
                    "cowWeight": cow_weight
                }
            
                json = ujson.dumps(data)
                client.publish(MQTT_MEASUREMENTS, json)
            
                # Abre porteiras
                servo1.move(0)
                servo2.move(90)
            
                info_sound()

                sleep(WAIT)
except KeyboardInterrupt:
    send_status('Offline')
    buzzer.deinit()
