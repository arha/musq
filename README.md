# musq

Swiss knife of MQTT. Trigger or log to/from bash scripts, GPIO, SPI/I<sup>2</sup>C or 'smart' plugs/devices from MQTT. MQTT is an IOT protocol supported by pretty much every platform and with some patience, exotic ones too, like Alexa, Tasker or IFTTT.

Easily configurable, modular and easily extendable with either shell scripts or full-on python.

musq is mqtt glue.


## What's supported?
-----------------

The following have been tested:
* RPI v3 model B
* Vanilla x64 debian9
* Raspberry Pi Zero, Unicorn HAT
* Orange PI, GPIO only

## Prerequirements

### Dependencies

```
apt-get install python3-pip
pip3 install paho-mqtt pyyaml
```

Extended stuff (varies depending on what you want)

### 'Smart' devices
```
pip3 install pyHS100 pyw215 
```

### Pimoroni's unicorn hat

```
apt-get install python3-pip python3-dev
pip3 install unicornhat
```

## Installation

Either clone the repo ```git clone https://github.com/arha/musq``` or download the [master zip](https://github.com/arha/musq/archive/master.zip). With the provided config file, sending a message to ```/test/beep-simple``` will call ```/usr/bin/beep``` and messages to ```/test/module/demo/#``` should output some debug data.

Run musq, ```python3 musq``` or simply ```./musq```.

### Messing around

Once that works, setup the logging module (```module: log_file```, needs a ```filename``` and ```topic``` argument) and see what appears. Send a few messages, then configure your own scripts.

The ```pizero``` module loaded on a RPi Zero will publish its internal temperature to ```/example/pizero/temperature```, while writing 1 or 0 to its subscribed topic followed by led (```/this/is/your/topic/led```) will trigger the onboard led.

Orange PIs can have stuff written to ```/example/opi/gpio/action/PG7``` (where action can be read, write, output, pullup), or to /example/opi/led/red (or green) to mess with its leds. The OPi will publish its internal temperature to ```/example/opi/temperature/soc```

# Standalone 'smart' devices

Modern 'smart' consumer IoT devices, like relays (such as D-LINK W215 or TP-Link HS100), or the various assortment of glass/door/PIR sensors require 50-100MB of bad APKs to use; rarely, if ever, have a plain HTTP interface, and usually die when the vendor phases them out/shuts down the server/files for bankruptcy. 

Once you go to the trouble of setting it up, the vendor's APK is useless; hooking the device up to MQTT makes much more sense: access it from anywhere, any OS, any interface and cut the dependency to the manufacturer's ecosystem.

The following devices have musq modules available and have been tested:

* D-LINK W215, via [pyw215](https://github.com/LinuxChristian/pyW215) by LinuxChristian. Needs: one-time setup with their dedicated APK to enter ssid/password (SSID/password cannot be entered by connecting to the device in AP mode); will also need installing the python library `pip3 install pyw215`
* HS-100, via [pyHS100](https://github.com/GadgetReactor/pyHS100) by GadgetReactor. Needs: one time setup from APK; will also need installing the python library `pip3 install pyHS100`

Any 'smart' device that acts as an output can be connected to mqtt via musq if its protocol has been reversed-engineered, and is callable by some sort of script - simply call the script from musq.


Hats and modules supported
--------------------------

* Pimoroni Unicorn HAT (Standard, 8x8) - GPIO

Planned:
--------
* Full RPi v1 and RPI v3
* NanoPi NEO
* Support for hardware libs for peripheral access (I^2C, SPI, serial links...)
* MIDI to MQTT
* Routing (copy messages to/from topics, check for feedback loops)
* Log to file
* Log to databases (MySQL, Postgres, MSSQL, db2) and CouchDB/MongoDB
* DynamoDB, AWS IoT core
* Write to IR or 433/866 MHz RF stuff with dumb dongle (audio out)

Features planned
----------------
* Cross-platform compatible GPIO access
* Cross-platform peripheral access

<!-- Pushed this file to trigger github's activity thingie 2 -->
