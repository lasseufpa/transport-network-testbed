import json
import time

import numpy as np
import requests
import re

from rest_middleware import PostFunctions as post_ryu, GetFunctions as  get_ryu

import os

import shlex, subprocess
import yaml

from mapping import Testbed_Tools

dir_path = os.path.dirname(os.path.realpath(__file__))

t = Testbed_Tools()

with open("config.yaml", "r") as ymlfile:
    mapping_yaml = yaml.safe_load(ymlfile)


######################################### Global Variables ###################################################

# Static Hosts
hosts = ["10.0.0.0/24", "10.0.0.1", "10.0.0.2", "10.0.0.3"]
pod_ip = ["192.168.46.0/26", mapping_yaml["ASSOCIATION"]["POD-H1"]["pod_ip"], mapping_yaml["ASSOCIATION"]["POD-H2"]["pod_ip"], "192.168.46.128/26"]

# IP and ARP codes
ip_code, arp_code = 2048, 2054

#Priority
high_priority, low_priority = 500, 0

# URL's
add_uri = 'http://localhost:8080/stats/flowentry/add'
del_uri = 'http://localhost:8080/stats/flowentry/delete'

switches_stats = 'http://localhost:8080/stats/switches'

table_id = lambda x: x
go_to = lambda x: x

number_of_switch = get_ryu.get_port_desc(switches_stats)



######################################### Clean entry and define table - TABLE 0 ###################################################

class SwitchKpiObject():
    def switch_kpi_object(self, switch_id, port_number):  
        return {
            "switch_{}:port_{}".format(switch_id,port_number) : {
                    'delay': '',
                    'jitter': '',
                    'throughput': '',
                    'updated_at': '',
                }
        }

dir_path = os.path.dirname(os.path.realpath(__file__))

        

with open(dir_path + "/../tmp/default_path.json","r+") as my_paths:
    default_paths = json.load(my_paths)
#print(default_paths)
switch_kpi_instance = SwitchKpiObject()

#sed -i '1d;2d;3d' tmp/adjacency_matrices.yaml




#with open(dir_path + "/../tmp/adjacency_matrices.yaml","r") as yamlfile:
#    
#    data = yaml.load(yamlfile, Loader=yaml.FullLoader)
#    
#    if data['dictitems']
#    print(data['dictitems'][6][3])

for current_switch in range(1, (len(number_of_switch)+1)):
    post_ryu.clean_all_flow_entry(del_uri, current_switch, 1)
    post_ryu.clean_all_flow_entry(del_uri, current_switch, 2)

for x in range(1, len(number_of_switch)+1):
    post_ryu.change_table_entry(add_uri, x, 0, high_priority, hosts[0], ip_code, 1)
    post_ryu.change_table_entry(add_uri, x, 0, high_priority, hosts[0], arp_code, 2)

    post_ryu.change_table_entry(add_uri, x, 0, high_priority, pod_ip[1], ip_code, 1)
    post_ryu.change_table_entry(add_uri, x, 0, high_priority, pod_ip[1], arp_code, 2)

    post_ryu.change_table_entry(add_uri, x, 0, high_priority, pod_ip[2], ip_code, 1)
    post_ryu.change_table_entry(add_uri, x, 0, high_priority, pod_ip[2], arp_code, 2)

class ChangeSwitch():
    def change_switch_route(self, s_analisado, s_ida, s_volta, the_host, destiny_host):
        post_ryu.add_flow_entry(add_uri, s_analisado, table_id(1), high_priority, 0,hosts[the_host], ip_code, go_to(s_volta))
        post_ryu.add_flow_entry(add_uri, s_analisado, table_id(1), high_priority, s_volta,hosts[destiny_host], ip_code, go_to(s_ida))
        
        post_ryu.add_flow_entry(add_uri, s_analisado, table_id(2), low_priority, 0, hosts[the_host], arp_code, go_to(s_volta))
        post_ryu.add_flow_entry(add_uri, s_analisado, table_id(2), low_priority, s_volta, hosts[destiny_host], arp_code, go_to(s_ida))

        post_ryu.add_flow_entry(add_uri, s_analisado, table_id(1), high_priority, 0,pod_ip[the_host], ip_code, go_to(s_volta))
        post_ryu.add_flow_entry(add_uri, s_analisado, table_id(1), high_priority, s_volta,pod_ip[destiny_host], ip_code, go_to(s_ida))

        post_ryu.add_flow_entry(add_uri, s_analisado, table_id(2), low_priority, 0, pod_ip[the_host], arp_code, go_to(s_volta))
        post_ryu.add_flow_entry(add_uri, s_analisado, table_id(2), low_priority, s_volta, pod_ip[destiny_host], arp_code, go_to(s_ida))

    
    def manage_switch_traffic(self, switch, iface_port, delay, limit, rate, loss, type_request):
        if type_request == 'delay':
            subprocess.run(['sudo', 'tc','qdisc','change','dev',
            's{}-eth{}'.format(int(switch), int(iface_port)), 'handle', '10:', 'netem', 'delay', '{}ms'.format(delay)])
        elif type_request == 'rate':
            subprocess.run(['sudo', 'tc','qdisc','replace','dev',
            's{}-eth{}'.format(int(switch), int(iface_port)), 'root', 'netem', 'delay', 
            '{}ms'.format(delay), 'rate', '{}Mbit'.format(rate),'limit','{}'.format(limit)])
        elif type_request == 'loss':
            subprocess.run(['sudo', 'tc','qdisc','change','dev',
            's{}-eth{}'.format(int(switch), int(iface_port)), 'handle', '10:', 'netem', 'loss', '{}%'.format(loss)])
            

class PostDelaySwitch():
    def post_delay_switch(self, s_analisado):  
        post_ryu.change_table_entry(add_uri, s_analisado, table_id(0), high_priority, hosts[0], ip_code, 3)
        time.sleep(0.1)   
        post_ryu.change_table_entry(add_uri, s_analisado, table_id(0), high_priority, hosts[0], ip_code, 1)


def main():
    change = ChangeSwitch()
    print("Creating Default Routes...")

    
    
    change.change_switch_route(1, 2, 1, 1, 2)
    change.change_switch_route(1, 3, 1, 1, 3)

    change.change_switch_route(2, 2, 1, 1, 3)
    change.change_switch_route(3, 2, 1, 1, 3)
    change.change_switch_route(7, 5, 1, 1, 3)

    change.change_switch_route(4, 2, 1, 1, 3)
    change.change_switch_route(5, 2, 1, 1, 3)
    change.change_switch_route(6, 2, 1, 1, 3)

    change.change_switch_route(8, 2, 1, 1, 3)

    
   


    #Isso é para o Host H2 que não aparece no TCC
    #change.change_switch_route(1, 3, 2, 2, 3)
    #change.change_switch_route(2, 2, 1, 2, 3)
    #change.change_switch_route(3, 2, 1, 2, 3)
    #change.change_switch_route(7, 5, 1, 2, 3)

    time.sleep(1)
    print("Finish!")

if __name__ == '__main__':
    main()
