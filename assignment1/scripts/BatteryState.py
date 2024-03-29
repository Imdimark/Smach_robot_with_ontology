#!/usr/bin/env python
"""
.. module:: BatteryStatusManagement
   :platform: Unix
   :synopsis: Module to manage the battery status of a robot using the Robot Operating System (ROS).
.. moduleauthor:: Giovanni Di Marco giovannidimarco06@gmail.com
"""

import rospy
import random
from std_msgs.msg import Bool
import roslaunch 
from std_srvs.srv import Empty
from assignment1.msg import PlanningAction,PlanningResult,PlanningGoal
import actionlib
batteryduration=40

def BatteryState():
    """
    Function to handle battery status.

    This function continually checks whether the robot's battery is charging or discharging, 
    based on the state of the parameter 'ImCharging'. It also publishes through the topic "BatteryState" the battery status at regular intervals.

    :param None: No parameters are passed to this function.
    :type None: None
    :returns: None
    """
	
    pub = rospy.Publisher('BatteryState', Bool, queue_size=10)
    client = actionlib.SimpleActionClient("move_to_position", PlanningAction)
    client.wait_for_server()
    rate = rospy.Rate(0.3) # 0.3 hz
    batterylevel = batteryduration
    batteryBool = True
    while not rospy.is_shutdown():
        ImCharging = rospy.get_param('IsChargingParam')
        #ImCharging = True
        if (not ImCharging) and batterylevel > 0: #discharging 
            batterylevel = batterylevel - 1
            if batterylevel < 7:
                rospy.loginfo("Battery is going too low")
            #batteryBool = True
            
        elif (not ImCharging) and batterylevel == 0: #Battery is empty
            batteryBool = False
            client.cancel_all_goals()
            rospy.loginfo("Battery is empty, preempting current goal, going to charge station")
        
        elif ImCharging and (batterylevel <= batteryduration): #charging 
            if batterylevel == batteryduration:
                rospy.loginfo("Battery is full")
                batteryBool = True
            else:
                batterylevel = batterylevel + 1
                rospy.loginfo("Charging")
	
        rospy.loginfo("Battery level:" + str(batterylevel)) #batteryBool
        pub.publish(batteryBool)
        rate.sleep()

if __name__ == '__main__':
    """
    Main function.

    This function initializes the ROS node and calls the BatteryState function to manage the battery status and publish it .

    :param None: No parameters are passed to this function.
    :type None: None
    :returns: None
    """    
    try:
        rospy.init_node('batterystatus', anonymous=True)#, anonymous=True
        BatteryState()
    except rospy.ROSInterruptException:
        pass


