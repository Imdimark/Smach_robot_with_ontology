#!/usr/bin/env python
import random
import rospy
import smach
import smach_ros
import time
from std_msgs.msg import String, Bool
from armor_api.armor_client import ArmorClient
import actionlib
from actionlib import SimpleActionClient
from assignment1.msg import PlanningAction, PlanningResult, PlanningGoal
from std_srvs.srv import Empty

"""
.. module:: Finite state machine
   :platform: Unix
   :synopsis: This module contains a state machine controlling the behaviour of a robot.
.. moduleauthor:: Giovanni Di Marco giovannidimarco06@gmail.com
"""

       
def extract_values(strings_list):
    """
    Function that extracts values from a list of strings.

    :param list strings_list: List of strings from which to extract values.
    :returns: List of substrings that match a specific pattern.
    :rtype: list
    """
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
    """
    Function that selects a random string from a list.

    :param list strings_list: List of strings to choose from.
    :param str character: Character that must be in the selected string.
    :returns: The selected string.
    :rtype: str
    """
    selected_string = None
    actual_position = rospy.get_param('ActualPosition')
    while selected_string is None or character not in selected_string:
        selected_string = random.choice(strings_list)
        
    return selected_string

def move_to_position_client(client, x, skip):
    """
    Function that sends a goal to a ROS action server.

    :param actionlib.SimpleActionClient client: The action client.
    :param str x: The goal to send to the action server.
    :param bool skip: Boolean to skip battery cancel.
    :returns: The result of the action.
    :rtype: PlanningResult
    """
    client.wait_for_server()
    goal = PlanningGoal()
    goal.target_room = x  # Ad esempio, posizione da raggiungere
    goal.skip_batterycancel = skip # this is a boolean, if true the robot will not cancel the goal if it is moving to the charging station
    client.send_goal(goal)
    
    client.wait_for_result()
    result = client.get_result()
    print ("result:", result)
    return result


class WaitForMapState(smach.State):
    """
    State that waits for a map to be loaded.

    :param None: No parameters are passed to this function.
    :returns: None
    """
    def __init__(self):
        smach.State.__init__(self, outcomes=['map_loaded'])
        self.service_client = rospy.ServiceProxy('initmap_service', Empty)

    def execute(self, userdata):
        rospy.loginfo('Waiting for map to be loaded...')
        rospy.wait_for_service('initmap_service')
        
        response = self.service_client()
        
        
        return 'map_loaded'

class MoveInCorridorsState(smach.State):
    """
    State that moves the robot in corridors.

    :param None: No parameters are passed to this function.
    :returns: None
    """
    def __init__(self):
        smach.State.__init__(self, outcomes=['battery_low', 'urgent_room_reached', 'no_urgent_available'], output_keys=['MoveInCorridorsState_output'])
        self.armcli = ArmorClient("example", "ontoRef")
        self.client = actionlib.SimpleActionClient("move_to_position", PlanningAction)
   
    def execute(self, userdata):      
        reachable_place_list_and_urgent = []
        #self.armcli.call('REASON','','',[''])
        canreach = self.armcli.call('QUERY','OBJECTPROP','IND',['canReach', 'Robot1'])
        

        reachable_place_list = extract_values (canreach.queried_objects)
        print ("can reach:", reachable_place_list)
        
        new__target_position = choose_randomly (reachable_place_list, "C") #C are all the corridors available <---------------------------
        result = move_to_position_client(self.client, new__target_position, False)
    
        isurgent_list_query =  self.armcli.call('QUERY','IND','CLASS',['URGENT'])
        isurgent_list = extract_values (isurgent_list_query.queried_objects)
        
        ############################################################################        
        canreach = self.armcli.call('QUERY','OBJECTPROP','IND',['canReach', 'Robot1'])
        reachable_place_list = extract_values (canreach.queried_objects)       
        reachable_place_list_and_urgent = list(set(reachable_place_list).intersection(isurgent_list))
        ###########################################################################
        
        if result.result:
            rospy.loginfo("Goal position reached")
            if reachable_place_list_and_urgent == []:
                rospy.loginfo("Goal position reached, no urgent rooms, continuing moving in corridors...")
                return 'no_urgent_available'
            else:
                rospy.loginfo("Goal position reached, urgent room found, moving to room...") ##the randomness will choose in the choose_randomly function
                userdata.MoveInCorridorsState_output = reachable_place_list_and_urgent ## giving to the next state the list of urgent and reachable rooms 
                return 'urgent_room_reached'
                
        else:
            rospy.loginfo("Goal was preempted or failed")
            return 'battery_low'
        

class VisitRoomState(smach.State):
    """
    State that manages the visit to a room.

    :param None: No parameters are passed to this function.
    :returns: None
    """
    def __init__(self):
        smach.State.__init__(self, outcomes=['room_visited', 'battery_low'], input_keys=['MoveInCorridorsState_output'])
        self.armcli = ArmorClient("example", "ontoRef")
        self.batterystate = rospy.Subscriber('BatteryState', Bool, self.battery_callback)
        self.client = actionlib.SimpleActionClient("move_to_position", PlanningAction)
    
    def battery_callback(self, msg):
        self.bs = msg.data
    
    def execute(self, userdata):
        rospy.loginfo('Visiting room...')     
        
        
        new__target_position = choose_randomly (userdata.MoveInCorridorsState_output, "R") #R are all the reachable room available <---------------
        
        result = move_to_position_client(self.client, new__target_position, False)

        if result.result:
            rospy.loginfo("Goal position reached, im in room")
            
        else:
            rospy.loginfo("Goal was preempted,going to charging station state")
            return 'battery_low'
        
        start_time = rospy.Time.now()  # ottieni il tempo corrente
        rate = rospy.Rate(10)  # imposta la frequenza di esecuzione del loop a 10 Hz
        
        
        rospy.loginfo('Ispetioning the room for 5 seconds...')
        while (rospy.Time.now() - start_time).to_sec() < rospy.get_param('RoomInspectionTime'):
            if not self.bs:
                return 'battery_low'
            rate.sleep()  # attendi il tempo necessario per mantenere la frequenza impostata

        
        rospy.loginfo('Room inspected, going back to corridor...')
        return 'room_visited'

class ChargingState(smach.State):
    """
    State that manages the charging of the robot.

    :param None: No parameters are passed to this function.
    :returns: None
    """
    def __init__(self):
        smach.State.__init__(self, outcomes=['battery_full'])
        self.armcli = ArmorClient("example", "ontoRef")
        self.client = actionlib.SimpleActionClient("move_to_position", PlanningAction)
        self.batterystate = rospy.Subscriber('BatteryState', Bool, self.battery_callback)
    
    def battery_callback(self, msg):
        self.bs = msg.data

    def execute(self, userdata):
        rospy.loginfo('Moving to charging station...')
        canreach = self.armcli.call('QUERY','OBJECTPROP','IND',['canReach', 'Robot1'])
        reachable_place_list = extract_values (canreach.queried_objects)
        new__target_position = choose_randomly (reachable_place_list, "C") #C are all the corridors available

        if "E" in reachable_place_list:
            rospy.loginfo('Moving to charging station...')
            new__target_position = "E"
            result = move_to_position_client(self.client, new__target_position,True)

        else:
            rospy.loginfo('Moving to corridor before going to charging station...')                   
            new__target_position = choose_randomly (reachable_place_list, "C") #C are all the corridors available
            result = move_to_position_client(self.client, new__target_position,True)
            rospy.loginfo('Moving to charging station...')
            new__target_position = "E"
            result = move_to_position_client(self.client, new__target_position,True)

        rospy.loginfo('Charging...')
        rospy.set_param('/IsChargingParam', True)
        
        
        while (self.bs == False):{
            time.sleep(1)
        }
        
        rospy.loginfo('...Charged')
        rospy.set_param('/IsChargingParam', False)
        return 'battery_full'

def main():
    """
    Main function.

    This function initializes the ROS node and creates and executes the state machine.

    :param None: No parameters are passed to this function.
    :returns: None
    """
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
                                            'no_urgent_available': 'MOVE_IN_CORRIDORS'})
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
