#!/usr/bin/env python
"""
This script is used to auto-generate kibana configure file for esxtop performance charts
"""
import os
import json
import re
import subprocess
import argparse

# pylint: disable=invalid-name
parser = argparse.ArgumentParser(description='kibana config')
parser.add_argument("-t", action="store", default="", help="timestamp used index name")
args_list = parser.parse_args()
timestamp = args_list.t

#EXECUTE_PATH = os.path.split(os.path.realpath(__file__))[0] + "/elk/kibana/"
EXECUTE_PATH = os.path.abspath(os.path.join(os.path.split(os.path.realpath(__file__))[0], os.path.pardir)) + "/elk/kibana/"

index_list = ["benchmark_" + timestamp, "esxtop_" + timestamp, "rackhdlog_" + timestamp]
for index in index_list:
    cmd = "curl -XPUT localhost:9200/.kibana/index-pattern/" + index \
        + " -d '{\"title\": \"" + index + "\"}'"
    subprocess.call(cmd, shell=True)
cmd = "curl localhost:9200/.kibana/config/_search?q=*"
output = subprocess.check_output(cmd, shell=True)
match = re.compile("[\s\S]\"_id\"\:\s*\"(\d.\d.\d)\"[\s\S]", re.I).search(output)
cmd = "curl -XPUT localhost:9200/.kibana/config/" + match.group(1) \
    + " -d '{\"defaultIndex\": \"benchmark_" + timestamp + "\"}'"
subprocess.call(cmd, shell=True)
kibana_files = ["benchmark.kibana", "esxtop.kibana"]
for kibana_configure in kibana_files:
    #f_configure = open(EXECUTE_PATH + kibana_configure, "r")
    #kibana_json_list = json.load(f_configure)
    with open(EXECUTE_PATH + kibana_configure, "r") as f:
        kibana_json_list = json.load(f)
    for json_data in kibana_json_list:
        data = json_data["_source"]
        type_es = json_data["_type"]
        id_es = json_data["_id"]
        del json_data["_type"]
        del json_data["_id"]
        cmd = "curl -XPUT localhost:9200/.kibana/" + type_es + "/" + id_es \
            + " -d " + "'" + json.dumps(data) + "'"
        subprocess.call(cmd, shell=True)
    f.close()
