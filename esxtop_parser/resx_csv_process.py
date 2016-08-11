#!/usr/bin/env python

import re
import argparse
import subprocess
#import pexpect


parser = argparse.ArgumentParser(description='esxtop csv file parser')
parser.add_argument("-U", action="store", default="none", help="ESXi host username")
parser.add_argument("-P", action="store", default="none", help="ESXi host password")
parser.add_argument("-H", action="store", default="none", help="ESXi host IP address")
parser.add_argument("-n", action="store", default="2500", help="Samples count")
parser.add_argument("-d", action="store", default="20", help="Sampling interval")
parser.add_argument("--nic", action="store", default="none", help="vmnic name")
parser.add_argument("--vm", action="store", default="none", help="Virtual Machine host list")
parser.add_argument("--config", action="store_true", default=False, help="Generate logstash configure flag")
parser.add_argument("--path", action="store", default="", help="Configure file and csv file stored path")

args_list = parser.parse_args()

delay = args_list.d
count = args_list.n
vm_list = args_list.vm.split(",")
nic_list = args_list.nic.split(",")
config_file = args_list.config
username = args_list.U
password = args_list.P
address = args_list.H
path = args_list.path

#system process is default included
vm_list.append("system")

#"""
#cmd_test = "esxtop -b -c rackhd_esxtop60rc -n {} -d {}".format(1, 2)
cmd_test = "resxtop --server {} --username {} -b -n {} -d {} -c {}rackhd_esxtop60rc ".format(address, username, 1, 2, path)
output = subprocess.check_output(cmd_test, shell=True)
output = output.split("\n")[0]

old_heading_list = output.split(",")

patten_list = [
    re.compile(".*PDH-CSV.*UTC.*", re.I),
    #re.compile(".*Memory\\\\Memory Overcommit \(1 Minute Avg\)", re.I),
    re.compile(".*Memory\\\\(Machine|Kernel|NonKernel|Free) MBytes", re.I),
    re.compile(".*Physical Cpu Load\\\\Cpu Load \(1 Minute Avg\)", re.I),
    re.compile(".*Physical Cpu\(_Total\)\\\\\% (Processor|Util|Core Util) Time", re.I),
]

if vm_list[0] != "none":
    #if -v is used, only specified vm will be monitored
    for vm in vm_list:
        cpu_string = ".*Group Cpu\(\d+\:{}\)\\\\\% (Used|Run|System)".format(vm)
        mem_string = ".*Group Memory\(\d+\:{}\)\\\\(Memory|Memory Granted|Memory Consumed|Target) Size MBytes".format(vm)
        patten_list.append(re.compile(cpu_string, re.I))
        patten_list.append(re.compile(mem_string, re.I))
        if nic_list[0] == "none":
            #if -n is not used, nics for all vms will be monitored
            net_string = ".*Network Port\(vSwitch\d+.+\:{}\)\\\\(MBits|Packets) (Transmitted|Received)\/sec".format(vm)
            patten_list.append(re.compile(net_string, re.I))
else:
    #if -v is not used, all vms will be monitored
    cpu_string = ".*Group Cpu\(\d+\:[\w_-]+\)\\\\\% (Used|Run|System)"
    mem_string = ".*Group Memory\(\d+\:[\w_-]+\)\\\\(Memory|Memory Granted|Memory Consumed|Target) Size MBytes"
    patten_list.append(re.compile(cpu_string, re.I))
    patten_list.append(re.compile(mem_string, re.I))
    if nic_list[0] == "none":
        #if -n is not used, all vmnics will be monitored
        net_string = ".*Network Port\(vSwitch\d\:\d+\:vmnic\d{1,2}\)\\\\(MBits|Packets) (Transmitted|Received)\/sec"
        patten_list.append(re.compile(net_string, re.I))

if nic_list[0] != "none":
    #if -n is used, only specified nics will be monitored
    for nic in nic_list:
        net_string = ".*Network Port\(vSwitch\d\:\d+\:{}\)\\\\(MBits|Packets) (Transmitted|Received)\/sec".format(nic)
        patten_list.append(re.compile(net_string, re.I))

target_index_list = []
new_heading_list = []
string_convert_list = []
for (key, data) in enumerate(old_heading_list):
    #print data
    for patten in patten_list:
        if patten.match(data):
            #print data
            target_index_list.append(key+1)
            convert_data = data.replace("\\\\localhost\\", "").replace("\\", "_").replace(" ", "-")
            string_convert_list.append(convert_data + " => \"float\"")
            new_heading_list.append(convert_data.replace("\"", ""))
awk_str = ""
iterate = len(target_index_list)
for i in range(iterate-1):
    awk_str = awk_str + " $" + str(target_index_list[i]) + "\",\""
awk_str = '{\'print' + awk_str + " $" + str(target_index_list[iterate-1]) + '\'}'
cmd_esxtop = "resxtop --server {} --username {} -b -n {} -d {} -c {}rackhd_esxtop60rc " \
             "| grep -v localhost | awk -F \",\" {} > {}esxtop.csv"\
    .format(address, username, count, delay, path, awk_str, path)

if config_file:
    f = open(path + "esxtop.logstash", "w")
    new_heading_list[0] = "_timestamp"
    del string_convert_list[0]
    converting_list = "\n            ".join(string_convert_list)
    headings = str(new_heading_list)
    logstash_string = \
        'input {\n' \
        '    file {\n' \
        '        path => ["/tmp/esxtop.csv"]\n' \
        '        start_position => "beginning"\n' \
        '        ignore_older => 0\n' \
        '        sincedb_path => "/dev/null"\n' \
        '    }\n' \
        '}\n' \
        '\n' \
        'filter {\n' \
        '    csv {\n' \
        '        columns => ' + headings + '\n' \
        '        separator => ","\n' \
        '        convert => {\n            ' + converting_list + '}\n' \
        '    }\n' \
        '    date {\n' \
        '        locale => "en"\n' \
        '        timezone => "Europe/Paris"\n' \
        '        match => [ "_timestamp", "MM/dd/yyyy HH:mm:ss" ]\n' \
        '        target => ["timestamp"]\n' \
        '        remove_field => ["_timestamp"]\n' \
        '    }\n' \
        '}\n' \
        '\n' \
        'output{\n' \
        '    elasticsearch\n' \
        '    {\n' \
        '       hosts => ["localhost:9200"]\n' \
        '       codec => "json"\n' \
        '       index => "esxtop"\n' \
        '    }\n' \
        '}'
    f.write(logstash_string)
    f.close()


subprocess.call(cmd_esxtop, shell=True)
