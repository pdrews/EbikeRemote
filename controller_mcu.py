import time
import board
from analogio import AnalogIn
import digitalio
import pwmio
from adafruit_motor import servo


# Switch microcontroller

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.button_packet import ButtonPacket

print("Welcome!")

ble = BLERadio()
ble.name = "MyThrottleButton"
# uart = UARTService()
# advertisement = ProvideServicesAdvertisement(uart)
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

analog_in = AnalogIn(board.A0)

def get_voltage(pin):
    return (pin.value * 3.3) / 65536
# print("scan done")

def switch_pressed():
    voltage = get_voltage(analog_in)
    if voltage > 1.9:
        led.value = True
        return True
    else:
        led.value = False
        return False

uart_connection = None
print("Starting the button code, scanning")

# See if any existing connections are providing UARTService.
if ble.connected:
    for connection in ble.connections:
        if connection.complete_name == "MyEbikeController":
            print("Found an existing connection!")
            uart_connection = connection
        break

while True:
    if not uart_connection:
        for adv in ble.start_scan(timeout=5):
            print(adv.complete_name)
            if adv.complete_name == "MyEbikeController":
                print("Found the controller, trying to connect...")
                uart_connection = ble.connect(adv)
                break
        # Stop scanning whether or not we are connected.
        ble.stop_scan()

    while uart_connection and uart_connection.connected:
        button_packet = ButtonPacket(ButtonPacket.BUTTON_1, switch_pressed())
        try:
            uart_connection[UARTService].write(button_packet.to_bytes())
        except OSError:
            pass
        time.sleep(0.05)
    print("Uart disconnected!!")
    uart_connection = None

# led = digitalio.DigitalInOut(board.LED)
# led.direction = digitalio.Direction.OUTPUT

# analog_in = AnalogIn(board.A0)

# # create a PWMOut object on Pin A2.
# pwm = pwmio.PWMOut(board.D5, duty_cycle=2 ** 15, frequency=50)
# max_duty_cycle = 6553
# min_duty_cycle = 3276
# duty_range = max_duty_cycle - min_duty_cycle
# # Create a servo object, my_servo.
# # my_servo = servo.Servo(pwm)

# def set_speed(value):
#     # Value in the range 0...1
#     pwm.duty_cycle = min_duty_cycle + int(duty_range * value)

# def get_voltage(pin):
#     return (pin.value * 3.3) / 65536

# # while True:
# #     led.value = True
# #     time.sleep(0.5)
# #     led.value = False
# #     time.sleep(0.5)

# while True:
#     voltage = get_voltage(analog_in)
#     if voltage > 1.9:
#         led.value = True
#         set_speed(0.5)
#     else:
#         led.value = False
#         set_speed(0.0)
#     # print((get_voltage(analog_in),))

#     # time.sleep(0.1)

# while True:
#     for angle in range(0, 180, 5):  # 0 - 180 degrees, 5 degrees at a time.
#         my_servo.angle = angle
#         time.sleep(0.05)
#     for angle in range(180, 0, -5): # 180 - 0 degrees, 5 degrees at a time.
#         my_servo.angle = angle
#         time.sleep(0.05)