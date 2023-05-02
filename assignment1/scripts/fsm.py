#!/usr/bin/env python
import random
import rospy
import smach
import smach_ros
import time
from std_msgs.msg import String
from armor_api.armor_client import ArmorClient
from actionlib import SimpleActionClient
from assignment1.msg import PlanningAction,PlanningActionResult,PlanningActionGoal
from std_srvs.srv import Empty

def urgent_room(probability):
    return random.random() < probability


def battery_callback(msg):
    return msg.data
    
def extract_values(strings_list):
    matched_substrings = []
    for string in strings_list:
        start_index = string.find("#")
        end_index = string.find(">")
        while start_index != -1 and end_index != -1:
            substring = string[start_index + 1 : end_index]
            matched_substrings.append(substring)
            start_index = string.find("#", end_index)
            end_index = string.find(">", start_index)
    return matched_substrings

def choose_randomly(strings_list, character):
    selected_string = None
    while selected_string is None or character not in selected_string:
        selected_string = random.choice(strings_list)
    return selected_string

def move_to_position_client(x):
    client = actionlib.SimpleActionClient("move_to_position", MoveToPositionAction)
    client.wait_for_server()

    goal = MoveToPositionGoal()
    goal.target_room = x  # Ad esempio, posizione da raggiungere
    client.send_goal(goal)
    #armcli.call('ADD','OBJECTPROP','IND',['REPLACE', 'Robot1', 'C1', new__target_position]) 
    rospy.loginfo('Moving...')
    #armcli.call('REASON','','',[''])
    #time.sleep(5) #simulating the movment of the robot
    #rospy.loginfo('Moving in corridors...')

    client.wait_for_result()
    result = client.get_result()
    return result


class WaitForMapState(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['map_loaded'])

    def execute(self, userdata):
        rospy.loginfo('Waiting for map to be loaded...')
        rospy.wait_for_service('initmap_service')
        service_client = rospy.ServiceProxy('initmap_service', Empty)
        response = service_client()
        rospy.set_param('ImInE', False)
        return 'map_loaded'

class MoveInCorridorsState(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['battery_low', 'urgent_room_reached', 'interrupted'])

    def execute(self, userdata):        
        
        armcli = ArmorClient("example", "ontoRef")
        canreach = armcli.call('QUERY','OBJECTPROP','IND',['canReach', 'Robot1'])
        reachable_place_list = extract_values (canreach.queried_objects)
        new__target_position = choose_randomly (reachable_place_list, "C") #C are all the corridors available
        result = move_to_position_client(new__target_position)
        there_is_urgent_room = urgent_room(0.2)


        if result.result:
            rospy.loginfo("Goal position reached")
            if not there_is_urgent_room:
                rospy.loginfo("Goal position reached, no urgent rooms, continuing moving in corridors...")
                return 'interrupted'
            else:
                rospy.loginfo("Goal position reached, urgent room found, moving to room...") ##the randomness will choose in the choose_randomly function
                return 'urgent_room_reached'
        else:
            rospy.loginfo("Goal was preempted or failed")
            return 'battery_low'
        

class VisitRoomState(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['room_visited', 'battery_low'])

    def execute(self, userdata):
        rospy.loginfo('Visiting room...')
        
        armcli = ArmorClient("example", "ontoRef")
        canreach = armcli.call('QUERY','OBJECTPROP','IND',['canReach', 'Robot1'])
        reachable_place_list = extract_values (canreach.queried_objects)
        new__target_position = choose_randomly (reachable_place_list, "R") #R are all the reachable room available
        
        result = move_to_position_client(new__target_position)

        if result.result:
            rospy.loginfo("Goal position reached, im in room")
            
        else:
            rospy.loginfo("Goal was preempted,going to charging station state")
            return 'battery_low'
        
        start_time = rospy.Time.now()  # ottieni il tempo corrente
        rate = rospy.Rate(10)  # imposta la frequenza di esecuzione del loop a 10 Hz
        batterystate = rospy.Subscriber('BatteryState', Bool, battery_callback)
        
        rospy.loginfo('Ispetioning the room for 5 seconds...')
        while (rospy.Time.now() - start_time).to_sec() < 5.0:
            if not batterystate:
                return 'battery_low'
            rate.sleep()  # attendi il tempo necessario per mantenere la frequenza impostata

        rospy.loginfo('Going back to corridors...')
        canreach = armcli.call('QUERY','OBJECTPROP','IND',['canReach', 'Robot1'])
        reachable_place_list = extract_values (canreach.queried_objects)
        new__target_position = choose_randomly (reachable_place_list, "C") #C are all the corridors available
        
        result = move_to_position_client(new__target_position)

        if result.result:
            rospy.loginfo("Goal position reached, im in Corridor again")
            return 'room_visited'
            
        else:
            rospy.loginfo("Goal was preempted,going to charging station state")
            return 'battery_low'



class ChargingState(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['battery_full'])

    def execute(self, userdata):
        rospy.loginfo('Moving to charging station...')
        armcli = ArmorClient("example", "ontoRef")
        canreach = armcli.call('QUERY','OBJECTPROP','IND',['canReach', 'Robot1'])
        reachable_place_list = extract_values (canreach.queried_objects)
        new__target_position = choose_randomly (reachable_place_list, "C") #C are all the corridors available
               

        if "E" in reachable_place_list:
            rospy.loginfo('Moving to charging station...')
            new__target_position = "E"
            result = move_to_position_client(new__target_position)

        else:
            rospy.loginfo('Moving to corridor before going to charging station...')                   
            new__target_position = choose_randomly (reachable_place_list, "C") #C are all the corridors available
            result = move_to_position_client(new__target_position)
            rospy.loginfo('Moving to charging station...')
            new__target_position = "E"
            result = move_to_position_client(new__target_position)

        rospy.loginfo('Charging...')
        rospy.set_param('ImInE', True)
        batterystate = rospy.Subscriber('BatteryState', Bool, battery_callback)
        while (not batterystate):{
            time.sleep(1)
        }
        
        rospy.loginfo('...Charged')
        rospy.set_param('ImInE', False)
        return 'battery_full'

def main():
    rospy.init_node('fsm_node')

    # Create the top-level SMACH state machine
    sm = smach.StateMachine(outcomes=['mission_completed'])

    # Open the container
    with sm:
        # Add states to the SMACH state machine
        smach.StateMachine.add('WAIT_FOR_MAP', WaitForMapState(),
                               transitions={'map_loaded': 'MOVE_IN_CORRIDORS'})
        smach.StateMachine.add('MOVE_IN_CORRIDORS', MoveInCorridorsState(),
                               transitions={'battery_low': 'CHARGING',
                                            'urgent_room_reached': 'VISIT_ROOM',
                                            'interrupted': 'mission_completed'})
        smach.StateMachine.add('VISIT_ROOM', VisitRoomState(),
                               transitions={'room_visited': 'MOVE_IN_CORRIDORS',
                                            'battery_low': 'CHARGING'})
        smach.StateMachine.add('CHARGING', ChargingState(),
                               transitions={'battery_full': 'MOVE_IN_CORRIDORS'})

    # Create and start the introspection server to visualize the SMACH state machine
    
    sis = smach_ros.IntrospectionServer('fsm', sm, '/SM_ROOT')
    sis.start()

    # Execute the SMACH state machine
    outcome = sm.execute()

    # Stop the introspection server
    sis.stop()

    # Print the outcome of the SMACH state machine
    rospy.loginfo('Mission completed with outcome: %s' % outcome)

if __name__ == '__main__':
    main()