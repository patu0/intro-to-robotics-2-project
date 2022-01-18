import sys
import time
sys.path.append(r'/home/bhagatsj/RobotSystems/lib')

from grayscale_module import Grayscale_Module
from picarx import Picarx
from adc import ADC

class Grayscale_Interpreter():
    '''Container class for the grayscale interpreter values'''
    def __init__(self, sensitivity, polarity):
        self.sensitivity = sensitivity
        self.polarity = polarity

    def get_line_status(self, fl_list):
        if fl_list[0] <= self.ref:
            return 'right'
        elif fl_list[2] <= self.ref:
            return 'left'

class Controller():
    '''Class that controls the Picarx'''
    def __init__(self, scale, sensitivity, polarity, ref=1000):
        #Car object
        self.car = Picarx()

        #Control specific values
        self.sensor = Grayscale_Interpreter(sensitivity, polarity)
        self.angle = 10
        self.scale = scale
        self.ref = ref

    def get_line_location(self):
        adc_list = self.car.get_adc_value()
        line_direction = self.sensor.get_line_status(adc_list)

        maneuver_val = -1 if line_direction == "left" else 1
        return maneuver_val

    def turn(self, maneuver_val):
        angle = self.scale*self.angle*maneuver_val
        self.car.set_dir_servo_angle(angle)
        time.sleep(1)
        self.car.set_dir_servo_angle(0)



if __name__ == "__main__":
    import time
    GM = Grayscale_Module(950)
    while True:
        print(GM.get_grayscale_data())
        time.sleep(1)
