#use with python3
import shlex, subprocess
import paramiko
import os


class Testbed_Tools():
    def __init__(self):
        print("Using Testbed_Tools...")

    def remote_host_cmd(self, node_ip, node_username, cmd):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
        ssh.connect(node_ip, username=node_username,password='1q2w3e4r', look_for_keys=False, allow_agent=False)

        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
        print(cmd)
        ssh_stdin.flush()
        ssh_stdin.close()
        valor = ssh_stdout.readlines()
        print("Connection Close at {}@{}....".format(node_username, node_ip))

        ssh.close()
    
    def convert_list_into_string(self, list_to_be_changed):
        final_new_string = ""
        for character in list_to_be_changed:
            final_new_string += character
        return final_new_string

    def change_string_value(self, current_host, eth0_ip, veth_ip, host_ip, mininet_host):
        cmd_list = list(eth0_ip)    
        cmd_list[8] = str(current_host)
        cmd_list[11] = str(current_host)
                
        new_eth0_ip = self.convert_list_into_string(cmd_list)

        cmd_list = list(veth_ip)
        cmd_list[8] = str(current_host)
        cmd_list[12] = str(current_host)
                
        new_veth_ip = self.convert_list_into_string(cmd_list)


        cmd_list = list(host_ip)
        cmd_list[7] = str(current_host)
                
        new_host_ip = self.convert_list_into_string(cmd_list)

        cmd_list = list(mininet_host)
        cmd_list[9] = str(current_host)
        new_mininet_host = self.convert_list_into_string(cmd_list)

        return [new_eth0_ip, new_veth_ip, new_host_ip, new_mininet_host]

    def run_cmd_in_bash_window(self, command_string):
        return subprocess.check_output(command_string,
                stdin=None,
                stderr=None,
                shell=True,
                universal_newlines=False).split(b'\n')[0].decode('utf-8')

