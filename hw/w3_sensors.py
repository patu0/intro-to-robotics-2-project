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
        if fl_list[0] > self.ref and fl_list[1] > self.ref and fl_list[2] > self.ref:
            return 'stop'
        elif fl_list[1] <= self.ref:
            return 'forward'
        elif fl_list[0] <= self.ref:
            return 'right'
        elif fl_list[2] <= self.ref:
            return 'left'

class Controller():
    '''Class that controls the Picarx'''
    def __init__(self, sensitivity, polarity, scale=1.0):
        #Car object
        self.car = car

        #Control specific values
        self.sensor = Grayscale_Interpreter(sensitivity, polarity)
        self.angle = 10
        self.scale = scale

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

    def test(self):
        print(self.sensor.get_line_status())

def swerve_loop():
    print('drive back and forth over the line')

def drive_straight():
    print('drive straight')

if __name__ == "__main__":
    import time
    car = Picarx()
    controller = Controller(car, 50, 220)
    while True:
        controller.test()
        time.sleep(1)
