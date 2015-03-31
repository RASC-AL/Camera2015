#!/usr/bin/env python
import roslib
roslib.load_manifest('rover2015')
import os
import rospy
import numpy as np
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
#from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge, CvBridgeError
import warnings

# opencv2 and cv compatible
try:
    import cv2.cv
    var1 = [v for v in dir(cv2.cv) if v.startswith('CV_')]
    var2 = [v[3:] for v in var1]
    for v1, v2 in zip(var1, var2):
        setattr(cv2, v2, getattr(cv2.cv, v1))
except Exception:
    pass

def checkcamList(camList):
    stream=os.popen("ls /dev/video*")
    devices = stream.read().split()
    for i in camList:
        if '/dev/video' + str(i) not in devices:
            warnings.warn('/dev/video' + str(i) + ' does not exits!')
            
# see my-webcam.rules for cameras mapping
# 0->video7, 1->video6, ...
camList = [7,6,5,4]
# camList = [0,1,2,3]
checkcamList(camList)

#caps = [cv2.VideoCapture(i) for i in camList]
cam = 0
fps = 30
cap = cv2.VideoCapture(camList[cam])
cap1 = cv2.VideoCapture(camList[1])

def callback_config(msg):
    global cam
    global cap
    global cap1
    s = str(msg.data).split(',')
    print s
    cam = int(s[0])
    if cam < len(camList):
        cap.open(camList[cam])
    if cam == 5:
        cap.open(camList[0])
        cap1.open(camList[1])
 
def talker():

    bridge=CvBridge()
    pub = rospy.Publisher('chatter', Image, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    
    rospy.Subscriber("config", String, callback_config)
    r = rospy.Rate(fps)
    
    while not rospy.is_shutdown():
        try:
            if cam in range(len(camList)):
                ret, frame = cap.read()
            if cam == 5:
                ret, frame = cap.read()
                ret, frame1 = cap1.read()
                if frame1 is None:
                    frame1 = frame # for debug with only one camera
                frame = np.hstack((frame, frame1))
            pub.publish(bridge.cv2_to_imgmsg(frame, "bgr8"))
        except Exception:
            pass
        r.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException: pass
