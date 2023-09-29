# nocmanager
Handle NOC-style setup of arbitrary number of screens with Firefox

Uses [Marionette](https://firefox-source-docs.mozilla.org/testing/marionette/index.html) to control Firefox, and `xset` to control the DPMS state.

Requires
* [Marionette](https://pypi.org/project/marionette-driver/)
* [Firefox](https://www.mozilla.org/en-US/firefox/new/)
* [Paho MQTT client](https://pypi.org/project/paho-mqtt/)
* A linux machine with at least one screen
* A working MQTT server

## Installation

```
pip install marionette_driver
pip install paho.mqtt
```

## Starting

NOCmanager is configured via environment variables

* `MQTT_HOST` IP address or hostname of MQTT host
* `LAYOUT` display layout, in the format <width>x<height>. I have two displays lined up horizontally: `LAYOUT="2x1"`
* `SCREEN` screen size in pixels, for example `SCREEN="1920x1200"`
* `FULLSCREEN` start in fullscreen mode
* `DEBUG` verbose debug output

**Example**

Starting NOCmanager with 2 horizontally arranged displays, 1920x1200 screens, fullscreen mode with debugging, and connect to MQTT server at 192.168.1.2:

```
MQTT_HOST=192.168.1.2 FULLSCREEN=on DEBUG=on LAYOUT="2x1" SCREEN="1920x1200" ./nocmanager.py
```

## MQTT topics

NOCmanager posts state information on the topic `/nocmanager/noc/state` and publishes a LWT on `/nocmanager/noc/lwt`

NOCmanager subscribes to the MQTT topic `/nocmanager/noc/command` for commands. Commands are a JSON formated string:

```
{
  "dpms_state": <boolean>,
  "windows": [ [ <window command screen 1, row 1>, <window command screen 2, row 1>, .... ],
               [ <window command screen 1, row 2>, <window command screen 2, row 2>, .... ],
               [ <window command screen 1, row 3>, <window command screen 2, row 3>, .... ], ...
             ]
}

<boolean> := true|false
<window command> := {
                       "url": <url>,
                       "fullscreen": <boolean>
                    }
```

**Example**

Posting `{"dpms_state": true, "windows": [[{"url": "https://grafana.com/oss/", "fullscreen": true}, {"url": "https://zoneminder.com/", "fullscreen": true}]]}`
to the subject `/nocmanager/noc/command` will switch the DPMS state ON on both displays, load the Grafana web page on display 1, and the Zoneminder web page on
display 2 (in a 2x1 display setup)

## Not implemented

The following features are not implemented
* MQTT authentication
* refreshing of windows
* resizing of windows



