#!/bin/bash
for arg in "$@"
do
    echo $arg
    PID=`ps aux | grep $arg | sed "/grep/d" | sed "/kill_pid_linux/d" | awk '{print $2}' | sort -r -n`
    for i in $PID
    do
        #echo "killing process $i ..."
        kill -9 $i
    done 
done
