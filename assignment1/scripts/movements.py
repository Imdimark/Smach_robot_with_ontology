import rospy
import actionlib
from time import sleep
from assignment1.msg import PlanningAction, PlanningResult, PlanningGoal
from armor_api.armor_client import ArmorClient

def simulating_movements(goal):
    armcli = ArmorClient("example", "ontoRef")
    target_room = goal.target_room #usefull for second assignment
    print ("Target room" + target_room)
    success = True
    rospy.loginfo('Moving...')
    for _ in range(5):
        if server.is_preempt_requested():
            rospy.loginfo("Moving action preempted")
            success = False
            break
        
        sleep(0.5)

    result = PlanningResult()
    result.result = success

    if success:
        actual_position = rospy.get_param('ActualPosition')
        armcli.call('REPLACE','OBJECTPROP','IND',['isIn', 'Robot1', actual_position, target_room]) 
        print (actual_position, target_room)
        armcli.call('REASON','','',[''])
        rospy.set_param('ActualPosition', target_room)
        server.set_succeeded(result)
        rospy.loginfo("Move action succeeded, now robot is in room %s", target_room)
    else:
        server.set_preempted(result)
    

if __name__ == "__main__":
    rospy.init_node("movements_server")
    print ("loop main spin")
    
    server = actionlib.SimpleActionServer(
        "move_to_position",
        PlanningAction,
        simulating_movements,
        False
    )
    server.start()
    rospy.spin()
