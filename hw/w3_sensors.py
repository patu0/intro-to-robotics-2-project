import argparse
import sys
import time
import logging

sys.path.append(r'/home/bhagatsj/RobotSystems/lib')
from picarx import Picarx

logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.ERROR , datefmt="%H:%M:%S ")

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

        logging.debug("Diff1: {}".format(diff1))
        logging.debug("Diff2: {}".format(diff2))
        line_direction = "unclear"
        if diff1 > self.sens:
            return 'left'
        elif diff2 > self.sens:
            return 'right'

        logging.debug("Line Direction: {}".format(line_direction))
        return line_direction

    def get_manuever_val(self, adc_list):
        line_direction = self.get_line_status(adc_list)

        maneuver_val = 0
        if line_direction == "left":
            maneuver_val = -1
        elif line_direction == "right":
            maneuver_val = 1

        logging.debug("Manuever Val: {}".format(maneuver_val))
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
        angle = self.scale*self.angle*maneuver_val

        return angle


    def test(self):
        self.get_turn_angle()
        time.sleep(2)

    def swerve_loop(self, duration):
        #Controller loop to drive left and right over a line
        start_time = time.time()
        rel_time = 0

        self.car.forward(30)
        while rel_time < duration:
            angle = self.get_turn_angle()
            self.car.set_dir_servo_angle(angle)
            time.sleep(1.5)
            self.car.set_dir_servo_angle(-angle)
            time.sleep(1)
            self.car.set_dir_servo_angle(0)
            time.sleep(0.5)
            rel_time = time.time() - start_time
        self.car.stop()
        
    def follow_line():
        #Controller loop to follow the line
        print('drive straight')


def main(config):
    print(config.debug)
    if config.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    car = Picarx()
    sensor = Grayscale_Interpreter(75, 1.0)
    controller = Controller(car, sensor, scale=0.9)
    while True:
        controller.test()
    #controller.swerve_loop(10)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Debug flag')
    main(parser.parse_args())
