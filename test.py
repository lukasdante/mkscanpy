import can
import time
import os
from mksCAN import Motor

bus = can.Bus(interface='socketcan', channel='vcan0', bitrate=500000)
x_motor = Motor(name='x-axis', bus=bus, version='42D', can_id=0x01, mode='serial-vfoc')

x_motor.show_params()