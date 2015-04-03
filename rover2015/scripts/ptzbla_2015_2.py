#!/usr/bin/env python
import roslib
roslib.load_manifest('rover2015')
import rospy
import cv
import numpy as np
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

cam_no = [7,6,5,4]
List = [str(i) for i in cam_no]

height=str(640)
width=str(480)
fps=str(30)
r = None
cam="0"
capture=cv.CaptureFromCAM(int(List[0]))
capture1=None
sub=None
frame=None
prev_cam='0'

def callback(data):
    print "data: " + data.data
    global height
    global width
    global capture
    global capture1
    global fps
    global r
    global prev_cam
    global cam
    global sub
    global cam_no
    string=str(data.data)
    b=string.split(',')
    height=str(b[2])
    width=str(b[3])
    prev_cam=cam
    cam=str(b[0])
    
    # change FPS
    fps=str(b[1])
    r = rospy.Rate(int(fps))
    
    # change camera
    if cam in [str(i) for i in range(len(cam_no))]:
        capture=None
        capture1=None
        capture=cv.CaptureFromCAM(cam_no[0])
        
    if cam==str(5):
        capture=None
        capture1=None
        capture=cv.CaptureFromCAM(cam_no[0])
        capture1=cv.CaptureFromCAM(cam_no[1])
    
    # change width and height
    cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_WIDTH,int(width))
    cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_HEIGHT,int(height))
        
def talker():
    global height
    global width
    global fps
    global r
    global capture
    global capture1
    global cam

    cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_WIDTH,int(width))
    cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_HEIGHT,int(height))
    bridge=CvBridge()
    pub = rospy.Publisher('chatter', Image)
    rospy.init_node('talker', anonymous=True)
    
    rospy.Subscriber("config", String, callback)
    #rospy.Subscriber('/image_raw/compressed', CompressedImage, callback1,queue_size=1)
    r = rospy.Rate(int(fps))
    cv.QueryFrame(capture)
    frame=cv.QueryFrame(capture)
    while not rospy.is_shutdown():
        if cam!=str(4):
            frame=cv.QueryFrame(capture)
            frame = np.asarray(frame[:,:])
        if cam==str(5):
            frame=cv.QueryFrame(capture)
            frame1=cv.QueryFrame(capture1)
            img=np.asarray(frame[:,:])
            img1=np.asarray(frame1[:,:])
            both=np.hstack((img,img1))
            bitmap = cv.CreateImageHeader((both.shape[1], both.shape[0]), cv.IPL_DEPTH_8U, 3)
            cv.SetData(bitmap, both.tostring(), both.dtype.itemsize * 3 * both.shape[1])
            frame=bitmap

        pub.publish(bridge.cv2_to_imgmsg(frame, "bgr8"))
        r.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException: pass
