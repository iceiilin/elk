#!/usr/bin/env python
"""
This script implemented 3 functions:
    1. Collect esxtop performance data
    2. Generate logstash configure file
    3. Generate kibana configure file
"""
import re
import os
import argparse
import subprocess
import elkconf_generator as generator

# pylint: disable=invalid-name, anomalous-backslash-in-string, line-too-long, anomalous-unicode-escape-in-string
parser = argparse.ArgumentParser(description='esxtop csv file parser')
parser.add_argument("-d", action="store", default="20", help="Samples interval")
parser.add_argument("-n", action="store", default="2500", type=int, help="Samples count")
parser.add_argument("-c", action="store", default="rackhd_esxtop60rc",
                    help="Specify esxtop configure file")
parser.add_argument("--suffix", action="store", default="",
                    help="name suffix to build store for the data collection")
parser.add_argument("--logpath", action="store", default="/home/onrack/elk/log",
                    help="Path for esxtop data log")
parser.add_argument("--nic", action="store", default="none", help="vmnic name")
parser.add_argument("--vm", action="store", default="none", help="Virtual Machine host list")
parser.add_argument("--entity", action="store", default="none", help="Specify entity file")
parser.add_argument("--logstash", action="store", default="esxtop.logstash",
                    help="Generate logstash configure flag")
parser.add_argument("--kibana", action="store", default="esxtop_kibana.template",
                    help="Generate kibana configure flag")

#parser.add_argument("--path", action="store", default="\\tmp\\", help="csv file path")
args_list = parser.parse_args()

execute_path = os.path.split(os.path.realpath(__file__))[0] + "/"

delay = args_list.d
count = args_list.n
suffix = args_list.suffix
log_path = args_list.logpath
vm_list = args_list.vm.split(",")
nic_list = args_list.nic.split(",")
entity_config = args_list.entity
LOGSTASH_CONFIG_FILE = execute_path + "esxtop" + suffix + ".logstash"
ESXTOP_CONFIG_FILE = execute_path + args_list.c
KIBANA_CONFIG_TEMPLATE = execute_path + args_list.kibana
KIBANA_CONFIG_FILE = execute_path + "esxtop" + suffix + ".kibana"

OLD_ENTITY_FILE = execute_path + "rackhd_esxtop.entity.origin"
ENTITY_FILE = execute_path + "rackhd_esxtop.entity" if (entity_config == "none") else execute_path + entity_config

all_vm_list = []
all_nic_list = []
###########################################################################
##This portion is to edit esxtop entity to reduce esxtop output size
###########################################################################
if entity_config == "none":
    cmd_entity = "esxtop --export-entity " + OLD_ENTITY_FILE
    subprocess.call(cmd_entity, shell=True)
    f_old_entity = open(OLD_ENTITY_FILE, "r")
    f_new_entity = open(ENTITY_FILE, "w")
    ## flag=1,2,3,4,5 stands for SchedGroup, Adapter, Device, NetPort, InterruptCookie respectively
    flag = 0
    ## Process "helper", "drivers", "ft" and "vmotion" will be dropped, "system" and "idle" is kept
    process_anti_patten = re.compile("\d+ ([A-Za-z\-\_]+\.\d+|helper|drivers|ft|vmotion|system|idle)", re.I)
    network_anti_patten = re.compile("\d+ (Management|Shadow .+|vmk\d+)", re.I)
    for line in f_old_entity.readlines():
        stripped_line = line.replace("\n", "")
        if stripped_line in ["SchedGroup", "Adapter", "Device", "NetPort", "InterruptCookie"]:
            flag += 1
            if flag == 1 or flag == 4:
                f_new_entity.write(line)
        elif flag == 1 and not process_anti_patten.match(stripped_line):
            f_new_entity.write(line)
            all_vm_list.append(stripped_line)
        elif flag == 4 and not network_anti_patten.match(stripped_line):
            f_new_entity.write(line)
            all_nic_list.append(stripped_line)
    f_old_entity.close()
    f_new_entity.close()
    os.remove(OLD_ENTITY_FILE)


###########################################################################
##This portion is to filter necessary headings of ESXi performance
##For each heading description, please refer to https://communities.vmware.com/docs/DOC-9279
###########################################################################
cmd_test = "esxtop --import-entity {} -b -n {} -d {} -c {}".format(ENTITY_FILE, 1, 2, ESXTOP_CONFIG_FILE)
output = subprocess.check_output(cmd_test, shell=True)
output = output.split("\n")[0]

old_heading_list = output.split(",")

############################host cpu and memory############################
patten_list = [
    re.compile(".*PDH-CSV.*UTC.*", re.I),
    re.compile(".*Memory\\\\Memory Overcommit \((1|5|10) Minute Avg\)", re.I),
    #re.compile(".*Memory\\\\(Machine|Kernel|NonKernel|Free) MBytes", re.I),
    #re.compile(".*\\\\Memory\\\\.*MBytes", re.I),
    re.compile(".*Physical Cpu Load\\\\Cpu Load \((1|5) Minute Avg\)", re.I),
    re.compile(".*Physical Cpu\(_Total\)\\\\\% (Processor|Util|Core Util) Time", re.I),
]

########################VM cpu, memory and network##########################
## if --vm is used, only specified vms will be monitored
if vm_list[0] != "none":
    for vm in vm_list:
        """
        #######################Filtered Memory items for VM##########################
        "\\localhost\Group Memory(19299:Krein)\Memory Size MBytes"
        "\\localhost\Group Memory(19299:Krein)\Memory Granted Size MBytes"
        "\\localhost\Group Memory(19299:Krein)\Memory Consumed Size MBytes"
        "\\localhost\Group Memory(19299:Krein)\Target Size MBytes"
        "\\localhost\Group Memory(19299:Krein)\Touched MBytes"
        "\\localhost\Group Memory(19299:Krein)\Touched Write MBytes"
        "\\localhost\Group Memory(19299:Krein)\% Active Estimate"
        "\\localhost\Group Memory(19299:Krein)\% Active Slow Estimate"
        "\\localhost\Group Memory(19299:Krein)\% Active Fast Estimate"
        "\\localhost\Group Memory(19299:Krein)\% Active Next Estimate"
        #######################Filtered CPU items for VM#############################
        "\\localhost\Group Cpu(28868:Ted_DEV_ORA)\% Used"
        "\\localhost\Group Cpu(28868:Ted_DEV_ORA)\% Run"
        "\\localhost\Group Cpu(28868:Ted_DEV_ORA)\% System"
        "\\localhost\Group Cpu(28868:Ted_DEV_ORA)\% Wait"
        "\\localhost\Group Cpu(28868:Ted_DEV_ORA)\% VmWait"
        "\\localhost\Group Cpu(28868:Ted_DEV_ORA)\% Ready"
        "\\localhost\Group Cpu(28868:Ted_DEV_ORA)\% Idle"
        "\\localhost\Group Cpu(28868:Ted_DEV_ORA)\% Overlap"
        "\\localhost\Group Cpu(28868:Ted_DEV_ORA)\% CoStop"
        "\\localhost\Group Cpu(28868:Ted_DEV_ORA)\% Max Limited"
        "\\localhost\Group Cpu(28868:Ted_DEV_ORA)\% Swap Wait"
        #######################Filtered network items for vm#########################
        "\\localhost\Network Port(vSwitch6:134217729:Management)\MBits Transmitted/sec"
        "\\localhost\Network Port(vSwitch6:134217729:Management)\MBits Received/sec"
        "\\localhost\Network Port(vSwitch6:134217730:36139:Krein)\MBits Transmitted/sec"
        "\\localhost\Network Port(vSwitch6:134217730:36139:Krein)\MBits Received/sec"
        "\\localhost\Network Port(vSwitch6:134217731:506106:quanta_t41)\MBits Transmitted/sec"
        "\\localhost\Network Port(vSwitch6:134217731:506106:quanta_t41)\MBits Received/sec"
        """
        #cpu_string = ".*Group Cpu\(\d+\:{}\)\\\\\% (Used|Run|System|Wait|Ready|Idle)".format(vm)
        cpu_string = ".*Group Cpu\(\d+\:{}\)\\\\\% (Used)".format(vm)
        mem_string = ".*Group Memory\(\d+\:{}\)\\\\(Touched MBytes|Memory Consumed Size MBytes)".format(vm)
        patten_list.append(re.compile(cpu_string, re.I))
        patten_list.append(re.compile(mem_string, re.I))
        if nic_list[0] == "none":
            #if -n is not used, nics for all vms will be monitored
            #net_string = ".*Network Port\(vSwitch\d+.+\:{}\)\\\\(MBits|Packets) (Transmitted|Received)\/sec".format(vm)
            net_string = ".*Network Port\(vSwitch\d+.+\:{}\)\\\\MBits (Transmitted|Received)\/sec".format(vm)
            patten_list.append(re.compile(net_string, re.I))
#if --vm is not used, all vms will be monitored
else:
    cpu_string = ".*Group Cpu\(\d+\:[\w_-]+\)\\\\\% (Used)"
    #mem_string = ".*Group Memory\(\d+\:[\w_-]+\)\\\\(Memory|Memory Granted|Memory Consumed|Target) Size MBytes"
    mem_string = ".*Group Memory\(\d+\:[\w_-]+\)\\\\(Touched MBytes|Memory Consumed Size MBytes)"
    patten_list.append(re.compile(cpu_string, re.I))
    patten_list.append(re.compile(mem_string, re.I))
    #if -n is not used, all phsical vmnics and VM vmnics will be monitored
    if nic_list[0] == "none":
        net_string = ".*Network Port\(vSwitch\d{1,2}\:.+(?!Management)\)\\\\MBits (Transmitted|Received)\/sec"
        patten_list.append(re.compile(net_string, re.I))

#if --nic is used, only specified nics will be monitored
if nic_list[0] != "none":
    for nic in nic_list:
        net_string = ".*Network Port\(vSwitch\d\:\d+\:{}\)\\\\MBits (Transmitted|Received)\/sec".format(nic)
        patten_list.append(re.compile(net_string, re.I))

target_index_list = []
target_heading_list = []
string_convert_list = []
for (key, data) in enumerate(old_heading_list):
    #print data
    for patten in patten_list:
        if patten.match(data):
            #print data
            target_index_list.append(key+1)
            #convert_data = data.replace("\\\\.+\\?", "").replace("\\", "_").replace(" ", "-").replace(".", "_")
            convert_data = data.replace("\\", "_").replace(" ", "-").replace(".", "_").replace("__", "")
            #convert_data = "_".join(data.split("\\")[3:]).replace(" ", "-").replace(".", "_")
            string_convert_list.append(convert_data + " => \"float\"")
            target_heading_list.append(convert_data.replace("\"", ""))

###########################################################################
## This portion is to create awk script
## to filter necessary data according headings
###########################################################################
awk_str = ""
iterate = len(target_index_list)
for i in range(iterate-1):
    awk_str = awk_str + " $" + str(target_index_list[i]) + "\",\""
awk_str = '{\'print' + awk_str + " $" + str(target_index_list[iterate-1]) + '\'}'
cmd_esxtop = "esxtop --import-entity {} -b -n {} -d {} -c {}" \
             "| grep -v CSV | awk -F \",\" {} > {}rackhd_esxtop{}.csv"\
    .format(ENTITY_FILE, str(count), delay, ESXTOP_CONFIG_FILE, awk_str, execute_path, suffix)

###########################################################################
## This portion is to generate logstash and kibana configure file
###########################################################################
generator.create_logstash(target_heading_list, string_convert_list, LOGSTASH_CONFIG_FILE, log_path, suffix)
generator.create_kibana(target_heading_list, KIBANA_CONFIG_TEMPLATE, KIBANA_CONFIG_FILE, suffix)

###########################################################################
## This portion is to add retry mechanism
###########################################################################
i = 0
while i < 10:
    subprocess.call(cmd_esxtop, shell=True)
    f = open(execute_path + "rackhd_esxtop" + suffix + ".csv", "rU")
    line_count = 0
    for line in f:
        line_count += 1
    if line_count < count:
        old_count = count
        count = count - line_count
        cmd_esxtop = cmd_esxtop.replace("-n " + str(old_count), "-n " + str(count)).replace(">", ">>")
        i += 1
    else:
        break
