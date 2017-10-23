import time
import cv2
import numpy as np
from camera import PiVideoStream
from collections import deque
import imutils
import sys

cv2.setUseOptimized(True)
this = sys.modules[__name__]


from flask import Flask, render_template, Response

app = Flask(__name__)

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def gen():
    # define the lower and upper boundaries of the "colour"
    # ball in the HSV color space
    colourLower = (0, 0, 0)
    colourUpper = (255, 255, 255)
     
    newframe = False
    firstCap = True
    while True:
        time.sleep(1/30)
        frame = camera.read()
        newframe = True
        # resize the frame, blur it, and convert it to the HSV
        # color space
        frame = imutils.resize(frame, width=320)
        blur = cv2.GaussianBlur(frame,(11,11),0)
        # hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

        if firstCap == True:
            print("first capture")
            backSubtractor = BackGroundSubtractor(0.001,frame)
            firstCap = False
            
        else:
            print("not the first capture")
            # get the foreground
            mask = backSubtractor.getForeground(frame)
     
            # construct a mask for the color, then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask
            
            #mask = mask.astype('uint8')
            #mask = np.uint8(mask)
            mask = cv2.inRange(mask, colourLower, colourUpper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            
         
            # find contours in the mask and initialize the current
            # (x, y) center of the ball
            cnts = cv2.findContours(mask, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2]
            center = None

            # only proceed if at least one contour was found
            cv2.drawContours(frame, cnts, -1, (255,0,0), 1)
            cv2.imwrite("mask.jpg", mask)
            
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            #c = max(cnts, key=cv2.contourArea)
            c_i = 0
            for c in cnts:
                if newframe == True :
                    c_i = 0
                    
                    newframe = False
                else:
                    c_i+=1
                    
                try:
                    print(globals()['pts%s' % c_i])
                except:
                    globals()['pts%s' % c_i] = deque(maxlen=16)
                    print("created variable pts" + str(c_i))

                cv2.drawContours(frame, cnts, c_i, (0,255,), 2)
                
                ((x, y), radius) = cv2.minEnclosingCircle(c)

                if (radius < 30) or (radius > 125):
                    print("rejected circle")
                else:
                    M = cv2.moments(c)
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    
                    # draw the circle and centroid on the frame,
                    # then update the list of tracked points
                    cv2.circle(frame, (int(x), int(y)), int(radius),
                            (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
                    globals()['pts%s' % c_i].appendleft(center)
                
                # loop over the set of tracked points
                for i in np.arange(1, len(globals()['pts%s' % c_i])):
                    # if either of the tracked points are None, ignore
                    # them
                    if globals()['pts%s' % c_i][i - 1] is None or globals()['pts%s' % c_i][i] is None:
                        continue

                    # otherwise, compute the thickness of the line and
                    # draw the connecting lines
                    thickness = int(np.sqrt(32 / float(i + 1)) * 2.5)
                    cv2.line(frame, globals()['pts%s' % c_i][i - 1], globals()['pts%s' % c_i][i], (0, 0, 255), thickness)
     
        # show the frame to our screen and increment the frame counter
        try:
            cv2.imwrite("stream.jpg", frame)
            image = open( "stream.jpg", 'rb').read()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
        except:
            print("no image")


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
        print("new stream")
        camera = PiVideoStream().start()
        time.sleep(0.5)
        print("camera ready")
        app.run(host='0.0.0.0', debug=True, use_reloader=False)
