import yaml
import time
import subprocess as sp
import os.path
from subprocess import Popen, PIPE, STDOUT
import sys
import socket
import termios

from mapping import Testbed_Tools


testbed_tools = Testbed_Tools()

def start_topology(f):

    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(dir_path)
    fnull = open(os.devnull, "w")

    
    if not os.path.exists("ryu-controller/ryu/ryu/app"):
        print("you have to install ryu first")
        quit()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(dir_path)
    
    print("Starting mininet and ryu...")
    sp.Popen(["sudo", "python", "mininet_topology/first_topology.py", "&>", "/dev/null"],  stdout=fnull)
    sys.stdout.flush()
    sys.stdin.flush()
    termios.tcflush(sys.stdin, termios.TCIOFLUSH)
    time.sleep(2)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    ryu_path = "ryu-controller/ryu/ryu/app/"
    sys.path.append(dir_path + ryu_path)
    

    sp.Popen(["ryu-manager", "{}testbed_analyzer.py".format(ryu_path), "{}ofctl_rest.py".format(ryu_path), "--observe-links"], stdout=fnull)
    sys.stdout.flush()
    sys.stdin.flush()
    termios.tcflush(sys.stdin, termios.TCIOFLUSH)
    time.sleep(5)
    
    print("Starting server.py...")
    sp.Popen(["python3", "server.py"], stdout=fnull)
    sys.stdout.flush()
    sys.stdin.flush()
    termios.tcflush(sys.stdin, termios.TCIOFLUSH)
  
    time.sleep(2)
    print("Mininet started successfull!!!")

def stop_topology(f):

    fnull = open(os.devnull, "w")
    sp.Popen(["sudo", "mn", "-c"],  stdout=fnull)
    print("Removing Mininet and Ryu...")
    sys.stdout.flush()
    sys.stdin.flush()
    termios.tcflush(sys.stdin, termios.TCIOFLUSH)
    time.sleep(5)

    
    s1 = testbed_tools.run_cmd_in_bash_window("ps aux | grep server.py | awk -F \" \" '{print $2}'")
    s2 = testbed_tools.run_cmd_in_bash_window("ps aux | grep server.py | grep python | awk -F \" \" '{print $2}'")

    print("Removing server.py and manage_switch.py")
    sp.Popen(['sudo','kill', '-9', s1], stdout=fnull)
    
    sys.stdout.flush()
    sys.stdin.flush()
    termios.tcflush(sys.stdin, termios.TCIOFLUSH)
    time.sleep(2)

    sp.Popen(['sudo','kill', '-9', s2], stdout=fnull)

    sys.stdout.flush()
    sys.stdin.flush()
    termios.tcflush(sys.stdin, termios.TCIOFLUSH)
    time.sleep(4)
 
    print("Ok!")