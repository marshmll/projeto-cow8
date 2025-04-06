from hx711 import HX711
from machine import Pin

dOut = Pin(22, Pin.OUT)
pdSck = Pin(23, Pin.OUT)

hx = HX711(dOut, pdSck)
hx.tare(10)

while True:
    print(round(hx.weight(10)))