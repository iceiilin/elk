#!/usr/bin/env python
"""
This script is used to auto-generate logstash config for rackhd log
"""
import os
import argparse

# pylint: disable=line-too-long, anomalous-backslash-in-string, too-many-locals
PARSER = argparse.ArgumentParser(description='rackhd log logstash configure file generator')
PARSER.add_argument("--path", action="store", default="none", help="Specify log path")
ARGS_LIST = PARSER.parse_args()

log_data_path = ARGS_LIST.path.strip("\n")
if log_data_path[len(log_data_path)-1] == "/":
    log_data_path = log_data_path[0:len(log_data_path)-1]

EXECUTE_PATH = os.path.split(os.path.realpath(__file__))[0] + "/"
f_template = open(EXECUTE_PATH + "log_logstash.template", "r")
f_logstash = open(EXECUTE_PATH + "log.logstash", "w")
for line in f_template.readlines():
    if line.find("path=>") != -1:
        line = line.replace("/tmp/logs/upstart",
                            log_data_path)
    f_logstash.write(line)
f_logstash.close()
f_template.close()
