#!/usr/bin/env python
import random
import rospy
import smach
import smach_ros
import time
from assignment1 import Empty
from std_msgs.msg import String
from armor_api.armor_client import ArmorClient

battery_callback(msg):
    return msg.data
    
def admitted_destinations(strings_list):
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


class WaitForMapState(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['map_loaded'])

    def execute(self, userdata):
        rospy.loginfo('Waiting for map to be loaded...')
        rospy.wait_for_service('initmap_service')
        service_client = rospy.ServiceProxy('initmap_service', Empty)
        response = service_client()
        

        #where i can go?
        #move to random corridor
        rospy.set_param('ImInE', False)
        return 'map_loaded'

class MoveInCorridorsState(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['battery_low', 'urgent_room_reached', 'interrupted'])

    def execute(self, userdata):        
        rospy.loginfo('Moving in corridors...')
        
        armcli = ArmorClient("example", "ontoRef")
        canreach = armcli.call('QUERY','OBJECTPROP','IND',['canReach', 'Robot1'])
        find_substrings (canreach.queried_objects)    

        
        
        
        
        # Implement your code to move in corridors here
        # Check if the battery is low or an urgent room has been reached
        battery_low = False # replace with your code
        urgent_room_reached = False # replace with your code

        if battery_low:
            return 'battery_low'
        elif urgent_room_reached:
            return 'urgent_room_reached'
        else:
            return 'interrupted'

class VisitRoomState(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['room_visited', 'battery_low'])

    def execute(self, userdata):
        rospy.loginfo('Visiting room...')
        # Implement your code to visit the room here
        # Check if the battery is low
        battery_low = False # replace with your code

        if battery_low:
            return 'battery_low'
        else:
            return 'room_visited'

class ChargingState(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['battery_full'])

    def execute(self, userdata):
        rospy.loginfo('Moving to charging station...')
        #movetoE
        #if you are in corridor go to EOFError
        #if you are in a 
        
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
    rospy.init_node('smach_example')

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
    
    sis = smach_ros.IntrospectionServer('smach_example', sm, '/SM_ROOT')
    sis.start()

    # Execute the SMACH state machine
    outcome = sm.execute()

    # Stop the introspection server
    sis.stop()

    # Print the outcome of the SMACH state machine
    rospy.loginfo('Mission completed with outcome: %s' % outcome)

if __name__ == '__main__':
    main()