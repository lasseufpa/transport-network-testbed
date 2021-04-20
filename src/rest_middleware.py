import json
import time

import numpy as np
import requests
import re

class GetFunctions():
    def get_port_desc(url):
        r = requests.get(url=url)
        return r.json()

    def get_stats_switch(url):
        r = requests.get(url=url)
        return r.json()

class PostFunctions():
    def change_table_entry(url, switch_id, table_id, priority, host, net_code, go_to_table_id):
        if net_code == 2048:
            change_table = {
                    "dpid": switch_id,
                    "table_id": table_id,
                    "priority": priority,
                    "flags": 1,
                    "match": {
                        "ipv4_dst": host,
                        "eth_type": net_code,

                    },
                    "actions": [
                        {
                            "type": "GOTO_TABLE",
                            "table_id": go_to_table_id
                        }
                    ]
            }
        else:
            change_table = {
                    "dpid": switch_id,
                    "table_id": table_id,
                    "priority": priority,
                    "flags": 1,
                    "match": {
                        "arp_tpa": host,
                        "eth_type": net_code,

                    },
                    "actions": [
                        {
                            "type": "GOTO_TABLE",
                            "table_id": go_to_table_id
                        }
                    ]
            }

        r = requests.post(url=url, json=change_table)
        return r


    def add_flow_entry(url, switch_id, table_id, priority, in_port, host, net_code, out_port):
        ip_type = "ipv4_dst"
        if net_code == 2054:
            ip_type = "arp_tpa"

        if in_port == 0:
            adding_flow = {
                    "dpid": switch_id,
                    "table_id": table_id,
                    "priority": priority,
                    "flags": 1,
                    "match": {
                        ip_type: host,
                        "eth_type": net_code,

                    },
                    "actions": [
                        {
                            "type": "OUTPUT",
                            "port": out_port
                        }
                    ]
            }
        else:
            adding_flow = {
                    "dpid": switch_id,
                    "table_id": table_id,
                    "priority": priority,
                    "flags": 1,
                    "match": {
                        "in_port": in_port,
                        ip_type: host,
                        "eth_type": net_code,

                    },
                    "actions": [
                        {
                            "type": "OUTPUT",
                            "port": out_port
                        }
                    ]
            }

        r = requests.post(url=url, json=adding_flow)
        return r

    def clean_all_flow_entry(url, switch_id, table_id):
        clean_flows = {"dpid": switch_id,
            "table_id": table_id, "priority": 500, "flags": 1}
        r = requests.post(url=url, json=clean_flows)
        return r

