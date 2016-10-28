#!/bin/bash
for arg in "$@"
do
    
    PID=`ps aux | grep $arg | sed "/grep/d" | sed "/kill_pid_linux/d" | awk '{print $2}' | sort -r -n`
    for i in $PID
    do
        echo "killing process $arg $i ..."
        kill -9 $i
    done 
done
