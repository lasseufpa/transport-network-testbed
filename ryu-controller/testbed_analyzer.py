from __future__ import division
import copy
from operator import attrgetter

from ryu.base import app_manager
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.base.app_manager import lookup_service_brick
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import in_proto
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import arp
from ryu.lib.packet import ipv4
from ryu.lib.packet import ipv6
from ryu.lib.packet import icmp
from ryu.lib.packet import ether_types
from ryu.lib import mac
from ryu.lib import hub
from ryu.lib import ip
from ryu.topology.api import get_switch, get_link
from ryu.app.wsgi import ControllerBase
from ryu.topology import event

from collections import defaultdict
import collections as col
from operator import itemgetter

import os
import os.path

import random
import time
import sys

import pickle

import json

from flask import request
import requests

import pprint

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path + "/../../../../")

from collections import defaultdict



# Cisco Reference bandwidth = 1 Gbps
REFERENCE_BW = 10000

DEFAULT_BW = 1000000

MAX_PATHS = float('Inf')

class ProjectController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ProjectController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.topology_api_app = self
        self.datapath_list = {}
        self.arp_table = {}
        self.switches = []
        self.hosts = {}
        self.multipath_group_ids = {}
        self.group_ids = []
        self.adjacency = defaultdict(dict)
        self.bandwidths = defaultdict(lambda: defaultdict(lambda: DEFAULT_BW))

        # Fake addresses only known to the controller
        self.controller_ip = "10.0.0.100"
        self.controller_mac = "dd:dd:dd:dd:dd:df"
        self.ping_mac = "00:00:00:00:00:01" #de:dd:dd:dd:de:dd
        self.ping_ip = "10.0.0.1"
        self.delay = defaultdict(lambda: defaultdict(lambda: 0))
        self.analisador = 0

        self.name = 'monitor'
        self.datapaths = {}
        self.port_stats = {}
        self.port_speed = {}
        self.flow_stats = {}
        self.flow_speed = {}
        self.stats = {}
        self.port_features = {}
        self.free_bandwidth = {}
        self.awareness = lookup_service_brick('awareness')
        self.graph = None
        self.capabilities = None
        self.best_paths = None
        # Start to green thread to monitor traffic and calculating
        # free bandwidth of links respectively.
        self.monitor_thread = hub.spawn(self._monitor)
        self.save_freebandwidth_thread = hub.spawn(self._save_bw_graph)

        self.replied = []
    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev): #proprio do monitor
        """
            Record datapath's info
        """
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if not datapath.id in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id] 

    def _monitor(self): #proprio do monitor
        """
            Main entry method of monitoring traffic.
        """
        while True:
            self.stats['flow'] = {}
            self.stats['port'] = {}
            for dp in self.datapaths.values():
                self.port_features.setdefault(dp.id, {})
                self._request_stats(dp)
                # refresh data.
                self.capabilities = None
                self.best_paths = None
            hub.sleep(1)
            if self.stats['flow'] or self.stats['port']:
                self.show_stat('flow')
                self.show_stat('port')
                hub.sleep(1)
    def _save_bw_graph(self): #proprio do monitor
        """
            Save bandwidth data into networkx graph object.
        """
        while True:
            self.graph = self.create_bw_graph(self.free_bandwidth)
            self.logger.debug("save_freebandwidth")
            hub.sleep(1)
    def _request_stats(self, datapath):
        """
            Sending request msg to datapath
        """
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPPortDescStatsRequest(datapath, 0)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    def get_min_bw_of_links(self, graph, path, min_bw):
        """
            Getting bandwidth of path. Actually, the mininum bandwidth
            of links is the bandwith, because it is the neck bottle of path.
        """
        _len = len(path)
        if _len > 1:
            minimal_band_width = min_bw
            for i in xrange(_len-1):
                pre, curr = path[i], path[i+1]
                if 'bandwidth' in graph[pre][curr]:
                    bw = graph[pre][curr]['bandwidth']
                    minimal_band_width = min(bw, minimal_band_width)
                else:
                    continue
            return minimal_band_width
        return min_bw

    def get_best_path_by_bw(self, graph, paths):
        """
            Get best path by comparing paths.
        """
        capabilities = {}
        best_paths = copy.deepcopy(paths)

        for src in paths:
            for dst in paths[src]:
                if src == dst:
                    best_paths[src][src] = [src]
                    capabilities.setdefault(src, {src: 1000000})
                    capabilities[src][src] = 1000000
                    continue
                max_bw_of_paths = 0
                best_path = paths[src][dst][0]
                for path in paths[src][dst]:
                    min_bw = 1000000
                    min_bw = self.get_min_bw_of_links(graph, path, min_bw)
                    if min_bw > max_bw_of_paths:
                        max_bw_of_paths = min_bw
                        best_path = path

                best_paths[src][dst] = best_path
                capabilities.setdefault(src, {dst: max_bw_of_paths})
                capabilities[src][dst] = max_bw_of_paths
        self.capabilities = capabilities
        self.best_paths = best_paths
        return capabilities, best_paths

    def create_bw_graph(self, bw_dict):
        """
            Save bandwidth data into networkx graph object.
        """
        try:
            graph = self.awareness.graph
            link_to_port = self.awareness.link_to_port
            for link in link_to_port:
                (src_dpid, dst_dpid) = link
                (src_port, dst_port) = link_to_port[link]
                if src_dpid in bw_dict and dst_dpid in bw_dict:
                    bw_src = bw_dict[src_dpid][src_port]
                    bw_dst = bw_dict[dst_dpid][dst_port]
                    bandwidth = min(bw_src, bw_dst)
                    # add key:value of bandwidth into graph.
                    graph[src_dpid][dst_dpid]['bandwidth'] = bandwidth
                else:
                    graph[src_dpid][dst_dpid]['bandwidth'] = 0
            return graph
        except:
            self.logger.info("Create bw graph exception")
            if self.awareness is None:
                self.awareness = lookup_service_brick('awareness')
            return self.awareness.graph

    def _save_freebandwidth(self, dpid, port_no, speed):
        # Calculate free bandwidth of port and save it.
        port_state = self.port_features.get(dpid).get(port_no)
        if port_state:
            capacity = port_state[2]
            curr_bw = self._get_free_bw(capacity, speed)
            self.free_bandwidth[dpid].setdefault(port_no, None)
            self.free_bandwidth[dpid][port_no] = curr_bw
        else:
            self.logger.info("Fail in getting port state")

    def _save_stats(self, _dict, key, value, length):
        if key not in _dict:
            _dict[key] = []
        _dict[key].append(value)

        if len(_dict[key]) > length:
            _dict[key].pop(0)

    def _get_speed(self, now, pre, period): #teste
        #agora vai
        if period:
            return (now - pre) / (period)
        else:
            return 0

    def _get_free_bw(self, capacity, speed):
        # BW:Mbit/s 
        #ta certo!!!!!
        return max(capacity / 10**3 - speed * 8, 0)

    def _get_time(self, sec, nsec):
        return sec + nsec / (10 ** 9)

    def _get_period(self, n_sec, n_nsec, p_sec, p_nsec):
        return self._get_time(n_sec, n_nsec) - self._get_time(p_sec, p_nsec)
    
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        """
            Save flow stats reply info into self.flow_stats.
            Calculate flow speed and Save it.
        """
        body = ev.msg.body
        dpid = ev.msg.datapath.id
        self.stats['flow'][dpid] = body
        self.flow_stats.setdefault(dpid, {})
        self.flow_speed.setdefault(dpid, {})
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match.get('in_port'),
                                             flow.match.get('ipv4_dst'))):
            key = (stat.match['in_port'],  stat.match.get('ipv4_dst'),
                   stat.instructions[0].actions[0].port)
            value = (stat.packet_count, stat.byte_count,
                     stat.duration_sec, stat.duration_nsec)
            self._save_stats(self.flow_stats[dpid], key, value, 5)

            # Get flow's speed.
            pre = 0
            period = 1
            tmp = self.flow_stats[dpid][key]
            if len(tmp) > 1:
                pre = tmp[-2][1]
                period = self._get_period(tmp[-1][2], tmp[-1][3],
                                          tmp[-2][2], tmp[-2][3])

            speed = self._get_speed(self.flow_stats[dpid][key][-1][1],
                                    pre, period)

            self._save_stats(self.flow_speed[dpid], key, speed, 5)
    
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        """
            Save port's stats info
            Calculate port's speed and save it.
        """
        body = ev.msg.body
        dpid = ev.msg.datapath.id
        self.stats['port'][dpid] = body
        self.free_bandwidth.setdefault(dpid, {})

        for stat in sorted(body, key=attrgetter('port_no')):
            port_no = stat.port_no
            if port_no != ofproto_v1_3.OFPP_LOCAL:
                key = (dpid, port_no)
                value = (stat.tx_bytes, stat.rx_bytes, stat.rx_errors,
                         stat.duration_sec, stat.duration_nsec)

                self._save_stats(self.port_stats, key, value, 5)

                # Get port speed.
                pre = 0
                period = 1
                tmp = self.port_stats[key]
                if len(tmp) > 1:
                    pre = tmp[-2][0] + tmp[-2][1]
                    period = self._get_period(tmp[-1][3], tmp[-1][4],
                                              tmp[-2][3], tmp[-2][4])

                speed = self._get_speed(
                    self.port_stats[key][-1][0] + self.port_stats[key][-1][1],
                    pre, period)

                self._save_stats(self.port_speed, key, speed, 5)
                self._save_freebandwidth(dpid, port_no, speed)
    


    def monitor_link(self, s1, s2):
        
        while True:
            self.send_ping_packet(s1, s2)
            hub.sleep(0.1)


    def send_ping_packet(self, s1, s2):
        datapath = self.datapath_list[int(s1.dpid)]
        dst_mac = self.ping_mac
        dst_ip = self.ping_ip
        out_port = s1.port_no
        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

        pkt = packet.Packet()
        pkt.add_protocol(ethernet.ethernet(ethertype=ether_types.ETH_TYPE_IP,
                                           src=self.controller_mac,
                                           dst=dst_mac))
        pkt.add_protocol(ipv4.ipv4(proto=in_proto.IPPROTO_ICMP,
                                   src=self.controller_ip,
                                   dst=dst_ip))
        echo_payload = '%s;%s;%f' % (s1.dpid, s2.dpid, time.time())
        payload = icmp.echo(data=echo_payload)
        pkt.add_protocol(icmp.icmp(data=payload))
        pkt.serialize()

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=datapath.ofproto.OFP_NO_BUFFER,
            data=pkt.data,
            in_port=datapath.ofproto.OFPP_CONTROLLER,
            actions=actions
        )

        datapath.send_msg(out)

    def ping_packet_handler(self, pkt):
        
        
        icmp_packet = pkt.get_protocol(icmp.icmp)
        echo_payload = icmp_packet.data
        payload = echo_payload.data
        info = payload.split(';')
        s1 = info[0]
        s2 = info[1]
        
        latency = (time.time() - float(info[2])) * 1000  # in ms
        if s2 != '0':
            
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(dir_path + "/../../../../tmp/setting.txt","r") as f:
                switchzinho = json.load(f)
            
            
            if int(s1) == int(s1):
                if len(s1) < 3:
                   
                    print("s%s to s%s latency = %f ms" % (s1, s2, latency))
                    payload = {'s1': s1, 's2': s2, 'latency': latency}
                    headers = {'Content-Type': 'application/json'}

                    requests.get('http://127.0.0.1:5000/get_delay', json=payload, headers=headers)
                    
                    
                        #getDelaySwitch.get_delay_switch(s1, s2, latency)
                    self.delay[int(s1)][int(s2)] = latency
                    
            
            f = open(dir_path + "/../../../../tmp/jitter.txt","a+")
            f.write('\n')
            f.write("Switch ")
            f.write(s1)
            f.write(" ")
            f.write(str(latency))
            f.close()
                    
  
    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        # print "Adding flow ", match, actions
        
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id, table_id=3,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority, table_id=3,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def _switch_features_handler(self, ev):
        print("switch_features_handler is called")
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        #esse cara que conversa com o controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):
        """
            Save port description info.
        """
        msg = ev.msg
        dpid = msg.datapath.id
        ofproto = msg.datapath.ofproto

        config_dict = {ofproto.OFPPC_PORT_DOWN: "Down",
                       ofproto.OFPPC_NO_RECV: "No Recv",
                       ofproto.OFPPC_NO_FWD: "No Farward",
                       ofproto.OFPPC_NO_PACKET_IN: "No Packet-in"}

        state_dict = {ofproto.OFPPS_LINK_DOWN: "Down",
                      ofproto.OFPPS_BLOCKED: "Blocked",
                      ofproto.OFPPS_LIVE: "Live"}

        ports = []
        for p in ev.msg.body:
            ports.append('port_no=%d hw_addr=%s name=%s config=0x%08x '
                         'state=0x%08x curr=0x%08x advertised=0x%08x '
                         'supported=0x%08x peer=0x%08x curr_speed=%d '
                         'max_speed=%d' %
                         (p.port_no, p.hw_addr,
                          p.name, p.config,
                          p.state, p.curr, p.advertised,
                          p.supported, p.peer, p.curr_speed,
                          p.max_speed))

            if p.config in config_dict:
                config = config_dict[p.config]
            else:
                config = "up"

            if p.state in state_dict:
                state = state_dict[p.state]
            else:
                state = "up"

            port_feature = (config, state, p.curr_speed)
            self.port_features[dpid][p.port_no] = port_feature
    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        """
            Handle the port status changed event.
        """
        msg = ev.msg
        reason = msg.reason
        port_no = msg.desc.port_no
        dpid = msg.datapath.id
        ofproto = msg.datapath.ofproto

        reason_dict = {ofproto.OFPPR_ADD: "added",
                       ofproto.OFPPR_DELETE: "deleted",
                       ofproto.OFPPR_MODIFY: "modified", }

        if reason in reason_dict:

            print "switch%d: port %s %s" % (dpid, reason_dict[reason], port_no)
        else:
            print "switch%d: Illeagal port state %s %s" % (port_no, reason)
    
    def show_stat(self, type):
        '''
            Show statistics info according to data type.
            type: 'port' 'flow'
        '''
        #if setting.TOSHOW is False:
        #    return

        bodys = self.stats[type]
        #if(type == 'flow'):
        #    print('datapath         ''   in-port        ip-dst      '
        #          'out-port packets  bytes  flow-speed(B/s)')
        #    print('---------------- ''  -------- ----------------- '
        #          '-------- -------- -------- -----------')
        #    for dpid in bodys.keys():
        #        for stat in sorted(
        #            [flow for flow in bodys[dpid] if flow.priority == 1],
        #            key=lambda flow: (flow.match.get('in_port'),
        #                              flow.match.get('ipv4_dst'))):
        #            print('%016x %8x %17s %8x %8d %8d %8.1f' % (
        #                dpid,
        #                stat.match['in_port'], stat.match['ipv4_dst'],
        #                stat.instructions[0].actions[0].port,
        #                stat.packet_count, stat.byte_count,
        #                abs(self.flow_speed[dpid][
        #                    (stat.match.get('in_port'),
        #                    stat.match.get('ipv4_dst'),
        #                    stat.instructions[0].actions[0].port)][-1])))
        #    print '\n'

        if(type == 'port'):
            f = open(dir_path + "/../../../../tmp/throughput.txt","a+")
            f.write('datapath   port   '
                  'port-speed(B/s)'
                  )
            #f.write('----------------   -------- '
            #      '-------- '
            #      '----------------   '
            #      )
            #ESSA PARTE AQUI DEVE FUNCIONAR SOMENTE QUANDO EU DOU UM REQUEST


            format = '%02x   %8x      %8.1f'
            
            
            for dpid in bodys.keys():
                for stat in sorted(bodys[dpid], key=attrgetter('port_no')):
                    if stat.port_no != ofproto_v1_3.OFPP_LOCAL:
                        
                        f.write('\n')
                        f.write(format % (
                            dpid, stat.port_no,
                            abs(self.port_speed[(dpid, stat.port_no)][-1])
                            ))
                f.write('\n') #separa pelos ID's
            f.write('\n')

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        arp_pkt = pkt.get_protocol(arp.arp)
        
        # avoid broadcast from LLDP
        if eth.ethertype == 35020:
            return

        if pkt.get_protocol(ipv6.ipv6):  # Drop the IPV6 Packets.
            match = parser.OFPMatch(eth_type=eth.ethertype)
            actions = []
            self.add_flow(datapath, 1, match, actions)
            return None

        dst = eth.dst
        src = eth.src
        dpid = datapath.id

        if dst == self.ping_mac:
            # ping packet arrives
            self.ping_packet_handler(pkt)
            return

        if src not in self.hosts:
            self.hosts[src] = (dpid, in_port)

        out_port = ofproto.OFPP_FLOOD

        if arp_pkt:
            # print dpid, pkt
            src_ip = arp_pkt.src_ip
            dst_ip = arp_pkt.dst_ip
            if arp_pkt.opcode == arp.ARP_REPLY:
                self.arp_table[src_ip] = src
                h1 = self.hosts[src]
                h2 = self.hosts[dst]
                out_port = self.install_paths(h1[0], h1[1], h2[0], h2[1], src_ip, dst_ip)
                self.install_paths(h2[0], h2[1], h1[0], h1[1], dst_ip, src_ip) # reverse
            elif arp_pkt.opcode == arp.ARP_REQUEST:
                if dst_ip in self.arp_table:
                    self.arp_table[src_ip] = src
                    dst_mac = self.arp_table[dst_ip]
                    h1 = self.hosts[src]
                    h2 = self.hosts[dst_mac]
                    out_port = self.install_paths(h1[0], h1[1], h2[0], h2[1], src_ip, dst_ip)
                    self.install_paths(h2[0], h2[1], h1[0], h1[1], dst_ip, src_ip) # reverse

        #print pkt

        actions = [parser.OFPActionOutput(out_port)]

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
            actions=actions, data=data)
        datapath.send_msg(out)


    @set_ev_cls(event.EventSwitchEnter)
    def switch_enter_handler(self, event):
        switch = event.switch.dp
        ofp_parser = switch.ofproto_parser
    
      
        if switch.id not in self.switches:
            self.switches.append(switch.id)
            self.datapath_list[switch.id] = switch

            # Request port/link descriptions, useful for obtaining bandwidth
            req = ofp_parser.OFPPortDescStatsRequest(switch)
            switch.send_msg(req)

    @set_ev_cls(event.EventSwitchLeave, MAIN_DISPATCHER)
    def switch_leave_handler(self, event):
    
        switch = event.switch.dp.id
        if switch in self.switches:
            del self.switches[switch]
            del self.datapath_list[switch]
            del self.adjacency[switch]
      

    @set_ev_cls(event.EventLinkAdd, MAIN_DISPATCHER)
    def link_add_handler(self, event):
        s1 = event.link.src
        s2 = event.link.dst
        self.adjacency[s1.dpid][s2.dpid] = s1.port_no
        self.adjacency[s2.dpid][s1.dpid] = s2.port_no

       
        switch_list = get_switch(self.topology_api_app, None)   
        switches=[switch.dp.id for switch in switch_list]
        links_list = get_link(self.topology_api_app, None)
        

        links=[(link.src.dpid,link.dst.dpid, link.src.port_no, link.dst.port_no) for link in links_list]

        dir_path = os.path.dirname(os.path.realpath(__file__))
        
        if links:
            if os.path.exists(dir_path + "/../../../../tmp/link_list.txt"):
                os.remove(dir_path + "/../../../../tmp/link_list.txt")

            with open(dir_path + "/../../../../tmp/link_list.txt","w+") as my_links:
                json.dump(sorted(links), my_links)
        
    

        hub.spawn(self.monitor_link, s1, s2)
   
    @set_ev_cls(event.EventLinkDelete, MAIN_DISPATCHER)
    def link_delete_handler(self, event):
        return
