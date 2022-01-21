import sys
sys.path.append(r'/home/bhagatsj/RobotSystems/lib')
from utils import reset_mcu
reset_mcu()

from picarx import Picarx
import time

if __name__ == "__main__":
    px = Picarx()
    px.forward(40)
    time.sleep(5)
    px.stop()

        



