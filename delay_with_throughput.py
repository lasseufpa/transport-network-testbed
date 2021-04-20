import shlex, subprocess
import sys
from flask import request
import requests
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
from mapping import Testbed_Tools

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/src/")

from manage_switch import ChangeSwitch, PostDelaySwitch
import requests
import time

changeSwitch = ChangeSwitch()
postDelaySwitch = PostDelaySwitch()





changeSwitch.change_switch_route(1, 2, 1, 1, 2)
changeSwitch.change_switch_route(1, 3, 1, 1, 3)

changeSwitch.change_switch_route(2, 2, 1, 1, 3)
changeSwitch.change_switch_route(3, 2, 1, 1, 3)
changeSwitch.change_switch_route(7, 5, 1, 1, 3)

changeSwitch.change_switch_route(4, 2, 1, 1, 3)
changeSwitch.change_switch_route(5, 2, 1, 1, 3)
changeSwitch.change_switch_route(6, 2, 1, 1, 3)

changeSwitch.change_switch_route(8, 2, 1, 1, 3)

delay_array = []



url = 'http://127.0.0.1:5000/post_delay'

obj = 	{
        "delay": 'delay_for_graffic',
        "analyzed_switch": 7,
        "switch_adjacent":1,
        "port_no": 4
    }	



def main():
    os.remove('tmp/throughput.txt')
    #Primeira rota
    delay_is_less = False
    changeSwitch.change_switch_route(1, 4, 1, 1, 3)
    changeSwitch.change_switch_route(7, 5, 2, 1, 3)

    
    changeSwitch.manage_switch_traffic(1, 4, 10, 0, 0, 0, 'delay')    
    changeSwitch.manage_switch_traffic(7, 2, 10, 0, 0, 0, 'delay') 

    x = 0
    while (x < 15):
        
        x = x+1
        delay_array.append(requests.post(url=url, json=obj).json())


        if delay_array[-1] > 45:
            if delay_is_less == True:
                print("latest delay ", delay_array[-1], " go to second route ")
                changeSwitch.change_switch_route(1, 3, 1, 1, 3)
                changeSwitch.change_switch_route(2, 2, 1, 1, 3)
                changeSwitch.change_switch_route(3, 2, 1, 1, 3)
                changeSwitch.change_switch_route(7, 5, 1, 1, 3)

                delay_is_less = False
            else:
                print("latest delay ", delay_array[-1], " already in second route ")

        elif delay_array[-1] < 45:
            
            if delay_is_less == False:
                print("latest delay ", delay_array[-1], " go to main route ")
                changeSwitch.change_switch_route(1, 4, 1, 1, 3)
                changeSwitch.change_switch_route(7, 5, 2, 1, 3)
                
                delay_is_less = True
            else:
                print("latest delay ", delay_array[-1], " already in main route ")
            
        time.sleep(1)

    changeSwitch.manage_switch_traffic(1, 4, 50, 0, 0, 0, 'delay')    
    changeSwitch.manage_switch_traffic(7, 2, 50, 0, 0, 0, 'delay')    
    x = 0
    while (x < 15):
        
        x = x+1
        delay_array.append(requests.post(url=url, json=obj).json())


        if delay_array[-1] > 45:
            if delay_is_less == True:
                print("latest delay ", delay_array[-1], " go to second route ")
                changeSwitch.change_switch_route(1, 3, 1, 1, 3)
                changeSwitch.change_switch_route(2, 2, 1, 1, 3)
                changeSwitch.change_switch_route(3, 2, 1, 1, 3)
                changeSwitch.change_switch_route(7, 5, 1, 1, 3)

                delay_is_less = False
            else:
                print("latest delay ", delay_array[-1], " already in second route ")

        elif delay_array[-1] < 45:
            
            if delay_is_less == False:
                print("latest delay ", delay_array[-1], " go to main route ")
                changeSwitch.change_switch_route(1, 4, 1, 1, 3)
                changeSwitch.change_switch_route(7, 5, 2, 1, 3)
                
                delay_is_less = True
            else:
                print("latest delay ", delay_array[-1], " already in main route ")
            
        time.sleep(1)

    changeSwitch.manage_switch_traffic(1, 4, 20, 0, 0, 0, 'delay')    
    changeSwitch.manage_switch_traffic(7, 2, 20, 0, 0, 0, 'delay')    
    x = 0
    while (x < 15):
        
        x = x+1
        delay_array.append(requests.post(url=url, json=obj).json())


        if delay_array[-1] > 45:
            if delay_is_less == True:
                print("latest delay ", delay_array[-1], " go to second route ")
                changeSwitch.change_switch_route(1, 3, 1, 1, 3)
                changeSwitch.change_switch_route(2, 2, 1, 1, 3)
                changeSwitch.change_switch_route(3, 2, 1, 1, 3)
                changeSwitch.change_switch_route(7, 5, 1, 1, 3)

                delay_is_less = False
            else:
                print("latest delay ", delay_array[-1], " already in second route ")

        elif delay_array[-1] < 45:
            
            if delay_is_less == False:
                print("latest delay ", delay_array[-1], " go to main route ")
                changeSwitch.change_switch_route(1, 4, 1, 1, 3)
                changeSwitch.change_switch_route(7, 5, 2, 1, 3)
                
                delay_is_less = True
            else:
                print("latest delay ", delay_array[-1], " already in main route ")
            
        time.sleep(1)

    changeSwitch.manage_switch_traffic(1, 4, 60, 0, 0, 0, 'delay')    
    changeSwitch.manage_switch_traffic(7, 2, 60, 0, 0, 0, 'delay')    

    x = 0
    while (x < 15):
        
        x = x+1
        delay_array.append(requests.post(url=url, json=obj).json())


        if delay_array[-1] > 45:
            if delay_is_less == True:
                print("latest delay ", delay_array[-1], " go to second route ")
                changeSwitch.change_switch_route(1, 3, 1, 1, 3)
                changeSwitch.change_switch_route(2, 2, 1, 1, 3)
                changeSwitch.change_switch_route(3, 2, 1, 1, 3)
                changeSwitch.change_switch_route(7, 5, 1, 1, 3)

                delay_is_less = False
            else:
                print("latest delay ", delay_array[-1], " already in second route ")

        elif delay_array[-1] < 45:
            
            if delay_is_less == False:
                print("latest delay ", delay_array[-1], " go to main route ")
                changeSwitch.change_switch_route(1, 4, 1, 1, 3)
                changeSwitch.change_switch_route(7, 5, 2, 1, 3)
                
                delay_is_less = True
            else:
                print("latest delay ", delay_array[-1], " already in main route ")
            
        time.sleep(1)

    print(delay_array)
    print("Finishhhing...")

if __name__ == '__main__':
    main()