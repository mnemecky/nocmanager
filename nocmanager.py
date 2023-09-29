#!/usr/bin/python3

# NOCManager - Handle NOC-style setups with arbitrary number of screens with Firefox
# Copyright (C) 2023 Michael Nemecky
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys
import os
from NOCmanager import NOCManager

# Read env variables
gMQTTHost = os.getenv("MQTT_HOST") or "localhost"
gMQTTPort = os.getenv("MQTT_PORT") or 1883
mqtt_topic_root = os.getenv("MQTT_TOPIC") or "/nocmanager"
mqtt_client = os.getenv("MQTT_CLIENT") or "noc"
mqtt_lwt = os.getenv("MQTT_LWT") or "lwt"
debug = False
if(os.getenv("DEBUG")):
    debug = os.getenv("DEBUG").lower() == "on" or os.getenv("DEBUG").lower() == "true" or False

#
# main routine
#

# LAYOUT: number of screens width X number of screens heigth
layout = os.getenv("LAYOUT") or '1x1'
# SCREEN: screen size in WxH pixels
screensize = os.getenv("SCREEN") or '640x480'

# extract layout from layout parameter
layoutW = int(layout.split('x')[0])
layoutH = int(layout.split('x')[1])
# extract screen size
screen_width = int(screensize.split('x')[0])
screen_heigth = int(screensize.split('x')[1])

# start a firefox instance with marionette enabled
firefox_pid = os.fork()
if firefox_pid == 0:
    os.execlp('firefox','firefox','--marionette')
    sys.exit(0)

fullscreen = False
if(os.getenv("FULLSCREEN")):
    fullscreen = os.getenv("FULLSCREEN").lower() == "on" or os.getenv("FULLSCREEN").lower() == "true" or False

# initialize
nocmanager = NOCManager(layoutW, layoutH, screen_width, screen_heigth, fullscreen, debug)

# connect to MQTT broker
nocmanager.ConnectMQTT(gMQTTHost, gMQTTPort)

# main loop
nocmanager.Loop()

os.kill(firefox_pid)
