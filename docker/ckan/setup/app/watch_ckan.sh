#!/bin/sh

if [ ! -d "$1" ];
then
  echo "$1 is not a directory";
  exit;
else
  export WATCH_DIR=$1
fi

while true; 
do   
  inotifywait -e modify -e move -e create -e delete -e attrib -r $WATCH_DIR; 
  killall -HUP python; 
done;
