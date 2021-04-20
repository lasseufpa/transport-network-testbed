#use with python3
import shlex, subprocess
#import paramiko
import os

print("Step 1. Install tools")
subprocess.run(['apt-get','-y','install','git','python-pip','python-dev'])

print("Step 2. Install python packages")
subprocess.run([ 'apt-get','-y','install','python-eventlet', 'python-routes','python-webob','python-paramiko'])

print("Step 3. Clone RYU git Repo")
subprocess.run(['git','clone','https://github.com/osrg/ryu.git'])

print("Step 4. Install RYU")
subprocess.run(['pip','install','setuptools','--upgrade'])
subprocess.Popen(['python','./setup.py','install'], cwd='ryu/')

print("Step 5. Install and Update python packages")
subprocess.run(['pip','install','six','--upgrade'])
subprocess.run(['pip','install','oslo.config','msgpack-python'])
subprocess.run(['pip','install','eventlet','--upgrade'])
subprocess.run([ 'pip', 'install', '-r', 'ryu/tools/pip-requires'])

print("Step 6. Test ryu-manager")

process = subprocess.Popen(['ryu-manager','--version'], stdout=subprocess.PIPE)
output = process.communicate()[0]

if process.returncode != 0:
    print("Error with ryu-manager installation...")
else:
    subprocess.run(['cp', 'testbed_analyzer.py', 'ryu/ryu/app/'])
  
print("installation completed, files are in ryu/ryu/app/")

