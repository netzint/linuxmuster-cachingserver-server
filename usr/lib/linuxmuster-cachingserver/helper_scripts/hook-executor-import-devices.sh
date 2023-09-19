#!/bin/bash

#########################################################
# 
# by Netzint GmbH 2023
# Lukas Spitznagel (lukas.spitznagel@netzint.de)
# 
#########################################################

SCHOOL=$2

if [ "$SCHOOL" == "" ] || [ "$SCHOOL" == "default-school" ]; then
  echo "Nothing to do at default-school"
else
  echo "Initiating synchronization on satellite-server..."
  /usr/bin/linuxmuster-cachingserver sync $@ --item linbo
  /usr/bin/linuxmuster-cachingserver sync $@ --item dhcp
fi
