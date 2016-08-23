#!/usr/bin/env python
"""
This script is used to auto-generate kibana configure file for esxtop performance charts
"""
import os
import argparse

# pylint: disable=line-too-long, anomalous-backslash-in-string, too-many-locals
PARSER = argparse.ArgumentParser(description='esxtop csv file parser')
PARSER.add_argument("--path", action="store", default="none", help="Specify benchmark data path")
ARGS_LIST = PARSER.parse_args()

benchmark_data_path = ARGS_LIST.path
if benchmark_data_path[len(benchmark_data_path)-1] == "/":
    benchmark_data_path = benchmark_data_path[0:len(benchmark_data_path)-1]

EXECUTE_PATH = os.path.split(os.path.realpath(__file__))[0] + "/"
f_template = open(EXECUTE_PATH + "benchmark_logstash.template", "r")
f_logstash = open(EXECUTE_PATH + "benchmark.logstash", "a")
for line in f_template.readlines():
    if line.find("path =>") != -1:
        line = line.replace("/home/onrack/_src/benchmark/20160725-001442",
                            benchmark_data_path)
    f_logstash.write(line)
f_logstash.close()
f_template.close()
