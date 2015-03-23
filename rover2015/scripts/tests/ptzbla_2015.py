#!/usr/bin/env python
import roslib
roslib.load_manifest('rover2015')
import os
import sys
import time
import re
from subprocess import call
import rospy
import numpy as np
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge, CvBridgeError

# opencv2 and cv compatible
try:
    import cv2.cv
    var1 = [v for v in dir(cv2.cv) if v.startswith('CV_')]
    var2 = [v[3:] for v in var1]
    for v1, v2 in zip(var1, var2):
        setattr(cv2, v2, getattr(cv2.cv, v1))
except Exception:
    pass

stream=os.popen("ls /dev/video*")
devices = stream.read().split()

camList = [re.findall(r'\d+',dev)[0] for dev in devices]
print "Available Video Devices:\n"
print camList

cam_no=[int(c) for c in camList]

height=str(480)
width=str(640)
fps=str(30)
cam=str(0)

capture=None
capture1=None
sub=None
frame=None
prev_cam=str(0)
check_fps_set=0

def bindCamera(cam, cap):
    # release camera resource
    if cap is not None and cap.isOpened():
        cap.release()
        cap = None
    # return None if cam is None
    if cam is None:
        return None
    # bind camera
    cap = cv2.VideoCapture(cam_no[int(cam)])
    while not cap:
        time.sleep(0.05)
        cap = cv2.VideoCapture(cam_no[int(cam)])
    return cap
    
def callback_compressedImage(ros_data):
    global sub
    global frame
    global cam
    if cam==str(4):
        bridge = CvBridge()
        frame = bridge.imgmsg_to_cv2(ros_data.data, 'bgr8')

def callback_configCam(setup_data):
    global cam_no
    string=str(setup_data.data)
    print "configCam:" + string
    
    cam_no = [int(c) for c in string.split(',')]
    
def callback_config(data):
    global height
    global width
    global capture
    global capture1
    global fps
    global cam
    global camList
    global check_fps_set
    global sub
    global cam_no
    string=str(data.data)
    print 'config:', string
    b=string.split(',')
    prev_cam=cam
    cam=str(b[0])
    fps=str(b[1])
    height=str(b[2])
    width=str(b[3])
    
    if cam in camList:
        capture = bindCamera(cam, capture)
        capture1 = bindCamera(None, capture1)
        
    if prev_cam==str(4):
        sub.unregister()
    if cam==str(4):
        capture=None
        capture1=None
        sub=rospy.Subscriber('/image_raw/compressed', CompressedImage, callback_compressedImage, queue_size=1)
        check_fps_set=1
        return
    if cam==str(5):
        capture=None
        capture1=None
        capture=bindCamera(cam_no[0], capture)
        capture1=bindCamera(cam_no[1], capture1)
        check_fps_set=1
        return

    check_fps_set=1
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))
 
def talker():
    global height
    global width
    global fps
    global check_fps_set
    global capture
    global capture1
    global cam
    global sub
    global frame
    
    capture = bindCamera(cam, capture)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))
    bridge=CvBridge()
    pub = rospy.Publisher('chatter', Image, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    
    rospy.Subscriber("config", String, callback_config)
    rospy.Subscriber("configCam", String, callback_configCam)
    #rospy.Subscriber('/image_raw/compressed', CompressedImage, callback1,queue_size=1)
    r = rospy.Rate(int(fps))
    
    frames=0
    start_time=0
    check=0

    if cam==str(4):
        sub=rospy.Subscriber('/image_raw/compressed', CompressedImage, callback_compressedImage, queue_size=1)
    while not rospy.is_shutdown():
        try:
            if cam in camList:
                ret, frame = capture.read()
            if cam==str(5):
                ret, frame = capture.read()
                ret, frame1 = capture1.read()
                frame = np.hstack((frame, frame1))
            if check==0:
                check=1
                start_time=time.time()
            if check_fps_set==1:
                r = rospy.Rate(int(fps))
                print "fps: " + fps
                start_time=time.time()
                frames=0
                check_fps_set=0
            frames=frames+1
            if frames%10==0:
                curtime=time.time()
                diff=curtime-start_time
                fps_show=str(frames/diff)
                print 'fps_show:', fps_show
            pub.publish(bridge.cv2_to_imgmsg(frame, "bgr8"))
        except Exception:
            capture = bindCamera(cam, capture)
        r.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException: pass
