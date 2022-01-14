import sys
sys.path.append(r'/home/bhagatsj/RobotSystems/lib')
from utils import reset_mcu
reset_mcu()

from picarx import Picarx
import time


def forward_and_backwards(px, speed, time):
    px.forward(speed)
    time.sleep(time)
    px.backward(speed)
    time.sleep(time)

if __name__ == "__main__":
    px = Picarx()
    forward_and_backwards(px, 50, time)


