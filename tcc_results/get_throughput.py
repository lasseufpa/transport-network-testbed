import shlex, subprocess
import sys
from flask import request
import requests
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
from mapping import Testbed_Tools

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/src/")

from manage_switch import ChangeSwitch, PostDelaySwitch

import time

changeSwitch = ChangeSwitch()


#create the default routes!!!

changeSwitch.change_switch_route(1, 2, 1, 1, 2)
changeSwitch.change_switch_route(1, 3, 1, 1, 3)

changeSwitch.change_switch_route(2, 2, 1, 1, 3)
changeSwitch.change_switch_route(3, 2, 1, 1, 3)
changeSwitch.change_switch_route(7, 5, 1, 1, 3)

changeSwitch.change_switch_route(4, 2, 1, 1, 3)
changeSwitch.change_switch_route(5, 2, 1, 1, 3)
changeSwitch.change_switch_route(6, 2, 1, 1, 3)

changeSwitch.change_switch_route(8, 2, 1, 1, 3)


def main():
    os.remove('tmp/throughput.txt')
    #Primeira rota
    
    changeSwitch.manage_switch_traffic(1, 3, 10, 1000, 6, 0.4, "rate") #Adicionando largura de banda
    
    print("primeira rota...")
    

    #Segunda rota
    time.sleep(15)
    changeSwitch.change_switch_route(1, 4, 1, 1, 3)
    changeSwitch.change_switch_route(7, 5, 2, 1, 3)

    changeSwitch.manage_switch_traffic(1, 4, 10, 1000, 8, 0.4, "rate")
    
    print("Segunda rota...")
    

    #Terceira rota
    time.sleep(15)
    changeSwitch.change_switch_route(1, 5, 1, 1, 3)
    changeSwitch.change_switch_route(7, 5, 3, 1, 3)

    changeSwitch.manage_switch_traffic(1, 5, 10, 1000, 2, 0.4, "rate")
    
    print("Terceira rota...")
    

    #Quarta rota
    time.sleep(15)
    changeSwitch.change_switch_route(1, 6, 1, 1, 3)
    changeSwitch.change_switch_route(7, 5, 4, 1, 3)

    changeSwitch.manage_switch_traffic(1, 6, 10, 1000, 5, 0.4, "rate")
    
    print("Quarta rota...")
    time.sleep(15)
    
    
    print("Finishhhing")

if __name__ == '__main__':
    main()
