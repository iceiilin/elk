#!/usr/bin/env python
"""

"""
import argparse

PARSER = argparse.ArgumentParser(description='RackHD ELK log and performance data collect tool')
PARSER.add_argument("--benchmark", action="store_false", default=True,
                    help="Enable benchmark data collecting")
PARSER.add_argument("--log", action="store_false", default=True,
                    help="Enable RackHD log data collecting")
PARSER.add_argument("--esxtop", action="store_false", default=True,
                    help="Enable esxi host performance data collecting")
PARSER.add_argument("--config", action="store", default="none",
                    help="Specify configure file")
PARSER.add_argument("-d", action="store", default=3600, type=int,
                    help="Specify test duration in seconds")
ARGS_LIST = PARSER.parse_args()


