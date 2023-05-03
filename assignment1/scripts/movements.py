import rospy
import actionlib
from time import sleep
from assignment1.msg import PlanningAction, PlanningResult, PlanningGoal
from armor_api.armor_client import ArmorClient

def simulating_movements(goal):
    armcli = ArmorClient("example", "ontoRef")
    target_room = goal.target_room #usefull for second assignment
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
        armcli.call('ADD','OBJECTPROP','IND',['REPLACE', 'Robot1', 'C1', target_room]) 
        
        armcli.call('REASON','','',[''])
        rospy.loginfo('Motion completed :)')
        rospy.loginfo("Move action succeeded")
        server.set_succeeded(result)
    else:
        server.set_preempted(result)

if __name__ == "__main__":
    rospy.init_node("movements_server")
    
    
    server = actionlib.SimpleActionServer(
        "move_to_position",
        PlanningAction,
        simulating_movements,
        False
    )
    server.start()
    rospy.spin()
