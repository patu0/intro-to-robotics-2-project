#!/usr/bin/python3
# coding=utf8
import argparse
import sys
sys.path.append('ArmPi/')
import cv2
import time
import math
import threading
import logging
import numpy as np
from LABConfig import color_range
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *
from camera import Camera

logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.ERROR , datefmt="%H:%M:%S ")


class Arm():
    def __init__(self, color):
        self.AK = ArmIK()
        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
        }
        self.count = 0
        self.track = False
        self._stop = False
        self.get_roi = False
        self.center_list = []
        self.first_move = True
        self.__isRunning = False
        self.detect_color = 'None'
        self.action_finish = True
        self.start_pick_up = False
        self.start_count_t1 = True
        self.move_square = False #TODO: Do we need this here?

        self.__target_color = (color,)
        logging.debug("Set color: {}".format(self.__target_color))
        self.servo1 = 500
        self.rect = None
        self.size = (640, 480)
        self.rotation_angle = 0
        self.unreachable = False
        self.world_X = 0
        self.world_Y = 0
        self.world_x = 0
        self.world_y = 0
        self.t1 = 0
        self.roi = ()
        self.last_x = 0
        self.last_y = 0

        #Reset servos
        self.init()

    def init(self):
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

    def start(self):
        #Reset state variables        
        self.count = 0
        self._stop = False
        self.track = False
        self.get_roi = False
        self.center_list = []
        self.first_move = True
        self.detect_color = 'None'
        self.action_finish = True
        self.start_pick_up = False
        self.start_count_t1 = True

        #Set is_Running flag
        self.__isRunning = True

    
    def stop(self):
        self._stop = True
        self.__isRunning = False

    def getAreaMaxContour(self, contours):
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours: 
            contour_area_temp = math.fabs(cv2.contourArea(c)) 
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:
                    area_max_contour = c

        return area_max_contour, contour_area_max

    def setBuzzer(self,timer):
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

    #TODO: Below here are the perception methods
    def get_max_area(self, frame_lab):
        frame_mask = cv2.inRange(frame_lab, color_range[i][0], color_range[i][1])  # 对原图像和掩模进行位运算
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # 开运算
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # 闭运算
        contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # 找出轮廓
        areaMaxContour, area_max = self.getAreaMaxContour(contours)  # 找出最大轮廓
        return areaMaxContour, area_max
    
    def draw_box(self, box, img):
        cv2.drawContours(img, [box], -1, self.range_rgb[self.detect_color], 2)
        cv2.putText(img, '(' + str(self.world_x) + ',' + str(self.world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[self.detect_color], 1)
        distance = math.sqrt(pow(self.world_x - self.last_x, 2) + pow(self.world_y - self.last_y, 2))
        return img, distance

    def update_state(self):
        self.center_list.extend((self.world_x, self.world_y))
        self.count += 1
        if self.start_count_t1:
            self.start_count_t1 = False
            self.t1 = time.time()
        if time.time() - self.t1 > 1.5:
            self.rotation_angle = self.rect[2]
            self.start_count_t1 = True
            self.world_X, self.world_Y = np.mean(np.array(self.center_list).reshape(self.count, 2), axis=0)
            self.count = 0
            self.center_list = []
            self.start_pick_up = True

    def update_world_coord(self, roi):
        img_centerx, img_centery = getCenter(self.rect, self.roi, self.size, square_length)
        self.world_x, self.world_y = convertCoordinate(img_centerx, img_centery, self.size)
        self.last_x, self.last_y = self.world_x, self.world_y
       

    def identify_multiple_colors(self, img):    
        img_copy = img.copy()
        img_h, img_w = img.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)

        if not self.__isRunning:
            return img

        frame_resize = cv2.resize(img_copy, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        if self.get_roi and not self.start_pick_up:
            get_roi = False
            frame_gb = getMaskROI(frame_gb, self.roi, self.size)    
        
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # 将图像转换到LAB空间

        color_area_max = None
        max_area = 0
        areaMaxContour_max = 0
        
        if not self.start_pick_up:
            for i in color_range:
                if i in self.__target_color:
                    areaMaxContour, area_max = self.get_max_area(frame_lab)
                    if areaMaxContour is not None:
                        if area_max > max_area:  # 找最大面积
                            max_area = area_max
                            color_area_max = i
                            areaMaxContour_max = areaMaxContour
            if max_area > 2500:  # 有找到最大面积
                rect = cv2.minAreaRect(areaMaxContour_max)
                box = np.int0(cv2.boxPoints(rect))
                
                self.roi = getROI(box)
                self.get_roi = True
                self.update_world_coord()

                if not self.start_pick_up:
                    img, distance = self.draw_box(box, img)

                if not self.start_pick_up:
                    if color_area_max == 'red':  # 红色最大
                        color = 1
                    elif color_area_max == 'green':  # 绿色最大
                        color = 2
                    elif color_area_max == 'blue':  # 蓝色最大
                        color = 3
                    else:
                        color = 0
                    self.color_list.append(color)

                    # 累计判断
                    if distance < 0.5:
                        self.update_state()
                    else:
                        self.t1 = time.time()
                        self.start_count_t1 = True
                        self.count = 0
                        self.center_list = []

                    if len(self.color_list) == 3:  # 多次判断
                        # 取平均值
                        color = int(round(np.mean(np.array(self.color_list))))
                        self.color_list = []
                        if color == 1:
                            self.detect_color = 'red'
                            self.draw_color = self.range_rgb["red"]
                        elif color == 2:
                            self.detect_color = 'green'
                            self.draw_color = self.range_rgb["green"]
                        elif color == 3:
                            self.detect_color = 'blue'
                            self.draw_color = self.range_rgb["blue"]
                        else:
                            self.detect_color = 'None'
                            self.draw_color = self.range_rgb["black"]
            else:
                if not self.start_pick_up:
                    self.draw_color = (0, 0, 0)
                    self.detect_color = "None"
        
        if self.move_square:
            cv2.putText(img, "Make sure no blocks in the stacking area", (15, int(img.shape[0]/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)    
        
        cv2.putText(img, "Color: " + self.detect_color, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, self.draw_color, 2)
        
        return img
        
    def identify_single_color(self, img):
        img_copy = img.copy()
        img_h, img_w = img.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)
        
        if not self.__isRunning:
            return img
        
        frame_resize = cv2.resize(img_copy, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        if self.get_roi and self.start_pick_up:
            self.get_roi = False
            frame_gb = getMaskROI(frame_gb, self.roi, self.size)    
        
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB) 
        
        area_max = 0
        areaMaxContour = 0
        if not self.start_pick_up:
            for i in color_range:
                if i in self.__target_color:
                    self.detect_color = i
                    areaMaxContour, area_max = self.get_max_area(frame_lab)
                    
                   
            if area_max > 2500:  # 有找到最大面积
                self.rect = cv2.minAreaRect(areaMaxContour)
                box = np.int0(cv2.boxPoints(self.rect))

                self.roi = getROI(box)
                self.get_roi = True

                self.update_world_coord()
                self.track = True

                img, distance = self.draw_box(box, img)

                if self.action_finish:
                    if distance < 0.3:
                        self.update_state()
                    else:
                        self.t1 = time.time()
                        self.start_count_t1 = True
                        self.count = 0
                        self.center_list = []
        return img

def main(config):
    #Line following simultaneity
    if config.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    #Init arm and camera objects
    arm = Arm('red')
    camera = Camera()
    arm.start()
    camera.camera_open()

    # Use the threads the same way original code did
    # they share too much information to quickly integrate
    # a consumer-producer framework

    #Start move thread
    # move_thread = threading.Thread(target=arm.move, daemon=True)
    # move_thread.start()

    #Start camera thread
    camera_threa = threading.Thread(target=camera.camera_task, args=(), daemon=True)
    camera_threa.start()

    #Start main thread, which executes the run function
    while True:
        img = camera.frame
        if img is not None:
            frame = img.copy()
            Frame = arm.identify_color(frame)           
            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
    camera.camera_close()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Debug flag')
    main(parser.parse_args())
    
