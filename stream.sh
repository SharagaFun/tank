#!/bin/sh

DEVICE=/dev/video0
RESOLUTION=640x480
FRAMERATE=25
HTTP_PORT=8001
LOGINPASS="just4:fun"

PLUGINPATH=/usr/local/lib/mjpg-streamer

mjpg_streamer -i "$PLUGINPATH/input_uvc.so -n -d $DEVICE -r $RESOLUTION -f $FRAMERATE" -o "$PLUGINPATH/output_http.so -n -p $HTTP_PORT -w /home/pi/www -c $LOGINPASS"
