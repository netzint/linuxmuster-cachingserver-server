#!/bin/bash

#########################################################
# 
# by Netzint GmbH 2023
# Lukas Spitznagel (lukas.spitznagel@netzint.de)
# 
#########################################################

ITEMS="linbo-start-conf,linbo-grub-conf,linuxmuster-devices,dhcp"

echo "Initiating synchronization on satellite-server..."
/usr/bin/linuxmuster-cachingserver sync $@ --items $ITEMS