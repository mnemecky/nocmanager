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

import paho.mqtt.client as MQTT
from marionette_driver.marionette import Marionette
import json
import os
import sys
import time

# class FirefoxHandler
#
# handle Marionette connection to (already running) Firefox instance
#
class FirefoxHandler:

	_debug = False

	# initalize handler class
	def __init__(self, debug=False):

		# window handler list
		self.WindowHandlerList = []

		# debug state
		self._debug = debug

		# initialize layout to default values 1x0, 640x480
		self.layoutWidth = 1
		self.layoutHeight = 0
		self.screenWidth = 640
		self.screenHeight = 480

		# connect to firefox using Marionette
		self.Firefox = Marionette(host='127.0.0.1', port=2828)
		# start firefox session
		self.Firefox.start_session()
		self.Firefox.timeout.page_load = 10

	def __del__(self):
		try:
			for handle in self.WindowHandlerList:
				self.Firefox.switch_to_window(handle)
				self.Firefox.close()
		except:
			pass

	# setup screen layout
	def SetupLayout(self, layoutWidth=1, layoutHeight=1, screenWidth=640, screenHeight=480):
		# initialize layout
		self.layoutWidth = layoutWidth
		self.layoutHeight = layoutHeight
		self.screenWidth = screenWidth
		self.screenHeight = screenHeight

		if self._debug:
			print("class FirefoxHandler.SetupLayout(%d,%d,%d,%d)" % (layoutWidth,layoutHeight,screenWidth,screenHeight))

		x = 0
		while x < layoutWidth:
			y = 0
			tHandlersLine = []
			while y < self.layoutHeight:
				if(x == 0 and y == 0):
					tWindowHandle = self.Firefox.current_window_handle
					self.Firefox.set_window_rect(0,0,screenHeight,screenWidth)
				else:
					tWindowHandle = self.Firefox.open(type='window')['handle']
					try:
						self.Firefox.switch_to_window(tWindowHandle)
						self.Firefox.set_window_rect(x*screenWidth,y*screenHeight,screenHeight,screenWidth)
					except:
						pass
				tHandlersLine.append(tWindowHandle)
				y += 1
			self.WindowHandlerList.append(tHandlersLine)
			x += 1

	# close browser
	# (iterate through all windows, use marionete.close() after select of window)
	def Close(self):
		pass

	# set all windows in fullscreen mode
	def Fullscreen(self):
		if self._debug:
			print("class FirefoxHandler.WindowFullscreen (all)")
		tX = 0
		while tX < self.layoutWidth:
			tY = 0
			while tY < self.layoutHeight:
				try:
					self.Firefox.switch_to_window(self.WindowHandlerList[tX][tY])
					self.Firefox.fullscreen()
				except:
					pass
				tY += 1
			tX += 1

	# set a specified window in fullscreen mode (single string notation)
	def WindowFullscreen(self, window):
		if self._debug:
			print("class FirefoxHandler.WindowFullscreen (%s)" % window)
		try:
			self.Firefox.switch_to_window(self._get_window_handler(window))
			self.Firefox.fullscreen()
		except:
			pass

	# set a specified window in fullscreen mode (X, Y notation)
	def WindowFullscreen(self, x, y):
		if self._debug:
			print("class FirefoxHandler.WindowFullscreen (%d,%d)" % (x,y))
		try:
			self.Firefox.switch_to_window(self._get_window_handler(x,y))
			self.Firefox.fullscreen()
		except:
			pass

	# load an URL in all windows
	def SetURL(self, url):
		if self._debug:
			print("class FirefoxHandler.SetURL (all) to %s" % url)
		tX = 0
		while tX < self.layoutWidth:
			tY = 0
			while tY < self.layoutHeight:
				try:
					self.Firefox.switch_to_window(self.WindowHandlerList[tX][tY])
					self.Firefox.navigate(url)
				except:
					pass
				tY += 1
			tX += 1

	# load an URL in the specified window (single string notation)
	def WindowSetURL(self, window, url):
		if self._debug:
			print("class FirefoxHandler.WindowSetURL (%s) to %s" % (window,url))
		try:
			self.Firefox.switch_to_window(self._get_window_handler(window))
			self.Firefox.navigate(url)
		except:
			pass

	# load an URL in the specified window (X, Y notation)
	def WindowSetURL(self, x, y, url):
		if self._debug:
			print("class FirefoxHandler.WindowSetURL (%d,%d) to %s" % (x,y,url))
		try:
			self.Firefox.switch_to_window(self._get_window_handler(x,y))
			self.Firefox.navigate(url)
			if self._debug:
				print("  done")
		except:
			pass

	# refresh all windows
	def Refresh(self):
		pass

	# refresh specified window
	def Refresh(self, window):
		pass

	# maximize all windows
	def Maximize(self):
		pass

	# maximize the specified window
	def WindowMaximize(self, window):
		pass

	# minimize all windows
	def Minimize(self):
		pass

	# minimize the specified window
	def WindowMinimize(self, window):
		pass

	# set browser orientation for all windows
	# accepts on of the following orientation values: 'portrait', 'landscape'
	def SetOrientation(self, orientation):
		pass

	# set browser orientation for specified window
	# accepts on of the following orientation values: 'portrait', 'landscape'
	def SetOrientation(self, window, orientation):
		pass

	def _get_window_handler(self, window):
		(xnum,ynum) = window.split('_')
		return self.WindowHandlerList[int(xnum)][int(ynum)]

	def _get_window_handler(self, x=0, y=0):
		return self.WindowHandlerList[x][y]


# class NOCManager
#
# handles firefox placement
class NOCManager:

    _debug = False
    _firefox = None
    _mqtt = None
    _layoutWidth = 1
    _layoutHeight = 1
    _screeWidth = 640
    _screenHeight = 480
    _state = {
        'dpms_state': False,
        'windows': [] }

    _mqtt_client = 'nocmanager'

    _mqtt_topic_state = '/nocmanager/noc/state'
    _mqtt_topic_command = '/nocmanager/noc/command'
    _mqtt_topic_lwt = '/nocmanager/noc/lwt'

    def __init__(self, layoutWidth=1, layoutHeight=1, screenWidth=640, screenHeight=480, fullscreen=False, debug=False ):
        self._layoutWidth = layoutWidth
        self._layoutHeight = layoutHeight
        self._screeWidth = screenWidth
        self._screenHeight = screenHeight
        self._debug = debug

        # switch display on
        self._display_control(True)

        # init Marionette
        self._firefox = FirefoxHandler( debug )
        self._firefox.SetupLayout(layoutWidth, layoutHeight, screenWidth, screenHeight )
        if fullscreen:
            self._firefox.Fullscreen()

        # setup state information for windows
        y = 0
        while y < layoutHeight:
            line = []
            x = 0
            while x < layoutWidth:
                line.append( { 'url': '', 'fullscreen': fullscreen } )
                x += 1
            self._state['windows'].append(line)
            y += 1

        # setup MQTT
        self._mqtt = MQTT.Client(self._mqtt_client)
        self._mqtt.connected_flag = False
        self._mqtt.on_connect = self._callback_on_connect
        self._mqtt.on_message = self._callback_on_message
        self._mqtt.will_set(self._mqtt_topic_lwt,"OFF",0,True)


    def __del__(self):
        # cleanup Marionette
        try:
            self._firefox.Close()
        except:
            pass

        # cleanup MQTT
        try:
        	self._mqtt.publish(topic_lwt,"OFF",0,True)
        	self._mqtt.loop_stop()
        	self._mqtt.disconnect()
        except:
        	pass

    def _callback_on_connect(self, client, userdata, flags, result):
        if self._debug:
            print("class NOCManager._callback_on_connect with result %d" % result)
        if result == 0:
            client.connected_flag = True
            client.subscribe(self._mqtt_topic_command)
            client.publish(self._mqtt_topic_lwt, "ON", 0, True)
        else:
            print("MQTT connection failed, error ",rc)

    def _callback_on_message(self, client, userdata, message):
        if self._debug:
            print("class NOCManager._callback_on_message, topic %s, payload %s" % (message.topic, message.payload))
        try:
            commands = json.loads(message.payload)
            for key in commands.keys():
                if key == 'dpms_state':
                    self._display_control(commands[key])
                if key == 'windows':
                    y = 0
                    for line in commands[key]:
                        if y >= self._layoutHeight:
                            break
                        x = 0
                        for window in line:
                            if x >= self._layoutWidth:
                                break
                            if 'url' in window:
                                self._set_window_url(x,y,window['url'])
                            if 'fullscreen' in window:
                                self._set_window_fullscreen(x,y)
                            x += 1
                        y -= 1
        except:
            pass

        self._publish_state()

    def _display_control(self, value):
        if self._debug:
            print("class NOCManager._display_control %r" % value)
        self._state['dpms_state'] = value
        if value:
            os.system('xset dpms force on')
        else:
            os.system('xset dpms force off')

    def _set_window_fullscreen(self, x, y):
        if self._debug:
            print("class NOCManager._set_window_fullscreen (%d,%d)" % (x,y))
        self._firefox.WindowFullscreen(x,y)
        self._state['windows'][y][x]['fullscreen'] = True

    def _set_window_url(self, x, y, url):
        if self._debug:
            print("class NOCManager._set_window_url (%d,%d) to %s" % (x,y,url))
        self._firefox.WindowSetURL(x, y, url)
        self._state['windows'][y][x]['url'] = url

    def _publish_state(self):
        self._mqtt.publish(self._mqtt_topic_state, json.dumps(self._state))

    def ConnectMQTT(self, host, port=1883):
        self._mqtt.loop_start()
        self._mqtt.connect(host, port)

        # MQTT connection loop
        while not self._mqtt.connected_flag:
            time.sleep(10)

    def SetMQTTTopic(self, topic):
        pass

    def Loop(self, delay=60):
        # main loop
        while True:
            self._publish_state()
            time.sleep(delay)