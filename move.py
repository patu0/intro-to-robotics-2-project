import sys
sys.path.append(r'/home/bhagatsj/RobotSystems/lib')
from utils import reset_mcu
reset_mcu()

from picarx_improved import Picarx
import time


def forward_and_backwards(px, speed, sleep_time):
    px.forward(speed)
    time.sleep(sleep_time)
    px.backward(speed)
    time.sleep(sleep_time)

if __name__ == "__main__":
    px = Picarx()
    px.set
    forward_and_backwards(px, 50, 2)


