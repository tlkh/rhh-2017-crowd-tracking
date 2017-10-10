import numpy as np
import cv2
import time
import imutils
from collections import deque
import sys, traceback
import paho.mqtt.client as mqttClient

cv2.setUseOptimized(True)

from camera import PiVideoStream


this = sys.modules[__name__]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected
        Connected = True
    else:
        print("Connection failed")

Connected = False   #global variable for the state of the connection
 
broker_address= "m13.cloudmqtt.com"
port = 10879
 
client = mqttClient.Client("Python") #create new instance
client.username_pw_set("camera", password="asdf1234") #set username and password
client.on_connect= on_connect #attach function to callback
client.connect(broker_address, port=port) #connect to broker

class BackGroundSubtractor:
    # When constructing background subtractor, we
    # take in two arguments:
    # 1) alpha: The background learning factor, its value should
    # be between 0 and 1. The higher the value, the more quickly
    # your program learns the changes in the background. Therefore, 
    # for a static background use a lower value, like 0.001. But if 
    # your background has moving trees and stuff, use a higher value,
    # maybe start with 0.01.
    # 2) firstFrame: This is the first frame from the video/webcam.
    def __init__(self,alpha,firstFrame):
        self.alpha  = alpha
        self.backGroundModel = firstFrame

    def getForeground(self,frame):
        # apply the background averaging formula:
        # NEW_BACKGROUND = CURRENT_FRAME * ALPHA + OLD_BACKGROUND * (1 - APLHA)
        self.backGroundModel =  frame * self.alpha + self.backGroundModel * (1 - self.alpha)

        # after the previous operation, the dtype of
        # self.backGroundModel will be changed to a float type
        # therefore we do not pass it to cv2.absdiff directly,
        # instead we acquire a copy of it in the uint8 dtype
        # and pass that to absdiff.

        return cv2.absdiff(self.backGroundModel.astype(np.uint8),frame)

cap = PiVideoStream().start()

time.sleep(0.5)
#cap = cv2.VideoCapture('opencv_test2.mov')

# define the lower and upper boundaries of the "colour"
# ball in the HSV color space
colourLower = (0, 0, 0)
colourUpper = (255, 80, 60)
 
newframe = False
firstCap = True

while True:
    frame = cap.read()
        
    newframe = True
    # resize the frame, blur it, and convert it to the HSV
    # color space
    #frame = imutils.resize(frame, width=320)
    #frame = cv2.pyrDown(frame)
    blur = cv2.GaussianBlur(frame,(11,11),0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    if firstCap == True:
        print("first capture")
        #backSubtractor = BackGroundSubtractor(0.001,frame)
        firstCap = False
        
    else:
        # get the foreground
        #mask = backSubtractor.getForeground(frame)
 
        # construct a mask for the color, then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        
        #mask = mask.astype('uint8')
        #mask = np.uint8(mask)
        mask = cv2.inRange(hsv, colourLower, colourUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        #cv2.imshow('mask',mask)
     
        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None

        # only proceed if at least one contour was found
        cv2.drawContours(frame, cnts, -1, (255,0,0), 1)
        
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        #c = max(cnts, key=cv2.contourArea)
        c_i = 0
        #print(cnts)
        
        for c in cnts:
            if newframe == True :
                c_i = 0
                people_count = 0
                newframe = False
                
            ((x, y), radius) = cv2.minEnclosingCircle(c)

            if (str(c) == str(cnts[-1])):
                lastobject = True
            else:
                lastobject = False

            if (12 < radius < 300):
                c_i+=1
                try:
                    print("processing track" + str(c_i) + ": " + str(globals()['pts%s' % c_i]))
                except Exception as e:
                    globals()['pts%s' % c_i] = deque(maxlen=128)
                    globals()['time%s' % c_i] = deque(maxlen=128)

                cv2.drawContours(frame, c, -1, (0,255,0), 2)
                print("number of circles: " + str(c_i))
                
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                upper_threshold = 40
                lower_threshold = -40
                
                try:
                    last_points = globals()['pts%s' % c_i]
                    last_point = last_points[-1]
                    if (lower_threshold < (center[0] - last_point[0]) < upper_threshold) and (lower_threshold < (center[1] - last_point[1]) < upper_threshold):
                        globals()['pts%s' % c_i].append(center)
                        globals()['time%s' % c_i].append(time.time())
                    else:
                        for i in range(1, c_i + 4):
                            try:
                                last_points = globals()['pts%s' % i]
                                last_point = last_points[-1]
                                if (lower_threshold < (center[0] - last_point[0]) < upper_threshold) and (lower_threshold < (center[1] - last_point[1]) < upper_threshold):
                                    globals()['pts%s' % i].append(center)
                                    globals()['time%s' % c_i].append(time.time())
                                else:
                                    print("threshold not met")
                                    
                                if i == c_i + 3:
                                    print("end case")
                                
                            except Exception as e:
                                if i == c_i + 3:
                                    print("deleting prev track")
                                    globals()['pts%s' % c_i].clear()
                                    globals()['time%s' % c_i].clear()
                                    globals()['pts%s' % c_i].append(center)
                                    globals()['time%s' % c_i].append(time.time())
                                else:
                                    print("error: " + str(e) + " in loop " + str(i) +" for " +str(c_i))
                                
                except Exception as e:
                    print("adding point to track " + str(c_i))
                    globals()['pts%s' % c_i].append(center)
                    globals()['time%s' % c_i].append(time.time())
                
                try:
                    last_points = globals()['pts%s' % c_i]
                    last_point = last_points[-1]
                    
                    for i in np.arange(1, len(globals()['pts%s' % c_i])):
                        if people_count < c_i:
                            people_count = c_i
                            if lastobject == True:
                                client.loop_start()
                                print("people count: " + str(people_count))
                                while Connected != True:
                                    time.sleep(0.1)
                                client.publish("people", people_count)
                                client.loop_stop()
                                try:
                                    client.loop_start()
                                    total_dwell = 0
                                    for i in (1, c_i):
                                        dwell = globals()['time%s' % c_i]
                                        dwell_time = int(dwell[-1] - dwell[0])
                                        total_dwell+=dwell_time
                                    avgdwell = int(total_dwell / c_i)
                                    #print("average dwell time: " + str(avgdwell))
                                    while Connected != True:
                                        time.sleep(0.1)
                                    client.publish("dwell", avgdwell)
                                    client.loop_stop()
                                    with open("log.txt", "a") as pts_log:
                                        points = globals()['pts%s' % c_i]
                                        point = points[-1]
                                        pts_log.write(str(point)[1:-1]+"\n")
                                        #print(str(point)[1:-1])
                                except Exception as e:
                                    print(e)
                                    print("failed to get aggregates")
                                lastobject = False
                            else:
                                total_dwell = 0
                                for i in (1, c_i):
                                        client.loop_start()
                                        dwell = globals()['time%s' % c_i]
                                        dwell_time = int(dwell[-1] - dwell[0])
                                        total_dwell+=dwell_time
                                        avgdwell = int(total_dwell / c_i)
                                        print("average dwell time: " + str(avgdwell))
                                        while Connected != True:
                                            time.sleep(0.1)
                                        client.publish("dwell", avgdwell)
                                        client.loop_stop()
                                        with open("log.txt", "a") as pts_log:
                                            points = globals()['pts%s' % c_i]
                                            point = points[-1]
                                            pts_log.write(str(point)[1:-1]+"\n")
                                            #print(str(point)[1:-1]
                        # if either of the tracked points are None, ignore
                        # them
                        if globals()['pts%s' % c_i][i - 1] is None or globals()['pts%s' % c_i][i] is None:
                            continue

                        # otherwise, compute the thickness of the line and
                        # draw the connecting lines
                        thickness = int(1)
                        cv2.line(frame, globals()['pts%s' % c_i][i - 1], globals()['pts%s' % c_i][i], (0, 0, 255), thickness)
                        if i == c_i:
                            dwell = globals()['time%s' % c_i]
                            dwell_time = dwell[-1] - dwell[0]
                            cv2.putText(frame, str(c_i), globals()['pts%s' % c_i][i], cv2.FONT_HERSHEY_SIMPLEX,0.8, (255, 255, 255), 2)
                            cv2.putText(frame, str(int(dwell_time)) + "s" , (globals()['pts%s' % c_i][i][0] + 20, globals()['pts%s' % c_i][i][1] + 20), cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 255, 255), 1)
                            #cv2.putText(frame, str(time.time()) + "s" , (globals()['pts%s' % c_i][i][0] + 30, globals()['pts%s' % c_i][i][1] + 20), cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 255, 255), 1)
                except Exception as e:
                    print(str(e) + ", no points, no line!")
                    
    cv2.imshow('image',frame)
    print(" ===== ===== ===== ")
    #out.write(frame)
    cv2.waitKey(1)

cv2.destroyAllWindows()
out.release()
cap.release()
