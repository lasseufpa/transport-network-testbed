import shlex, subprocess
import sys

import os
import time

import json
from flask import Flask, jsonify, request, render_template
from flask import request

import requests
dir_path = os.path.dirname(os.path.realpath(__file__))
from mapping import Testbed_Tools

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/src/")

from manage_switch import ChangeSwitch, PostDelaySwitch

#Instantiate the class
changeSwitch = ChangeSwitch()
postDelaySwitch = PostDelaySwitch()
testbed_tools = Testbed_Tools()

#Set Global variable
MEASUREMENTS_NUMBER = 5 #This is used in Jitter, here means that we going get the average of 5 delays requests
MAX_NUMBER_OF_SWITCHES = 40 #This is the MAX number of switches in topology

#Initiate the flask
app = Flask(__name__)

#THIS IS THE MAIN ROUTE
@app.route("/", methods=['GET'])
def index():
    return "Hello, World!"

#THIS FUNCTION CREATE THE FLOWS
@app.route("/set_flow_entries", methods=["POST"]) 
def change_switch_flow():
    req = request.json
    changeSwitch.change_switch_route(req['analyzed_switch'], 
                                    req['num_port_send'], 
                                    req['num_port_reciever'], 
                                    req['host_to_be_changed'], 
                                    req['destiny_host'])
    return req


@app.route("/switch_traffic_change", methods=["POST"]) 
def change_mininet_switch_traffic():
    req = request.json

    bash_cmd_output = None
    if req['type'] == 'delay':
        req['limit'], req['rate'], req['loss'] = 0,0,0
    elif req['type'] == 'rate':
        req['loss'] = 0
    elif req['type'] == 'loss':
        req['limit'], req['rate'], req['delay'] = 0,0,0
    elif req['type'] == 'list':
        req['limit'], req['rate'], req['delay'], req['loss'] = 0,0,0,0
        bash_cmd_output = subprocess.check_output(
                "sudo tc -p -s -d  qdisc show dev s{}-eth{}".format(req['switch'], req['iface_port']),
                stdin=None,
                stderr=None,
                shell=True,
                universal_newlines=False).split(b'\n')[0].decode('utf-8')

    if bash_cmd_output == None:
        bash_cmd_output = "Ok!"
        changeSwitch.manage_switch_traffic(req['switch'], req['iface_port'], req['delay'],
    req['limit'], req['rate'], req['loss'], req['type'])

    return bash_cmd_output

#THIS FUNCTION GET THE DELAY
@app.route("/post_delay", methods=["POST", "GET"]) 
def get_delay_between_switch():
    
    req = request.json
    
    with open(dir_path + "/tmp/setting.txt","w+") as f:
        json.dump(req['switch_adjacent'], f)

    postDelaySwitch.post_delay_switch(req['analyzed_switch'])

    for current_switch in range(1, MAX_NUMBER_OF_SWITCHES):
        if current_switch != req['switch_adjacent']:
            cmd_list = list("sed -i '/Switch X/d' tmp/jitter.txt")
            cmd_list[16] = str(current_switch)
            cmd_str = testbed_tools.convert_list_into_string(cmd_list)
    
            bash_cmd_output = testbed_tools.run_cmd_in_bash_window(cmd_str) 
    
    cmd1_str = "sed -i '/^$/d' tmp/jitter.txt"
    testbed_tools.run_cmd_in_bash_window("sed -i '/^$/d' tmp/jitter.txt")
    
    bash_cmd_output = testbed_tools.run_cmd_in_bash_window("awk -F \" \" '{print $3}' tmp/jitter.txt")
    
    print("The delay is: ", bash_cmd_output)
    
    if req['delay'] == "delay_kpi":
        os.remove('tmp/jitter.txt')
    
    if req['delay'] == "delay_for_graffic":
        with open(dir_path + "/tmp/delay_plot.txt","a+") as f:
            f.write("analyzer_switch ")
            f.write(str(req['analyzed_switch']))
            f.write(" ")
            f.write(bash_cmd_output)
            f.write("\n")
        os.remove('tmp/jitter.txt')

    return bash_cmd_output

@app.route("/get_delay", methods=["POST", "GET"])
def show_delay_between_switch():
    req = request.json

    print(req)
    return req['s1']

#THIS FUNCTION GET THE JITTER
@app.route("/get_jitter", methods=["POST", "GET"])
def get_jitter():
    req = request.json
    
    for iterator in range(1, MEASUREMENTS_NUMBER):
        postDelaySwitch.post_delay_switch(req['analyzed_switch'])
        time.sleep(2)

    for current_switch in range(1, MAX_NUMBER_OF_SWITCHES):
        if current_switch != req['switch_adjacent']:
            cmd_list = list("sed -i '/Switch X/d' tmp/jitter.txt")
            cmd_list[16] = str(current_switch)
            cmd_str = testbed_tools.convert_list_into_string(cmd_list)
            out = testbed_tools.run_cmd_in_bash_window(cmd_str)


    testbed_tools.run_cmd_in_bash_window("sed -i '/^$/d' tmp/jitter.txt")
    testbed_tools.run_cmd_in_bash_window("awk -F \" \" '{print $3}' tmp/jitter.txt > tmp/sum.txt")
    testbed_tools.run_cmd_in_bash_window("cat tmp/sum.txt")
    

    delays_output = open('tmp/sum.txt')
    array_of_delays = delays_output.readlines()
    
    sum_of_delay = 0.0
    for current_delay in range(0, (MEASUREMENTS_NUMBER-1)):
        sum_of_delay = sum_of_delay + float(array_of_delays[current_delay].replace('\n',''))

    jitter = sum_of_delay/MEASUREMENTS_NUMBER
    

    if req['jitter'] == "jitter_for_graffic":
        with open(dir_path + "/tmp/jitter_plot.txt","a+") as f:
            f.write("analyzer_switch ")
            f.write(str(req['analyzed_switch']))
            f.write(" ")
            f.write(str(jitter))
            f.write("\n")
        #os.remove('tmp/jitter.txt')

    os.remove('tmp/sum.txt')
    os.remove('tmp/jitter.txt')
    return str(jitter)

@app.route("/get_throughput", methods=["POST", "GET"])
def get_throughput():
    req = request.json
    output = dict()
    output = testbed_tools.run_cmd_in_bash_window("awk -F \" \" '{print $1}' tmp/throughput.txt")
    for x in range(1, MAX_NUMBER_OF_SWITCHES):
        print("this is the bash output ", output)
        print("this is the x output ", x)

        if x == output:
            print('foi')


    #print(data)
    return "okay"

if __name__ == "__main__":
    app.run(debug=True)
