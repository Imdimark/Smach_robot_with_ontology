import rospy
import actionlib
from time import sleep
from assignment1.msg import PlanningAction,PlanningActionResult,PlanningActionGoal

def execute_cb(goal, server):
    target_room = goal.target_room
    success = True
    for _ in range(5):
        if server.is_preempt_requested():
            rospy.loginfo("Move action preempted")
            success = False
            break
        sleep(0.5)

    result = PlanningActionResult()
    result.result = success

    if success:
        rospy.loginfo("Move action succeeded")
        server.set_succeeded(result)
    else:
        server.set_preempted(result)

if __name__ == "__main__":
    rospy.init_node("movements_server")
    server = actionlib.SimpleActionServer(
        "move_to_position",
        PlanningAction,
        execute_cb=execute_cb,
        auto_start=False,
    )
    server.start()
    rospy.spin()
