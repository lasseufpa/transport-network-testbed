# Mininet-4ward
## Scenarios
### tn_slices

### Testbed
This scenario creates a backhaul and fronthaul virtualized and has some functions to get status from SDN network. (e.g. Throughput, Delay and Jitter)

## How to create and run Mininet Topologies and Ryu Controller
Mininet topologies can be created acessing mininet_topology, and run one of the topologies inside this directory, or you can create your own topology. You can follow this steps to run the Ryu Controller + Mininet + API_Server


## Run mininet and Ryu Controller:

First you have to run Ryu Controller with ryu-manager tool, if you are in tn_slices directory, you need to go to ryu/ryu/app and run ryu-manager:

``` Shel scripting
$ cd ryu/ryu/app
$ ryu-manager delay_switch_monitor.py ofctl_rest.py --observe-links
```
The next step is running Mininet, let's use one of the topologies that have in mininet_topology
``` Shel scripting
$ sudo python first_topology.py
```

Note: if you are using your own topology, you have to wait a little after runing mininet

Finaly, run API_server:
``` Shel scripting
$ python3 server.py
```
## Deploy scenario:

Now that you have the system running, you can use insomnia, postman or wget to set the flows:


### For route http://127.0.0.1:5000/get_delay:
```json
	{
		"switch_analisado": 1 #here you will put the dpid of switch
	}	
```
### For route http://127.0.0.1:5000/deploy:
```json
	{
		"switch_analisado": 3,
		"switch_ida": 2,
		"switch_volta": 1,
		"host_a_ser_mudado": 1
	}
```

