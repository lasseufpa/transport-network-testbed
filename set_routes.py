#use with python3
import shlex, subprocess
import paramiko
import os
import time
import yaml

from mapping import Testbed_Tools


t = Testbed_Tools()

dir_path = os.path.dirname(os.path.realpath(__file__))

pid_host = []

with open("config.yaml", "r") as ymlfile:
    mapping_yaml = yaml.safe_load(ymlfile)


def convert_list_into_string(list_to_be_changed):
    final_new_string = ""
    for character in list_to_be_changed:
        final_new_string += character
    return final_new_string


subprocess.run(['sudo', 'mkdir','-p','/var/run/netns'])

str_eth0_ip= "192.168.x0.x"
str_veth_ip= "192.168.x0.1x"
str_host_ip = "10.0.0.x"
str_mininet_host = "mininet-hx"

eth0_ip = ['192.168.0.0']
veth_ip = ['192.168.0.0']
host_ip = ['10.0.0.0']
mininet_host = ["mininet-hx"]
cmd_to_get_mininet_ip = "ifconfig enp1s0 | grep inet | awk -F \" \" '{print $2}' | sed -n '1p'"

mininet_ip = subprocess.check_output(cmd_to_get_mininet_ip, 
                stdin=None,
                stderr=None,
                shell=True,
                universal_newlines=False).split(b'\n')[0].decode('utf-8')


for current_host in range(1, (len(mapping_yaml['ASSOCIATION'])+1)):
    machine_array = t.change_string_value(current_host, str_eth0_ip, str_veth_ip, str_host_ip, str_mininet_host)
    eth0_ip.append(machine_array[0])
    veth_ip.append(machine_array[1])
    host_ip.append(machine_array[2])
    mininet_host.append(machine_array[3])



for current_host in range(1, (len(mapping_yaml['ASSOCIATION'])+1)):
        cmd_list = list("ps aux | grep mininet | grep root | grep hX | awk -F \" \" '{print $2}'")
        cmd_list[42] = str(current_host)
        cmd_str = convert_list_into_string(cmd_list)
        
        pid_host.append(subprocess.check_output(cmd_str, 
                stdin=None,
                stderr=None,
                shell=True,
                universal_newlines=False).split(b'\n')[0].decode('utf-8'))

        subprocess.run(['sudo', 'ln','-fs', 
                        '/proc/{}/ns/net'.format(pid_host[current_host-1]), 
                        '/var/run/netns/{}'.format(pid_host[current_host-1])])
                        
        subprocess.run(['sudo', 'ip', 'link', 'add', 
                        'veth-h{}'.format(current_host), 'type', 
                        'veth', 'peer', 'name', 'eth0-h{}'.format(current_host)])


# Send veth to Mininet host namespace
for current_host in range(1, (len(mapping_yaml['ASSOCIATION'])+1)):
    subprocess.run(['sudo', 'ip', 'link', 'set', 'eth0-h{}'.format(current_host), 'netns', pid_host[current_host-1]])

# Turn network interfaces Up
for current_host in range(1, (len(mapping_yaml['ASSOCIATION'])+1)):
    print("funcionou")
    subprocess.run(['sudo','ip','netns','exec',
    pid_host[current_host-1], 'ip', 'link', 'set', 
    'eth0-h{}'.format(current_host), 'up'])
    subprocess.run(['sudo','ip','link','set',
    'veth-h{}'.format(current_host),'up'])

for current_host in range(1, (len(mapping_yaml['ASSOCIATION'])+1)):
    print("foir")
    subprocess.run(['sudo', 'ip', 'netns', 'exec', 
    '{}'.format(pid_host[current_host-1],), 'ip', 'addr', 'add', 
    '{}/24'.format(eth0_ip[current_host]), 'dev', 
    'eth0-h{}'.format(current_host)])

    subprocess.run(['sudo', 'ip', 'addr', 'add', 
    '{}/24'.format(veth_ip[current_host]), 'dev', 
    'veth-h{}'.format(current_host)])


#Node_N to All Nodes
for current_host in range(1, (len(mapping_yaml['ASSOCIATION'])+1)):
    for target_host in range(1, (len(mapping_yaml['ASSOCIATION'])+1)):
        if target_host != current_host:
            subprocess.run(['sudo', 'ip', 'rule', 'add', 'iif', 
            '{}'.format(mapping_yaml["ASSOCIATION"]["POD-H{}".format(target_host)]['iface_node']), 'from', 
            '{}'.format(mapping_yaml["ASSOCIATION"]["POD-H{}".format(target_host)]['pod_ip']), 'table', 
            '{}'.format(mininet_host[target_host])  ])
        
            subprocess.run(['sudo', 'ip', 'route', 'add', 
            '{}'.format(mapping_yaml["ASSOCIATION"]["POD-H{}".format(current_host)]['pod_ip']), 'via', 
            '{}'.format(eth0_ip[target_host]), 'dev', 
            'veth-h{}'.format(target_host), 'table', 
            '{}'.format(mininet_host[target_host]) ])

            subprocess.run(['sudo', 'ip', 'netns', 'exec', 
            '{}'.format(pid_host[target_host-1]), 'ip', 'route', 'add', 
            '{}'.format(mapping_yaml["ASSOCIATION"]["POD-H{}".format(current_host)]["pod_ip"]), 'via', 
            '{}'.format(host_ip[current_host] ) ])

            subprocess.run(['sudo', 'ip', 'netns', 'exec', 
            '{}'.format(pid_host[current_host-1]), 'ip', 'route', 'add', 
            '{}'.format(mapping_yaml["ASSOCIATION"]["POD-H{}".format(current_host)]["pod_ip"]),'via', 
            '{}'.format(veth_ip[current_host]) ])

#Enable IP FORWARD
subprocess.call("sudo sysctl -w net.ipv4.ip_forward=1 > /dev/null", shell=True)

#CREATE ROUTES
for current_host in range(1, (len(mapping_yaml['ASSOCIATION'])+1)):
    subprocess.run(['sudo', 'ip', 'route', 'add', 
    '{}'.format(mapping_yaml["ASSOCIATION"]["POD-H{}".format(current_host)]["pod_ip"]), 'via', 
    '{}'.format(mapping_yaml["ASSOCIATION"]["POD-H{}".format(current_host)]["node_ip"]), 'dev', 
    '{}'.format(mapping_yaml["ASSOCIATION"]["POD-H{}".format(current_host)]["iface_node"])])


#SSH CONNECTION
for current_host in range(1, (len(mapping_yaml['ASSOCIATION'])+1)):
    for target_host in range(1, (len(mapping_yaml['ASSOCIATION'])+1)):
        if target_host != current_host:
            t.remote_host_cmd(mapping_yaml["ASSOCIATION"]["POD-H{}".format(current_host)]["node_ip"], mapping_yaml["ASSOCIATION"]["POD-H{}".format(current_host)]["node_username"], 
                'echo 1q2w3e4r | sudo -S ip rule add from {} table mininet'
                .format(mapping_yaml["ASSOCIATION"]["POD-H{}".format(current_host)]["pod_ip"])
            )
            time.sleep(2)
            t.remote_host_cmd(mapping_yaml["ASSOCIATION"]["POD-H{}".format(current_host)]["node_ip"], mapping_yaml["ASSOCIATION"]["POD-H{}".format(current_host)]["node_username"], 
                'echo 1q2w3e4r | sudo -S ip route add {} via {} table mininet'
                .format(mapping_yaml["ASSOCIATION"]["POD-H{}".format(target_host)]["pod_ip"], mininet_ip)
            )
            time.sleep(2)

if os.path.exists(dir_path + "/rm_link.py"):
    os.remove(dir_path + "/rm_link.py")

fs = open(dir_path + "/rm_link.py","w+")

fs.write("import subprocess\n")
fs.write("import os\n")
fs.write("import time\n")
fs.write("import yaml\n")

fs.write("from mapping import Testbed_Tools\n")
fs.write("t = Testbed_Tools()\n\n")

fs.write("with open(\"config.yaml\", \"r\") as ymlfile:\n")
fs.write("    mapping_yaml = yaml.safe_load(ymlfile)\n")

for current_host in range(1, (len(mapping_yaml['ASSOCIATION'])+1)):
    fs.write("subprocess.call('sudo ip link delete veth-h{} 2> /dev/null',shell=True)\n".format(current_host))
    fs.write("subprocess.call('sudo rm -rf /var/run/netns/{}', shell=True)\n".format(pid_host[current_host-1]))
    fs.write("subprocess.call('sudo ip rule del from {}', shell=True)\n".format(mapping_yaml["ASSOCIATION"]["POD-H{}".format(current_host)]["pod_ip"]))
    fs.write("subprocess.call('sudo ip route del {}', shell=True)\n".format(mapping_yaml["ASSOCIATION"]["POD-H{}".format(current_host)]["pod_ip"]))


for current_host in range(1, (len(mapping_yaml['ASSOCIATION'])+1)):
    for target_host in range(1, (len(mapping_yaml['ASSOCIATION'])+1)):
        fs.write(
        "t.remote_host_cmd(mapping_yaml[\"ASSOCIATION\"][\"POD-H{}\"][\"node_ip\"], mapping_yaml[\"ASSOCIATION\"][\"POD-H{}\"][\"node_username\"], 'echo 1q2w3e4r | sudo -S ip rule del from {} table mininet')\n"
        .format(current_host, current_host, mapping_yaml["ASSOCIATION"]["POD-H{}".format(current_host)]["pod_ip"])
        )
        
        fs.write("time.sleep(2)\n")
        
        fs.write(
        "t.remote_host_cmd(mapping_yaml[\"ASSOCIATION\"][\"POD-H{}\"][\"node_ip\"], mapping_yaml[\"ASSOCIATION\"][\"POD-H{}\"][\"node_username\"], 'echo 1q2w3e4r | sudo -S ip route del {} table mininet')\n"
        .format(current_host, current_host, mapping_yaml["ASSOCIATION"]["POD-H{}".format(target_host)]["pod_ip"])
        )
        fs.write("time.sleep(2)\n\n")

fs.write("print(\"The links were deleted!!!\")\n")
fs.close()

print("The links were created!!!")
