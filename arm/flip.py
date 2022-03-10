#!/usr/bin/python3
# coding=utf8
from asyncio.log import logger
import time
import sys

sys.path.append('ArmPi/')

from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *
import logging


logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.ERROR , datefmt="%H:%M:%S ")

class Flip():
    def __init__(self, shared_state):
        self.state = shared_state

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

    def rotate_block(self):
        '''Stack blocks'''
        coordinate = {
            'red': (-15 + 1, -7 - 0.5, 1.5),
            'green': (-15 + 1, -7 - 0.5, 1.5),
            'blue': (-15 + 1, -7 - 0.5, 1.5),
        }
        dz = 2.5
        z_r = coordinate['red'][2]

        while True:
            if self.state.isRunning:
                if self.state.detect_color != 'None' and self.state.start_pick_up:  # 如果检测到方块没有移动一段时间后，开始夹取
                    self.set_rgb(self.state.detect_color)
                    self.setBuzzer(0.1)
                    # 高度累加
                    z = z_r
                    z_r += dz
                    if z == 2 * dz + coordinate['red'][2]:
                        z_r = coordinate['red'][2]
                    if z == coordinate['red'][2]:
                        self.state.move_square = True
                        time.sleep(3)
                        self.state.move_square = False

                    result = self.state.AK.setPitchRangeMoving((self.state.world_X, self.state.world_Y, 7), -90, -90,
                                                               0)  # 移到目标位置，高度5cm
                    if result == False:
                        self.state.unreachable = True
                    else:
                        self.state.unreachable = False
                        time.sleep(result[2] / 1000)

                        if not self.state.isRunning:
                            continue
                        # Calculate rotation angle and 
                        servo2_angle = getAngle(self.state.world_X, self.state.world_Y, self.state.rotation_angle)

                        logger.debug("open grippers")
                        Board.setBusServoPulse(1, self.state.servo1 - 280, 500)  # Open grippers
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(0.5)

                        if not self.state.isRunning:
                            continue
                        logger.debug("lower to height of 2 cm")
                        self.state.AK.setPitchRangeMoving((self.state.world_X, self.state.world_Y, 2), -90, -90, 0,
                                                          1000)  # lower the height to 2cm
                        time.sleep(1.5)

                        if not self.state.isRunning:
                            continue
                        logger.debug("close gripper")
                        Board.setBusServoPulse(1, self.state.servo1, 500)  # gripper closed
                        time.sleep(0.8)

                        if not self.state.isRunning:
                            continue
                        logger.debug("raise arm")
                        Board.setBusServoPulse(2, 500, 500)
                        self.state.AK.setPitchRangeMoving((self.state.world_X, self.state.world_Y, 12), -90, -90, 0,
                                                          1000)  # robotic arm is raised
                        time.sleep(1)

                        if not self.state.isRunning:
                            continue
                        logger.debug("???")
                        self.state.AK.setPitchRangeMoving(
                            (coordinate[self.state.detect_color][0], coordinate[self.state.detect_color][1], 12), -90,
                            -90, 0, 1500)
                        time.sleep(5)

                        if not self.state.isRunning:
                            continue

                        logger.debug("???")
                        servo2_angle = getAngle(coordinate[self.state.detect_color][0],
                                                coordinate[self.state.detect_color][1], -90)
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(5)

                        if not self.state.isRunning:
                            continue
                        logger.debug("???")
                        self.state.AK.setPitchRangeMoving(
                            (coordinate[self.state.detect_color][0], coordinate[self.state.detect_color][1], z + 3),
                            -90, -90, 0, 500)
                        time.sleep(5)

                        if not self.state.isRunning:
                            continue
                        logger.debug("???")
                        self.state.AK.setPitchRangeMoving(
                            (coordinate[self.state.detect_color][0], coordinate[self.state.detect_color][1], z), -90,
                            -90, 0, 1000)
                        time.sleep(5)

                        if not self.state.isRunning:
                            continue
                        logger.debug("Open grippers and drop object")
                        Board.setBusServoPulse(1, self.state.servo1 - 200, 500)  # Claws open to drop objects
                        time.sleep(1)

                        if not self.state.isRunning:
                            continue
                        self.state.AK.setPitchRangeMoving(
                            (coordinate[self.state.detect_color][0], coordinate[self.state.detect_color][1], 12), -90,
                            -90, 0, 800)
                        time.sleep(0.8)

                        logger.debug("return to original position")
                        self.state.init()  # return to original position
                        time.sleep(1.5)

                        self.state.detect_color = 'None'
                        self.state.get_roi = False
                        self.state.start_pick_up = False
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
