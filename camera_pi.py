import cv2
import time
import udp
import math
import imutils
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse

class Camera(object):
    def __init__(self):        
        self.video = VideoStream(usePiCamera=1 > 0).start()
        time.sleep(2.0)
        self.f = open("pos.csv", "w")
        self.yellowLower = (23, 130, 14)
        self.yellowUpper = (45, 255, 255)
        #self.yellowLower = (10, 100, 125)
        #self.yellowUpper = (30, 255, 255)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.xPos = [0]
        self.yPos = [0]
        self.zPos = [0]
        self.direction = 0
        self.bounced = 0
        self.i = 0
        self.j = 0
        self.cxlast = 0
        self.cylast = 0
        self.cx = 0
        self.cy = 0
        self.now = time.time()
        self.lasttime = self.now
        self.prod = udp.producer()
    def __del__(self):
        self.video.release()
        self.f.close()
    def get_frame(self):
        frame = self.video.read()
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, self.yellowLower, self.yellowUpper)
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None
	radius = 0
	x = 0
	y = 0

	if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
	    M = cv2.moments(c)            
	    if M["m00"] == 0:
		self.cx = self.cxlast
		self.cy = self.cylast
	    else:
		self.cxlast = self.cx
		self.cylast = self.cy
		self.cx = int(M["m10"] / M["m00"])
		self.cy = int(M["m01"] / M["m00"])
		center = (self.cx, self.cy)
	    if radius > 5:
		self.i += 1
		cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
		cv2.circle(frame, center, 5, (0, 0, 255), -1)
		self.xPos.append(math.ceil(int(x)))
		self.yPos.append(math.ceil(int(y)))
		self.zPos.append(math.ceil(2*radius))
		coord = 'Bounced: ' + str(int(self.bounced))
                cv2.putText(frame, coord, (10,50), self.font, 0.6, (0,0,255),2,cv2.LINE_AA)
		if self.yPos[self.i] > self.yPos[self.i-3] and self.direction == 0:
                    self.direction = 1
		if self.yPos[self.i] < self.yPos[self.i-3] and self.direction == 1:
		    self.direction = 0
		    self.bounced += 1
		    self.j = 0
	    else:
                coord = 'Bounced: ' + str(int(self.bounced))
                cv2.putText(frame, coord, (10,50), self.font, 0.6, (0,0,255),2,cv2.LINE_AA)
                self.j += 1
                if self.j >= 50:
                    self.bounced = 0
        self.now = time.time()
        fps = 1 / (self.now - self.lasttime)
        self.lasttime = self.now
        self.prod.send(self.bounced)
        writestr = str(self.now)+","+str(self.yPos[self.i])+","+str(self.bounced)+","+str(len(cnts))+","+str(radius)+","+str(x)+","+str(y)+"\n"
        self.f.write(writestr)
	frame = imutils.resize(frame, width=400)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()