#!/bin/bash

# by Netzint GmbH lukas.spitznagel@netzint.de

SCHOOL=$2

if [ "$SCHOOL" == "" ] || [ "$SCHOOL" == "default-school" ]; then
  for line in $(cat /etc/linuxmuster/sophomorix/default-school/devices.csv); do
    HOSTNAME=$(echo $line | cut -d';' -f2)
    LINBOGROUP=$(echo $line | cut -d';' -f3)
    IMAGE=$(cat /srv/linbo/start.conf.$LINBOGROUP 2>/dev/null | grep "BaseImage" | head -n 1 | awk '{print $3}' | cut -d'.' -f1 )
    MACCT="/srv/linbo/images/$IMAGE/$IMAGE.qcow2.macct"

    if [ "$IMAGE" != "" ]; then
      echo "Now running: setMACCTPWs.py --host ${HOSTNAME} --macct $MACCT"
      /usr/lib/linuxmuster-cachingserver/helper_scripts/setMACCTPWs.py --host ${HOSTNAME} --macct $MACCT
    fi
  done
else
  for line in $(cat /etc/linuxmuster/sophomorix/$SCHOOL/$SCHOOL.devices.csv); do
    HOSTNAME=$(echo $line | cut -d';' -f2)
    LINBOGROUP=$(echo $line | cut -d';' -f3)
    IMAGE=$(cat /srv/linbo/start.conf.$LINBOGROUP 2>/dev/null | grep "BaseImage" | head -n 1 | awk '{print $3}' | cut -d'.' -f1)
    MACCT="/srv/linbo/images/$IMAGE/$IMAGE.qcow2.macct"

    if [ "$IMAGE" != "" ]; then
      echo "Now running: setMACCTPWs.py --host ${SCHOOL}-${HOSTNAME} --macct $MACCT"
      /usr/lib/linuxmuster-cachingserver/helper_scripts/setMACCTPWs.py --host ${SCHOOL}-${HOSTNAME} --macct $MACCT
    fi
  done
fi