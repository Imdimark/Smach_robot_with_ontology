#!/usr/bin/env python
# license removed for brevity
import rospy
import random
from std_msgs.msg import Bool
import roslaunch 
#from assignment1 import Empty
from std_srvs.srv import Empty
from assignment1.msg import PlanningAction,PlanningActionResult,PlanningActionGoal

batteryduration=39


'''def InitMap():
    rospy.loginfo('Waiting for map to be loaded...')
    rospy.wait_for_service('initmap_service')
        
    service_client = rospy.ServiceProxy('initmap_service', Empty)
        
         
    response = service_client()
    #rospy.wait_for_message('initmap_service/complete', Empty)'''


def BatteryState():
    rospy.set_param('ImInE', True)
    pub = rospy.Publisher('BatteryState', Bool, queue_size=10)
    client = actionlib.SimpleActionClient("move_to_position", PlanningAction)
    client.wait_for_server()
    rate = rospy.Rate(1) # 1hz
    batterylevel = batteryduration
    while not rospy.is_shutdown():
        ImCharging = rospy.get_param('ImInE')

        
        if (not ImCharging) and batterylevel > 0: #discharging 
            batterylevel = batterylevel - 1
            if batterylevel < 7:
                rospy.loginfo("Battery is going too low")
            #batteryBool = True
            
        elif (not ImCharging) and batterylevel == 0: #Battery is empty
            batteryBool = False
            client.cancel_all_goals()
            rospy.loginfo("Battery is empty, preempting current goal, going to charge station")
        
        elif ImCharging and batterylevel <= batteryduration: #charging 
            batterylevel = batterylevel + 1
            batteryBool = True
	
        rospy.loginfo(batterylevel) #batteryBool
        pub.publish(batteryBool)
        rate.sleep()

if __name__ == '__main__':
    
    try:
        rospy.init_node('batterystatus', anonymous=True)
        #InitMap()
        BatteryState()
    except rospy.ROSInterruptException:
        pass

