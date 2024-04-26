#!/bin/bash

#########################################################
# 
# by Netzint GmbH 2024
# Lukas Spitznagel (lukas.spitznagel@netzint.de)
# 
#########################################################

SCHOOL=$2

echo "Initiating synchronization on satellite-server..."
/usr/bin/linuxmuster-cachingserver update-config $@
