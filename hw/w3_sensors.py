import sys
import time
import logging
sys.path.append(r'/home/bhagatsj/RobotSystems/lib')

from grayscale_module import Grayscale_Module
from picarx import Picarx
from adc import ADC

logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO , datefmt="%H:%M:%S ")
logging.getLogger().setLevel(logging.DEBUG)

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

    def get_manuever_val(self, adc_list):
        logging.debug(adc_list)
        line_direction = self.get_line_status(adc_list)

        maneuver_val = -1 if line_direction == "left" else 1
        return maneuver_val

class Controller():
    '''Class that controls the Picarx'''
    def __init__(self, car, sensor, scale=1.0):
        self.car = car
        self.sensor = sensor
        self.angle = 10
        self.scale = scale

    def get_turn_angle(self):
        #Calculate turn angle
        adc_list = self.car.get_adc_value()
        maneuver_val = self.sensor.get_manuever_val(adc_list)
        return self.scale*self.angle*maneuver_val

    def swerve_loop(self, duration):
        #Controller loop to drive left and right over a line
        rel_time = 0
        self.car.forward(30)
        while rel_time < duration:
            angle = self.get_turn_angle()
            if angle != 0:
                self.car.set_dir_servo_angle(angle)
                time.sleep(1)
                self.car.set_dir_servo_angle(0)
                time.sleep(0.5)
            rel_time += 0.6
        self.car.stop()
        
    def follow_line():
        #Controller loop to follow the line
        print('drive straight')

if __name__ == "__main__":
    car = Picarx()
    sensor = Grayscale_Interpreter(75, 1.0)
    controller = Controller(car, sensor)

    controller.swerve_loop(6)
