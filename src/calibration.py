from machine import Pin
from hx711 import HX711
from time import sleep

# Initialize the HX711 with the appropriate pins
dOut = Pin(18, Pin.IN)  # GPIO18 for data pin
pdSck = Pin(19, Pin.OUT)  # GPIO19 for clock pin

hx = HX711(dOut, pdSck, HX711.SELA128)  # Use channel A with gain 128

# Step 1: Tare the scale (set zero point)
print("Tarando a balança...")
hx.tare(10)  # Take 10 samples to calculate the tare value
print("Tara definida com o valor:", hx._tare)

# Step 2: Place a known weight on the load cell
known_weight = int(input("Digite o peso conhecido para calibração: "))
input(f"Coloque o peso ({known_weight}g) sobre a balança e pressione Enter para continuar...")

# Step 3: Measure the raw value with the known weight
raw_value_with_weight = hx.get_raw()
print("Valor raw com o peso:", raw_value_with_weight)

# Step 4: Calculate the calibration factor
raw_value_without_weight = hx._tare
calibration_factor = (raw_value_with_weight - raw_value_without_weight) / known_weight
print("Fator de calibração calculado:", calibration_factor)

# Step 5: Update the calibration factor in the HX711 object
hx.cal_factor(calibration_factor)
print("Fator de calibração atualizado.")

# Step 6: Verify the calibration
print("Verificando calibração...")
measured_weight = hx.weight(10)  # Take 10 samples to calculate the weight
print("Peso medido: {:.2f} g".format(measured_weight))

## TEMP!!!
hx.cal_factor = hx.CALIBRATION_FACTOR

# Continuous weight measurement
while True:
    weight = hx.weight(10)  # Take 10 samples to calculate the weight
    print("Peso: {:.2f} g".format(weight))
    sleep(1)  # Wait for 1 second before the next reading

