#!/usr/bin/python3
# coding=utf8
import logging
import time
import sys

sys.path.append('ArmPi/')

from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.ERROR , datefmt="%H:%M:%S ")
logger = logging.getLogger(__name__)

class Flip():
    def __init__(self, shared_state):
        self.state = shared_state
        self.index = 0

    def setBuzzer(self, timer):
        Board.setBuzzer(0)
        Board.setBuzzer(1)
        time.sleep(timer)
        Board.setBuzzer(0)

    def set_rgb(self, color):
        if color == "red":
            Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
            Board.RGB.show()
        elif color == "green":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
            Board.RGB.show()
        elif color == "blue":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
            Board.RGB.show()
        else:
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
            Board.RGB.show()

    def flip_block(self):
        '''Rotate block'''
        while True:
            if self.state.isRunning:
                if self.state.detect_color != 'None' and self.state.start_flip:
                    self.set_rgb(self.state.detect_color)
                    self.setBuzzer(0.1)        
                    result = self.state.AK.setPitchRangeMoving((self.state.world_X, self.state.world_Y, 7), -90, -90,
                                                               0)  
                    if result == False:
                        self.state.unreachable = True
                    else:
                        self.state.unreachable = False
                        time.sleep(result[2] / 1000)

                        if not self.state.isRunning:
                            continue
                        
                        logger.debug("Move into position, open grippers")
                        servo2_angle = getAngle(self.state.world_X, self.state.world_Y, self.state.rotation_angle)
                        Board.setBusServoPulse(1, self.state.servo1 - 280, 500)  
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(0.5)

                        if not self.state.isRunning:
                            continue
                        logger.debug("lower arm to 2cm")
                        self.state.AK.setPitchRangeMoving((self.state.world_X, self.state.world_Y, 2.5), -90, -90, 0, 1000)
                        time.sleep(1.5)

                        if not self.state.isRunning:
                            continue
                        logger.debug("Close grippers")
                        Board.setBusServoPulse(1, self.state.servo1, 500)  # 夹持器闭合
                        time.sleep(0.8)

                        if not self.state.isRunning:
                            continue
                        logger.debug("Moves up")
                        Board.setBusServoPulse(2, 500, 500)
                        self.state.AK.setPitchRangeMoving((self.state.world_X, self.state.world_Y, 5), -90, -90, 0, 1000)
                        time.sleep(1)

                        logger.debug("Rotate block")
                        Board.setBusServoPulse(3, 300, 500)
                        time.sleep(1.25)
                        Board.setBusServoPulse(5, 240, 500)
                        time.sleep(1.25)
                     
                        if not self.state.isRunning:
                            continue 
                        logger.debug("place block in middle")
                        self.state.AK.setPitchRangeMoving((0, 18, 0.5), -90, -90, 0, 1000)   #place it in the middle
                        time.sleep(0.8)

                        if not self.state.isRunning:
                            continue 
                        logger.debug("open grippers")
                        Board.setBusServoPulse(1, self.state.servo1 - 400, 500)  # 爪子张开  ，放下物体
                        time.sleep(1.25)

                        logger.debug("return to init state")
                        self.state.init() 
                        time.sleep(1.5)

                        self.state.detect_color = 'None'
                        self.state.get_roi = False
                        self.state.start_flip = False
                        self.state.start_pick_up = False
                        print("Done flipping, Flip Flag: {}, Move Flag: {}".format(self.state.start_flip, self.state.start_pick_up))
                        self.set_rgb(self.state.detect_color)
            else:
                if self.state._stop:
                    self.state._stop = False
                    Board.setBusServoPulse(1, self.state.servo1 - 70, 300)
                    time.sleep(0.5)
                    Board.setBusServoPulse(2, 500, 500)
                    self.state.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
                    time.sleep(1.5)
                time.sleep(0.01)

    def sort_blocks(self):
        '''Sort blocks into their spot'''
        coordinates = [(-15 + 0.5, 0 - 0.5,  1.5), (-15 + 0.5, 6 - 0.5,  1.5), (-15 + 0.5, 12 - 0.5, 1.5)]
        while True:
            if self.state.isRunning:        
                if self.state.detect_color != 'None' and self.state.start_pick_up:
                    self.set_rgb(self.state.detect_color)
                    self.setBuzzer(0.1)
                    result = self.state.AK.setPitchRangeMoving((self.state.world_X, self.state.world_Y, 7), -90, -90, 0)  
                    if result == False:
                        self.state.unreachable = True
                    else:
                        self.state.unreachable = False
                        time.sleep(result[2]/1000)

                        if not self.state.isRunning:
                            continue
                        servo2_angle = getAngle(self.state.world_X, self.state.world_Y, self.state.rotation_angle) #计算夹持器需要旋转的角度
                        Board.setBusServoPulse(1, self.state.servo1 - 280, 500)  # 爪子张开
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(0.5)
                        
                        if not self.state.isRunning:
                            continue
                        self.state.AK.setPitchRangeMoving((self.state.world_X, self.state.world_Y, 1.5), -90, -90, 0, 1000)
                        time.sleep(1.5)

                        if not self.state.isRunning:
                            continue
                        Board.setBusServoPulse(1, self.state.servo1, 500)  #夹持器闭合
                        time.sleep(0.8)

                        if not self.state.isRunning:
                            continue
                        Board.setBusServoPulse(2, 500, 500)
                        self.state.AK.setPitchRangeMoving((self.state.world_X, self.state.world_Y, 12), -90, -90, 0, 1000)  #机械臂抬起
                        time.sleep(1)

                        if not self.state.isRunning:
                            continue
                        result = self.state.AK.setPitchRangeMoving((coordinates[self.index][0], coordinates[self.index][1], 12), -90, -90, 0)   
                        time.sleep(result[2]/1000)
                        
                        if not self.state.isRunning:
                            continue                   
                        servo2_angle = getAngle(coordinates[self.index][0], coordinates[self.index][1], -90)
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(0.5)

                        if not self.state.isRunning:
                            continue
                        self.state.AK.setPitchRangeMoving((coordinates[self.index][0], coordinates[self.index][1], coordinates[self.index][2] + 3), -90, -90, 0, 500)
                        time.sleep(0.5)
                        
                        if not self.state.isRunning:
                            continue                    
                        self.state.AK.setPitchRangeMoving((coordinates[self.index]), -90, -90, 0, 1000)
                        time.sleep(0.8)

                        if not self.state.isRunning:
                            continue
                        Board.setBusServoPulse(1, self.state.servo1 - 200, 500)  # 爪子张开  ，放下物体
                        time.sleep(0.8)

                        if not self.state.isRunning:
                            continue
                        self.state.AK.setPitchRangeMoving((coordinates[self.index][0], coordinates[self.index][1], 12), -90, -90, 0, 800)
                        time.sleep(0.8)

                        self.state.init()  # 回到初始位置
                        time.sleep(1.5)

                        self.state.detect_color = 'None'
                        self.state.get_roi = False
                        self.state.start_flip = False
                        self.state.start_pick_up = False
                        self.state.word_section_ind += 1
                        self.index += 1
                        print("Done moving, Flip Flag: {}, Move Flag: {}".format(self.state.start_flip, self.state.start_pick_up))
                        self.set_rgb(self.state.detect_color)
            else:
                if self.state._stop:
                    self.state._stop = False
                    Board.setBusServoPulse(1, self.state.servo1 - 70, 300)
                    time.sleep(0.5)
                    Board.setBusServoPulse(2, 500, 500)
                    self.state.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
                    time.sleep(1.5)
                time.sleep(0.01)