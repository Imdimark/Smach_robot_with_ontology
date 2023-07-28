# Surveillance_robot

## Index of contents:
1. [Introduction](#introduction)
2. [Behaviour](#video)
3. [Software architecture](#soft)
4. [Installation and running procedure](#installation)
5. [Working hypothesis and environment](#hyp)
6. [Authors and contacts](#contacts)




## Introduction <a name="introduction"></a>
The project at hand focuses on the development and implementation of a surveillance robot, engineered to operate within an indoor environment. The environment consists of a 2D layout with four rooms and three corridors. The robot simulates its movements wasting time For an initial starting point, the robot is placed in a specific location referred to as 'E'.

<img src="https://github.com/Imdimark/EXPROLAB_Assignment1/assets/78663960/471cb60b-42c2-490f-9482-4c0e266a9d8f" width="40%" height="40%">

The development of this package primarily leverages two other packages: 

  1. [SMACH](http://wiki.ros.org/smach) for implementing and managing the finite state machine
  2. [ARMOR](http://wiki.ros.org/smach) in order to load, query and modify multiple ontologies and requires very little knowledge of OWL APIs and Java.




## Behaviour <a name="video"></a>
The operational structure of the robot is based on a topological map, which it constructs using incoming data about the connections between various rooms, corridors, and doorways. This information aids the robot in maneuvering around its environment and effectively fulfilling its surveillance duties.
The robot's actions follow an endless cycle: it moves to a new location, waits for a while, and then moves again. This process continues until the robot's energy levels run low, at which point it returns to location 'E' for a recharge before resuming its routine.
When the robot's battery is not low, it navigates through the environment with a specific policy in mind. It's programmed to stay primarily in the corridors, keeping a closer eye on them. However, if a nearby room hasn't been inspected for a while, the robot will deviate from its path to check the room, ensuring complete and thorough surveillance.

https://github.com/Imdimark/EXPROLAB_Assignment1/assets/78663960/47b87029-80bd-4c74-83d3-069cad416995

This video shows how the state machine works and goes through all the states. The window in the middle represents graphically how the smach machine works and which is the actual state. The other four windows, made by gnome terminals represent the four nodes that are running:

- **state of the battery** that is going up or down depending if it is discharging or charging (different state machine states)
- **movements** that shows the state of the movements like where the robot is, where the robot chan goes, and if the movements have been done
- **ontology** this node is in charge to contact the ARMOR service the ontology and initialize the map and the visited time of the rooms (useful for the urgency threshold), the windows show up when the process is done and the fsm can proceed to the next state.
- **FSM** is the core of the system, this window shows up the changing of the states and some info. To better understand is suggested to follow state changes throughout the smach_viewer. 


## Software architecture <a name="soft"></a>
### software components:
#### InitMapNode node
This node provides a ROS service named 'initmap_service', which is used to initialize a topological map used for robot navigation. The external communications of this component are mainly handled through ROS:
- initmap_service a service called by the fsm node at the beginning of the finite state machine.
- ActualPosition parameter used to set the knowledge of the actual position, this parameter is used by the movements node to have the knowledge about the starting position and update the onology with the appropriate query. In this specific node, it initializes the starting position in corridor "E".
- armor_interface_srv is the service, client-side, that interacts with the armor server for  load, query, and modify the ontology

#### batterystatus node
The node 'batterystatus' manages the battery status of a robot. 
External communications: 
- BatteryState topic published by this node to monitor the battery status, 
- IsChargingParam ROS parameter, this node gets this parameter at every cycle iteration to understand if the robot is in corridor "E" at the charging station. This parameter is useful to see if the robot is currently charging.
 - move_to_position is a simpleactionclient used to cancel the moving (simulated by wasting time) when the battery is empty, in order to be able to receive the new one of moving in the charging station.
#### movements_server node
It is designed to simulate the movements of a robot using ROS and the Armor ontology and wasting time.
External communications:
- move_to_position server-side service, the server listens on the 'move_to_position' action for PlanningAction goals. The goal message includes the target room and a flag indicating whether to skip battery checks. 
- MovingDurationParam parameter to determine how long to "sleep" to simulate movement.
- ActualPosition parameter to track and update the robot's current position.
- armor_interface_srv is the service, client-side, that interacts with the armor server for  load, query, and modify the ontology
#### fsm_node node
The FSM consists of four states, each represented by a smach.State class. This program makes the robot move and behave according to its battery level and the rooms it should visit.
External communications:
- BatteryState topic subscribed to monitor the robot's battery level
- initmap_service service, clientside, to call the creation of the ontology
- move_to_position SimpleActionClient which is likely responsible for controlling the robot's movements through the PlanningAction action
### State Viewpoint
The following schema represents the possible states and when transition could happen 

<img src="https://github.com/Imdimark/EXPROLAB_Assignment1/assets/78663960/d8306a3a-8e4d-4c79-a1b3-f12376af0b95" width="60%" height="60%">

### Nodes
The following schema is a rqt_graph generated starting from the running ros nodes and represents their architecture and how the nodes communicate with each other.

<img src="https://github.com/Imdimark/EXPROLAB_Assignment1/assets/78663960/c9032477-4bab-49e4-8fcd-098970b08404" width="60%" height="60%">

### Smach state machine
As we said smach is a fundamental component for the entire architecture, leading the implementation of the finite state machine. As we can see in the video, through the command: ```rosrun smach_viewer smach_viewer.py``` we can follow actual state changes.
<img src="https://github.com/Imdimark/EXPROLAB_Assignment1/assets/78663960/7cb4dc51-8ce3-4f5f-a7c0-62932a981d32" width="60%" height="60%">
 
 The states are WAIT_FOR_MAP, MOVE_IN_CORRIDORS, VISIT_ROOM, and CHARGING.

- WAIT_FOR_MAP in this state, the robot waits for a map to be loaded, which it uses for navigation.
- MOVE_IN_CORRIDORS  in this state, the robot moves in the corridors. It continues to move until its battery is low or an urgent room needs to be visited (in this case the state change only at the end of the movement.
- VISIT_ROOM  in this state, the robot visits a room. If the battery is low, it transitions to the charging state. Once the room has been visited, the robot goes back to moving in the corridors.
- CHARGING in this state, the robot moves to the charging station and starts charging its battery. Once the battery is fully charged, the robot goes back to moving in the corridors.
## Installation and running procedure <a name="installation"></a>
Some generic requirements can be necessary(like Python and ros), but the suggestion is to start with this container (based on Linux):  [carms84/exproblab](https://hub.docker.com/r/carms84/exproblab) 

Some mandatory prerequisites are needed:
- Download the project in your workspace:
  - ```cd <myworkspace>/src/```
  - ```git clone https://github.com/Imdimark/EXPROLAB_Assignment1```
- Install gnome terminal: ```sudo apt-get install gnome-terminal```
- Install armor, following this guideline: https://github.com/EmaroLab/armor
- Install smach: http://wiki.ros.org/smach
- Download the topological map ``` git clone https://github.com/buoncubi/topological_map``` under the project folder( ```roscd EXPROLAB_Assignment1``` )

First running of the code:
- If the roscore is not running let's do: ```roscore & ```
- Go under the workspace ```cd <myworkspace>/ ```
- Build the workspace ```catkin make ```
- Finally is possible to launch the code ```roslaunch assignment1 assignment1.launch  ```

Running of the code:
- Check if the rocore is running, otherwise do step 1 of the previous paragraph
- launch the code ```roslaunch assignment1 assignment1.launch  ```


**Optional**, if you want to edit the topological map, using protegé install the editor following this guideline: https://protege.stanford.edu/

In this last case be careful that if you save the edits made through ARMOR you can have some errors, please follow this guide: 
Due to an internal bug of Protégé, when you save an ontology manipulated with aRMOR, and then try to open it with Protégé, you might face an error similar to `Cause: Don't know how to translate SWRL Atom: _:genid2147483693`. If this occurs you will not be able to open the ontology. However, you can open it by following these steps.

1. Open the ontology as a text file.
2. Search for `// Rules` (which should be the last section of the file).
3. Delete the `Rules` section. Be careful that the `</rdf:RDF>` statement should remain as the last line of the file.
4. Save the ontology from the text editor.
5. Now you can open the ontology with Protégé.

Note that the 3rd point deletes all the SWRL rules from the ontology. Hence, the inferences of the reasoner are different from the ones that you got within ROS. To fully visualize the reasoner inferences from Protégé you can proceed in two ways.

1. Open the original ontology with Protégé, and copy-paste the three `SWLRule` (from the `SWRL` tab) back into the ontology manipulated with aRMOR. Now you can update the reasoner and check the knowledge it infers through Protégé.
2. Make aRMOR save the ontology by exporting the `INFERENCES` (there is a dedicated command for it). In this way, you do not have to copy-paste back the rules in the ontology as in point 1. However, in this way, Protégé would not let you see any differences between the knowledge you asserted in the ontology, and the knowledge inferred by the reasoner.



## Working hypothesis and environment <a name="hyp"></a>
### System's features
The system uses ROS nodes and components like ARMOR and SMACH implements a very well finite state machine that automatically chooses the correct state and uses the ontology for the knowledge ( in this case about the environment). ROS plays a fundamental connecting all the players and giving the possibility to scale up or scale down the system, also watching future improvements.

## System's limitations
Conformation of the room must be declared a prior (like doors, and rooms) and it could be more agnostic. The battery mechanism works very well, but the robot reaches the charging station ( in corridor E) without using the remaining battery. This is very unrealistic.

## Possible technical improvements
A possible technical improvement is implementing a simulated 3d environment environment like a gazebo. Next to that could be possible to implement an algorithm that preserves the battery to make it possible for the robot to reach the charging station. Regarding the agnosticism of the environment in the code, reaching information through a sensor like a camera could be useful to build the ontology before starting.

## Authors and contacts <a name="contacts"></a>

Author: Giovanni Di Marco
Mail: giovannidimarco06@gmail.com
Linkedin: https://www.linkedin.com/in/giovanni-di-marco-068453b1/






---------------------------------------------------------------------------------------------------------------------------------------------







miglioramenti futuri:fare in modo che arrivi alla stazione di ricarica con la batteria residua

In order to implement the mainly in corridor behaviour, the urgent threshold in the ontology has been changed.







