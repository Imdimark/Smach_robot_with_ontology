# SmachRobot_ROS

1. [Introduction](#introduction)
3. [Installation and running procedure](#installation)



## Introduction <a name="introduction"></a>
The project at hand focuses on the development and implementation of a surveillance robot, engineered to operate within an indoor environment. The robot's primary task is to move across different locations, residing there for specified durations before progressing to the next. This environment consists of a 2D layout with four rooms and three corridors. For an initial starting point, the robot is placed in a specific location referred to as 'E'.
The operational structure of the robot is based on a topological map, which it constructs using incoming data about the connections between various rooms, corridors, and doorways labeled as C1, C2, R1, R2, R3, and D1 to D6 respectively. This information aids the robot in maneuvering around its environment and effectively fulfilling its surveillance duties.
The robot's actions follow an endless cycle: it moves to a new location, waits for a while, and then moves again. This process continues until the robot's energy levels run low, at which point it returns to location 'E' for a recharge before resuming its routine.
When the robot's battery is not low, it navigates through the environment with a specific policy in mind. It's programmed to stay primarily in the corridors, keeping a closer eye on them. However, if a nearby room hasn't been inspected for a while, the robot will deviate from its path to check the room, ensuring complete and thorough surveillance.

## Installation and running procedure <a name="installation"></a>
Some generic requirements can be necessary(like Python and ros), but the suggestion is to start with this container (based on Linux):  [carms84/exproblab](https://hub.docker.com/r/carms84/exproblab) 

Some mandatory prerequisites are needed:
- Download the project in your workspace:
  - ```cd <myworkspace>/src/```
  - ```git clone https://github.com/Imdimark/SmachRobot_ROS```
- Install gnome terminal: ```sudo apt-get install gnome-terminal```
- Install armor, following this guideline: https://github.com/EmaroLab/armor
- Install smach: http://wiki.ros.org/smach
- Download the topological map ``` git clone https://github.com/buoncubi/topological_map``` under the project folder( ```roscd SmachRobot_ROS``` )

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

Note that the 3rd point deletes all the SWRL rules from the ontology. Hence, the inferences of the reasoner are different from the ones that you got within ROS. To fully visualise the reasoner inferences from Protégé you can proceed in two ways.

1. Open the original ontology with Protégé, and copy-paste the three `SWLRule` (from the `SWRL` tab) back into the ontology manipulated with aRMOR. Now you can update the reasoner and check the knowledge it infers through Protégé.
2. Make aRMOR save the ontology by exporting the `INFERENCES` (there is a dedicated command for it). In this way, you do not have to copy-paste back the rules in the ontology as in point 1. However, in this way, Protégé would not let you see any differences between the knowledge you asserted in the ontology, and the knowledge inferred by the reasoner.








miglioramenti futuri:fare in modo che arrivi alla stazione di ricarica con la batteria residua

In order to implement the mainly in corridor behaviour, the urgent threshold in the ontology has been changed.
![rosgraph](https://github.com/Imdimark/SmachRobot_ROS/assets/78663960/c9032477-4bab-49e4-8fcd-098970b08404)


![Screenshot 2023-07-13 155637](https://github.com/Imdimark/SmachRobot_ROS/assets/78663960/471cb60b-42c2-490f-9482-4c0e266a9d8f)



![image](https://github.com/Imdimark/SmachRobot_ROS/assets/78663960/5085a9b5-4172-486f-894a-04a6ba1a9bef)

  
![48739a0a-97ee-45ea-bc50-2c873329e5ed](https://github.com/Imdimark/SmachRobot_ROS/assets/78663960/82110b94-637e-4d00-a1e3-1c59031e0e9e)
