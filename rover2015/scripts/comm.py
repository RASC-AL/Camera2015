#!/usr/bin/env python
# Software License Agreement (BSD License)

import rospy
from std_msgs.msg import String
import os

from conf import COMM_FILE

cam = 0

def talker():
    global cam
    
    pub = rospy.Publisher('config', String, queue_size=10)
    rospy.init_node('talker_config', anonymous=True)
    r = rospy.Rate(1) # 10hz
    
    print os.getcwd()
    
    while not rospy.is_shutdown():
        if os.path.exists(COMM_FILE):
            with open(COMM_FILE) as f:
                temp_cam = int(f.read())
                if temp_cam != cam:
                    cam = temp_cam
                    pub.publish('%d,%d,%d,%d' % (cam,15,640,480))
        r.sleep()
        
if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException: pass
