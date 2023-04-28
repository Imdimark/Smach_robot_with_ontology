#!/usr/bin/env python

import rospy
import time
import rospkg
import subprocess
from armor_api.armor_client import ArmorClient
from std_msgs.msg import Bool

rospy.init_node('InitMapNode')

 
url = 'https://github.com/buoncubi/topological_map/blob/main/topological_map.owl'
filename = 'topological_map.owl'

subprocess.call(['wget', url, '-O', filename])



#waitfor a server
armcli = ArmorClient("example", "ontoRef")
armcli.call('LOAD','FILE','',['topological_map.owl', 'http://bnc/exp-rob-lab/2022-23', 'true', 'PELLET', 'false'])
armcli.call('ADD','OBJECTPROP','IND',['hasDoor', 'E', 'D6'])
armcli.call('ADD','OBJECTPROP','IND',['hasDoor', 'E', 'D7'])
armcli.call('ADD','OBJECTPROP','IND',['hasDoor', 'R1', 'D1'])
armcli.call('ADD','OBJECTPROP','IND',['hasDoor', 'R2', 'D2'])
armcli.call('ADD','OBJECTPROP','IND',['hasDoor', 'R3', 'D3'])
armcli.call('ADD','OBJECTPROP','IND',['hasDoor', 'R4', 'D4'])
armcli.call('ADD','OBJECTPROP','IND',['hasDoor', 'C1', 'D1'])
armcli.call('ADD','OBJECTPROP','IND',['hasDoor', 'C1', 'D2'])
armcli.call('ADD','OBJECTPROP','IND',['hasDoor', 'C1', 'D5'])
armcli.call('ADD','OBJECTPROP','IND',['hasDoor', 'C1', 'D6'])
armcli.call('ADD','OBJECTPROP','IND',['hasDoor', 'C2', 'D3'])
armcli.call('ADD','OBJECTPROP','IND',['hasDoor', 'C2', 'D4'])
armcli.call('ADD','OBJECTPROP','IND',['hasDoor', 'C2', 'D5'])
armcli.call('ADD','OBJECTPROP','IND',['hasDoor', 'C2', 'D7'])
armcli.call('DISJOINT','IND','',['R1','R2','R3','R4','E','C1','C2','D1','D2','D3','D4','D5','D6','D7'])
armcli.call('REASON','','',[''])



rospy.loginfo('Map loaded, closing the node InitMapNode')
