#!/usr/bin/env python
"""
This script is to start or stop RackHD ELK log and performance data collecting tool
"""
# pylint: disable=invalid-name
import os
import json
import argparse
import subprocess
import time
import shutil

PARSER = argparse.ArgumentParser(description='RackHD ELK log and performance data collect tool')
PARSER.add_argument("-b", "--benchmark", action="store_false", default=True, dest="benchmark",
                    help="Disable benchmark data collecting")
PARSER.add_argument("-l", "--log", action="store_false", default=True, dest="log",
                    help="Disable RackHD log data collecting")
PARSER.add_argument("-e", "--esxtop", action="store_false", default=True, dest="esxtop",
                    help="Disable esxi host performance data collecting")
PARSER.add_argument("-c", "--config", action="store", default="hosts", dest="config",
                    help="Specify ansible inventory file, default using hosts in executing folder")
PARSER.add_argument("--start", action="store_true", default=False,
                    help="Start operation flag")
PARSER.add_argument("--stop", action="store_true", default=False,
                    help="Stop operation flag")
PARSER.add_argument("-d", "--duration", action="store", default=200, type=int, dest="duration",
                    help="Specify esxtop duration in seconds, default duratio is 36000 seconds")
PARSER.add_argument("-D", "--delay", action="store", default=4, type=int, dest="delay",
                    help="Specify esxtop sampling interval, default 4 seconds")
PARSER.add_argument("-k", "--kill", action="store_true", default=False, dest="kill",
                    help="Flag to kill ELK")
PARSER.add_argument("-C", "--clear", action="store_true", default=False, dest="clear",
                    help="Flag to clear elasticsearch data")
PARSER.add_argument("-i", "--infinite", action="store_true", default=False, dest="infinite",
                    help="Flag to run test infinitely until manually stop")


ARGS_LIST = PARSER.parse_args()
BENCHMARK_FLAG = ARGS_LIST.benchmark
LOG_FLAG = ARGS_LIST.log
ESXTOP_FLAG = ARGS_LIST.esxtop
START_FLAG = ARGS_LIST.start
STOP_FLAG = ARGS_LIST.stop
CONFIG_FILE = ARGS_LIST.config
DURATION = ARGS_LIST.duration
DELAY = ARGS_LIST.delay
KILL = ARGS_LIST.kill
CLEAR = ARGS_LIST.clear
INFINITE = ARGS_LIST.infinite

if __name__ == "__main__":
    if os.path.exists("/opt/config/hosts"):
        shutil.copy("/opt/config/hosts", "/opt/rackhd_elk/hosts")
    arg_override = {"benchmark": BENCHMARK_FLAG,
                    "log": LOG_FLAG,
                    "esxtop": ESXTOP_FLAG}
    stop_cmd = "ansible-playbook -i " + CONFIG_FILE + \
        " stop.yml --extra-vars '" + json.dumps(arg_override) + "'"
    if CLEAR:
        subprocess.call("curl -XDELETE localhost:9200/_all | python -mjson.tool", shell=True)
    if KILL:
        subprocess.call("sudo ./files/kill_pid_linux.sh cli elasticsearch logstash", shell=True)
    if START_FLAG:
        count = DURATION / DELAY
        arg_override["delay"] = DELAY
        arg_override["count"] = count
        setup_cmd = "ansible-playbook -i " + CONFIG_FILE + \
            " setup_env.yml --extra-vars '" + json.dumps(arg_override) + "'"
        subprocess.call(setup_cmd, shell=True)
        start_cmd = "ansible-playbook -i " + CONFIG_FILE + \
            " start.yml --extra-vars '" + json.dumps(arg_override) + "'"
        subprocess.call(start_cmd, shell=True)
        if not INFINITE:
            print "Sleep for {} seconds ... ".format(DURATION)
            time.sleep(DURATION)
            subprocess.call(stop_cmd, shell=True)
    elif STOP_FLAG:
        subprocess.call(stop_cmd, shell=True)
    else:
        print "Error: no task is started"
        print "Please specify if you want to start or stop the job"

    while True:
        pass
