#!/usr/bin/env python
# license removed for brevity
import rospy
import random
from std_msgs.msg import Bool


batteryduration=39

def BatteryState():
    #rospy.set_param('ImInE', True)
    pub = rospy.Publisher('BatteryState', Bool, queue_size=10)
    rospy.init_node('batterystatus', anonymous=True)
    rate = rospy.Rate(1) # 1hz
    batterylevel = batteryduration
    while not rospy.is_shutdown():
        ImCharging = rospy.get_param('ImInE')

        
        if (not ImCharging) and batterylevel > 0: #discharging 
            batterylevel = batterylevel - 1
            #batteryBool = True
        
        elif (not ImCharging) and batterylevel == 0: #Battery is empty
            batteryBool = False
        
        elif ImCharging and batterylevel <= batteryduration: #charging 
            batterylevel = batterylevel + 1
            batteryBool = True
	
        rospy.loginfo(batterylevel) #batteryBool
        pub.publish(batteryBool)
        rate.sleep()

if __name__ == '__main__':
    
    try:
        BatteryState()
    except rospy.ROSInterruptException:
        pass

