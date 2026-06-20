#!/bin/bash


##################

# Author: Sundar
# Date: 06/06/2026
#
# This script outputs the node health. 
#
# Version: v1

##################

set -x # debug mode

df -h

free -g

nproc

ps -ef | grep "amazon" | awk -F " " '{print $2}'
