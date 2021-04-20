import shlex, subprocess
import paramiko
import os
import time

sudo tc qdisc change dev s1-eth3 handle 10: netem delay 100ms


def post_delay_switch(switch, iface_port, delay):
    subprocess.run(['sudo', 'tc','qdisc','change','dev',
    's{}-eth{}'.format(int(switch), int(iface_port)), 'netem', 'delay', '100ms'])