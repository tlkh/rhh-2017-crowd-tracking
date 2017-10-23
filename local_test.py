import numpy as np
import cv2
import time
from collections import deque

cv2.setUseOptimized(True)
this = sys.modules[__name__]

cap = cv2.VideoCapture('opencv_test1.mov')
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))


# take first frame of the video

# Setup the termination criteria, either 10 iteration or move by atleast 1 pt

# define the lower and upper boundaries of the "colour"
# ball in the HSV color space
colourLower = (0, 0, 0)
colourUpper = (255, 80, 35)
 
# initialize the list of tracked points, the frame counter,
# and the coordinate deltas

counter = 0
newframe = False
firstCap = True

while(cap.isOpened()):
    ret ,frame = cap.read()
    if ret == True:
        
        newframe = True
        # resize the frame, blur it, and convert it to the HSV
        # color space
        #frame = imutils.resize(frame, width=320)
        frame = cv2.pyrDown(frame)
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
                        globals()['pts%s' % c_i] = deque(maxlen=8)
                        globals()['time%s' % c_i] = deque(maxlen=8)

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
                                    print("people count: " + str(people_count))
                                    try:
                                        total_dwell = 0
                                        for i in (1, c_i):
                                            dwell = globals()['time%s' % c_i]
                                            dwell_time = int(dwell[-1] - dwell[0])
                                            total_dwell+=dwell_time
                                        avgdwell = int(total_dwell / c_i)
                                        print("average dwell time: " + str(avgdwell))
                                        with open("log.txt", "a") as pts_log:
                                            points = globals()['pts%s' % c_i]
                                            point = points[-1]
                                            pts_log.write(str(point)[1:-1]+"\n")
                                            print("str(point)[1:-1]")
                                    except Exception as e:
                                        print(e)
                                        print("failed to get aggregates")
                                    lastobject = False
                                else:
                                    total_dwell = 0
                                    for i in (1, c_i):
                                            dwell = globals()['time%s' % c_i]
                                            dwell_time = int(dwell[-1] - dwell[0])
                                            total_dwell+=dwell_time
                                            avgdwell = int(total_dwell / c_i)
                                            print("average dwell time: " + str(avgdwell))
                                            with open("log.txt", "a") as pts_log:
                                                points = globals()['pts%s' % c_i]
                                                point = points[-1]
                                                pts_log.write(str(point)[1:-1]+"\n")
                                                print("str(point)[1:-1]")
                            # if either of the tracked points are None, ignore
                            # them
                            if globals()['pts%s' % c_i][i - 1] is None or globals()['pts%s' % c_i][i] is None:
                                continue

                            # otherwise, compute the thickness of the line and
                            # draw the connecting lines

                            # otherwise, compute the thickness of the line and
                            # draw the connecting lines
                            thickness = int(1)
                            cv2.line(frame, globals()['pts%s' % c_i][i - 1], globals()['pts%s' % c_i][i], (0, 0, 255), thickness)
                            if i == c_i:
                                dwell = globals()['time%s' % c_i]
                                dwell_time = dwell[-1] - dwell[0]
                                cv2.putText(frame, str(c_i), globals()['pts%s' % c_i][i], cv2.FONT_HERSHEY_SIMPLEX,0.8, (255, 255, 255), 2)
                                cv2.putText(frame, str(int(dwell_time)) + "s" , (globals()['pts%s' % c_i][i][0] + 20, globals()['pts%s' % c_i][i][1] + 20), cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 255, 255), 1)
                            
                    except Exception as e:
                        print(str(e) + ", no points, no line!")
                        
        cv2.imshow('image',frame)
        print(" ===== ===== ===== ")
        #out.write(frame)
        cv2.waitKey(1)

cv2.destroyAllWindows()
out.release()
cap.release()
