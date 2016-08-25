#!/usr/bin/env python
"""
This script is to start or stop RackHD ELK log and performance data collecting tool
"""
# pylint: disable=invalid-name
import json
import argparse
import subprocess
PARSER = argparse.ArgumentParser(description='RackHD ELK log and performance data collect tool')
PARSER.add_argument("-b", "--benchmark", action="store_false", default=True, dest="benchmark",
                    help="Enable benchmark data collecting")
PARSER.add_argument("-l", "--log", action="store_false", default=True, dest="log",
                    help="Enable RackHD log data collecting")
PARSER.add_argument("-e", "--esxtop", action="store_false", default=True, dest="esxtop",
                    help="Enable esxi host performance data collecting")
PARSER.add_argument("-c", "--config", action="store", default="hosts", dest="config",
                    help="Specify configure file, default using hosts in executing folder")
PARSER.add_argument("--start", action="store_true", default=False,
                    help="Start operation flag")
PARSER.add_argument("--stop", action="store_true", default=False,
                    help="Stop operation flag")
PARSER.add_argument("-d", "--duraion", action="store", default=3600, type=int, dest="duration",
                    help="Specify test duration in seconds, default duratio is 3600 seconds")
PARSER.add_argument("-D", "--delay", action="store", default=4, type=int, dest="delay",
                    help="Specify esxtop sampling interval, default 4 seconds")

ARGS_LIST = PARSER.parse_args()
BENCHMARK_FLAG = ARGS_LIST.benchmark
LOG_FLAG = ARGS_LIST.log
ESXTOP_FLAG = ARGS_LIST.esxtop
START_FLAG = ARGS_LIST.start
STOP_FLAG = ARGS_LIST.stop
CONFIG_FILE = ARGS_LIST.config
DURATION = ARGS_LIST.duraion
DELAY = ARGS_LIST.delay

if __name__ == "__main__":
    arg_override = {"benchmark": BENCHMARK_FLAG,
                    "log": LOG_FLAG,
                    "esxtop": ESXTOP_FLAG}
    if START_FLAG:
        count = DURATION / DELAY
        arg_override["delay"] = DELAY
        arg_override["count"] = count
        setup_cmd = "ansible-playbook -i " + CONFIG_FILE + \
            " setup_env.yml --extra-vars " + json.dumps(arg_override)
        subprocess.call(setup_cmd, shell=True)
        start_cmd = "ansible-playbook -i " + CONFIG_FILE + \
            " start.yml --extra-vars " + json.dumps(arg_override)
        subprocess.call(start_cmd, shell=True)
    elif STOP_FLAG:
        stop_cmd = "ansible-playbook -i " + CONFIG_FILE + \
            " start.yml --extra-vars " + json.dumps(arg_override)
        subprocess.call(stop_cmd, shell=True)
    else:
        print "Error: not taks is started"
        print "Please specify if you want to start or stop the job"
