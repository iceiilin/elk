#!/bin/bash

PID=`ps -c | grep $1 | sed "/grep/d" | sed "/kill_pid_esxi/d" | awk '{print $2}' | sort -r -n`
for i in $PID
do
    #echo "killing process $i ..."
    kill -9 $i
done 
