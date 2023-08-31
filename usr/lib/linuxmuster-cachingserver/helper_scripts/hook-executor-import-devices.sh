#!/bin/bash

#########################################################
# 
# by Netzint GmbH 2023
# Lukas Spitznagel (lukas.spitznagel@netzint.de)
# 
#########################################################

echo "Initiating synchronization on satellite-server..."
/usr/bin/linuxmuster-cachingserver sync $@ --items linbo
/usr/bin/linuxmuster-cachingserver sync $@ --items dhcp