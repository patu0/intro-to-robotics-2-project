import sys
import time
sys.path.append(r'/home/bhagatsj/RobotSystems/lib')

from grayscale_module import Grayscale_Module
from picarx import Picarx
from adc import ADC

class Grayscale_Interpreter():
    """
    Class to interpret the values from the greyscale cameras
    ...

    Attributes
    ----------
    sensitivity : int
        the expected difference between the line and the rest of the floor
    polarity : [1,-1]
        Direction of the sensitivity. Positive will look for a darker 
        line and negative will look for a lighter line
    """

    def __init__(self, sensitivity, polarity=1):
        self.sens = sensitivity
        self.pol = polarity

        assert((self.pol == 1) or (self.pol == -1))

    def get_line_status(self, adc_list):          
        diff1 = (adc_list[0]-adc_list[1])*self.pol
        diff2 = (adc_list[2]-adc_list[1])*self.pol

        if diff1 > self.sens:
            return 'left'
        elif diff2 > self.sens:
            return 'right'
        else:
            return 'unclear'

class Controller():
    '''Class that controls the Picarx'''
    def __init__(self, car, sensitivity, polarity, scale=1.0):
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
        adc_list = self.car.get_adc_value()
        print(adc_list)
        print(self.sensor.get_line_status(adc_list))

def swerve_loop():
    print('drive back and forth over the line')

def drive_straight():
    print('drive straight')

if __name__ == "__main__":
    car = Picarx()
    controller = Controller(car, 75, 1.0)
    while True:
        controller.test()
        time.sleep(1)
