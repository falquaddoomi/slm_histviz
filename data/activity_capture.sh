#!/bin/bash

TAG=$1

if [ -z "$TAG" ]; then
  echo "ERROR: must specify tag for log as first argument"
  exit -1
fi

adb logcat -b events -c
# adb logcat -v threadtime -b events | egrep 'am_focused_activity|am_resume_activity|screen_toggled'

adb logcat -v threadtime -b events > "logs/${TAG}_$( date +%k:%M_%d-%m-%y ).log"
