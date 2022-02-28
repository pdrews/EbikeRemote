print("Hello World!")

import time
import board
from analogio import AnalogIn
import digitalio
import pwmio
# from adafruit_motor import servo


# Switch microcontroller

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.button_packet import ButtonPacket

ble = BLERadio()
ble.name = "MyEbikeController"
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

ble = BLERadio()

# create a PWMOut object on Pin 5!(vhi output level).
pwm = pwmio.PWMOut(board.D5, duty_cycle=2 ** 15, frequency=50)
max_duty_cycle = 6553
min_duty_cycle = 3276
duty_range = max_duty_cycle - min_duty_cycle

def set_speed(value):
    # Value in the range 0...1
    pwm.duty_cycle = min_duty_cycle + int(duty_range * value)
    
last_button_time = time.monotonic_ns()

while True:
    ble.start_advertising(advertisement)
    while not ble.connected:
        print("TryingToConnect!")
        time.sleep(0.1)
    print("Connected!")
    while ble.connected:
        if uart.in_waiting:
            packet = Packet.from_stream(uart)
            if isinstance(packet, ButtonPacket):
                if packet.pressed:
                    print("Pressed")
                    last_button_time = time.monotonic_ns()
                    led.value = True
                elif not packet.pressed:
                    print("Not pressed")
                    # allow 0.2s without a packet before we drop.
                    last_button_time = time.monotonic_ns()
                    led.value = False
        # print(time.monotonic_ns() - last_button_time, 2*1e8)
        if (time.monotonic_ns() - last_button_time) > 2*1e8:
            led.value = False
