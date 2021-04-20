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
import flask

changeSwitch = ChangeSwitch()
postDelaySwitch = PostDelaySwitch()


url = 'http://127.0.0.1:5000/post_delay'
obj1 = 	{
		"delay": 'delay_for_graffic',
		"analyzed_switch": 1,
		"switch_adjacent": 2,
		"port_no": 3
	}	

obj2 = 	{
		"delay": 'delay_for_graffic',
		"analyzed_switch": 1,
		"switch_adjacent": 7,
		"port_no": 4
	}	

obj3 = 	{
		"delay": 'delay_for_graffic',
		"analyzed_switch": 1,
		"switch_adjacent": 4,
		"port_no": 5
	}	

obj4 = 	{
		"delay": 'delay_for_graffic',
		"analyzed_switch": 1,
		"switch_adjacent": 8,
		"port_no": 6
	}	

def main():
    #os.remove('tmp/sum_delay_tcc.txt')
    #Primeira rota
    first_delay_array = []
    second_delay_array = []
    third_delay_array = []
    fourth_delay_array = []

    x=0
    while (x < 15):
        x = x+1

        first_delay_array.append(requests.post(url=url, json=obj1).json())
        second_delay_array.append(requests.post(url=url, json=obj2).json())
        third_delay_array.append(requests.post(url=url, json=obj3).json())
        fourth_delay_array.append(requests.post(url=url, json=obj4).json())

        time.sleep(1)
        
    
    print("primeira mudança...")
    print("the delay ", first_delay_array)
    print("\n")
    print("the delay ", second_delay_array)
    print("\n")
    print("the delay ", third_delay_array)
    print("\n")
    print("the delay ", fourth_delay_array)

    x=0
    while (x < 15):
        x = x+1
        first_delay_array.append(requests.post(url=url, json=obj1).json())
        second_delay_array.append(requests.post(url=url, json=obj2).json())
        third_delay_array.append(requests.post(url=url, json=obj3).json())
        fourth_delay_array.append(requests.post(url=url, json=obj4).json())
        
        time.sleep(1)
        

    print("Segunda mudança...")
    print("the delay ", first_delay_array)
    print("\n")
    print("the delay ", second_delay_array)
    print("\n")
    print("the delay ", third_delay_array)
    print("\n")
    print("the delay ", fourth_delay_array)

    x=0
    while (x < 15):
        x = x+1

        first_delay_array.append(requests.post(url=url, json=obj1).json())
        second_delay_array.append(requests.post(url=url, json=obj2).json())
        third_delay_array.append(requests.post(url=url, json=obj3).json())
        fourth_delay_array.append(requests.post(url=url, json=obj4).json())

        time.sleep(1)
        
    
    print("primeira mudança...")
    print("the delay ", first_delay_array)
    print("\n")
    print("the delay ", second_delay_array)
    print("\n")
    print("the delay ", third_delay_array)
    print("\n")
    print("the delay ", fourth_delay_array)

    x=0
    while (x < 15):
        x = x+1
        first_delay_array.append(requests.post(url=url, json=obj1).json())
        second_delay_array.append(requests.post(url=url, json=obj2).json())
        third_delay_array.append(requests.post(url=url, json=obj3).json())
        fourth_delay_array.append(requests.post(url=url, json=obj4).json())
        
        time.sleep(1)
        

    print("Segunda mudança...")
    print("the delay ", first_delay_array)
    print("\n")
    print("the delay ", second_delay_array)
    print("\n")
    print("the delay ", third_delay_array)
    print("\n")
    print("the delay ", fourth_delay_array)

        

if __name__ == '__main__':
    main()
