#!/usr/bin/env python3

import socket
import sys
import time
import math
import numpy as  np
import matplotlib.pyplot as plt 

# Imports from ROS
import rospy
from std_msgs.msg import String

# Import message file
from khepera_communicator.msg import K4_controls, SensorReadings

# Server socket port input at script launch
print("========== Khepera IV Communicatoion Driver Node ==========")

var = 109 # last 3 digits of one of the Khepera bots in the lab
print("You entered: ", var)
KHEP_IP_NO = int(var) #UDP Port number of this Khepera robot


# Creating socket (DGRAM is data gram, how UDP works)
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Automatically get the standard host name from local computer
host_name = socket.gethostname()

# Please Change this host ip to the IP address of your own computer
host_ip = '192.168.0.103'

# Bind socket (the port number will be 2000 + last 3 digit of the Khepera IP)
# Thus we will have a unique port number for each Khepera to send sensor data to, if needed in the future
serverSock.bind((host_ip, 2000 + int(KHEP_IP_NO)))
serverSock.settimeout(5)


# Establish the node 
# (the name of the node will end with the port number, ex: 'K4_Comm_3000' for port 3000)
rospy.init_node('K4_Send_Cmd_' + str(KHEP_IP_NO), anonymous=True)

# Initialize angular(W) and linear(V) velocity control variables
W = 0
V = 0

# Address and port for the Khepera robot intended to send commands
addr = ('192.168.0.' + str(KHEP_IP_NO), 2000)

# Global variables for callbacks 
last_data = K4_controls()
started = False
x = 0
def callback(data):
    global started, last_data
    last_data = data
    if (not started):
        started = True

def timer_callback(event):
    global started, last_data
    global W, V
    global x
    if (started):
        rospy.loginfo(last_data)
        # Commands for the Khepera
        W = last_data.ctrl_W
        V = last_data.ctrl_V

        # UDP communication
        serverSock.sendto(bytes(str(W) + 'x' + str(V),'utf-8'), addr)
        try:
            response = serverSock.recv(4096)
            print("\nResponse:\n{}".format(response.decode('utf-8')))
        except:
            print("Nothing received over socket.")


def send_cmd():
    s = rospy.Subscriber('K4_controls_' + str(var), K4_controls, callback)
    timer = rospy.Timer(rospy.Duration(0.025), timer_callback) # Set frequency to 50 hz (0.02 sec interval)
    rospy.spin()
    timer.shutdown()

if __name__ == '__main__':
    try:
        send_cmd()
    except rospy.ROSInterruptException:
        pass