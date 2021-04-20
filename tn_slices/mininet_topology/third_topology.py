from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call


import subprocess as sb
import os

#The useful links for create this topology are in doc/mininet
class Topology_Network():
        "Creating the Main Topology"

        net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

        info( '*** Adding controller\n' )
        c0=net.addController(name='c0',
                          controller=RemoteController,
                          ip='127.0.0.1',
                          protocol='tcp',
                          port=6633)

        s1 = net.addSwitch('s1')
        s2 = net.addSwitch('s2')
        s3 = net.addSwitch('s3')
        s4 = net.addSwitch('s4')
        s5 = net.addSwitch('s5')
        s6 = net.addSwitch('s6')
        s7 = net.addSwitch('s7')
        s8 = net.addSwitch('s8')

        h1 = net.addHost('h1', cls=Host, ip="10.0.0.1", defaultRoute=None)
        h2 = net.addHost('h2', cls=Host, ip="10.0.0.2", defaultRoute=None)
        h3 = net.addHost('h3', cls=Host, ip="10.0.0.3", defaultRoute=None)
       
        net.addLink(s1,s2,3,1, cls=TCLink, bw=10, delay='10ms') 
        net.addLink(s1,s4,4,1, cls=TCLink, bw=10, delay='20ms')
        net.addLink(s1,s8,5,1, cls=TCLink, bw=10, delay='20ms')
        net.addLink(s1,h1,1,1, cls=TCLink, bw=10, delay='20ms')
        net.addLink(s1,h2,2,1, cls=TCLink, bw=10, delay='20ms')

        net.addLink(s2,s3,2,1, bw=10, delay='10ms')
        net.addLink(s2,s4,3,2)
        net.addLink(s2,s5,4,2)

        net.addLink(s3,s7,2,1)
        net.addLink(s3,s6,3,2)
        
        net.addLink(s4,s5,3,1)
        
        net.addLink(s5,s6,3,1)
        
        net.addLink(s6,s7,3,2)
        
        net.addLink(s7,h3,4,1)

        net.addLink(s8,s7,2,3)

        info( '*** Starting network\n')
        net.build()
        info( '*** Starting controllers\n')
        for controller in net.controllers:
           controller.start()

        info( '*** Starting switches\n')
        net.get('s1').start([c0])
        net.get('s2').start([c0])
        net.get('s3').start([c0])
        net.get('s4').start([c0])
        net.get('s5').start([c0])
        net.get('s6').start([c0])
        net.get('s7').start([c0])
        net.get('s8').start([c0])
        
        info( '*** Post configure switches and hosts\n')
        h1.setMAC('00:00:00:00:00:01')
        h2.setMAC('00:00:00:00:00:02')
        h3.setMAC('00:00:00:00:00:03')
    
        h1.cmd('arp -s %s %s' % (h2.IP(), h2.MAC()))
        h1.cmd('arp -s %s %s' % (h3.IP(), h3.MAC()))

        h2.cmd('arp -s %s %s' % (h1.IP(), h1.MAC()))
        h2.cmd('arp -s %s %s' % (h3.IP(), h3.MAC()))

        h3.cmd('arp -s %s %s' % (h1.IP(), h1.MAC()))
        h3.cmd('arp -s %s %s' % (h2.IP(), h2.MAC()))
  

        CLI(net)
        net.stop()



if __name__ == '__main__':
    setLogLevel('info')
    Topology_Network()
