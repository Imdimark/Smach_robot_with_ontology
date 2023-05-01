import rospy
import actionlib
from time import sleep


# move_server.py

import rospy
import actionlib
from time import sleep
from assignment1.msg import PlanningAction
def execute_cb(goal, server):
    target_position = goal.target_position

    success = True
    for _ in range(5):
        if server.is_preempt_requested():
            rospy.loginfo("Move action preempted")
            success = False
            break
        sleep(1)

    result = MoveToPositionResult()
    result.reached = success

    if success:
        rospy.loginfo("Move action succeeded")
        server.set_succeeded(result)
    else:
        server.set_preempted(result)

if __name__ == "__main__":
    rospy.init_node("move_server")
    server = actionlib.SimpleActionServer(
        "move_to_position",
        MoveToPositionAction,
        execute_cb=execute_cb,
        auto_start=False,
    )
    server.start()
    rospy.spin()
