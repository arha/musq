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

* Dependencies

```
apt-get install python3-pip
pip3 install paho-mqtt pyyaml
```

Extended stuff (varies depending on what you want)
# smart devices
pip3 install pyHS100 pyw215 

# unicorn hat
apt-get install python3-pip python3-dev
pip3 install unicornhat
```

# Standalone 'smart' devices

Modern 'smart' consumer IoT devices, like relays (such as D-LINK W215 or TP-Link HS100), or the various assortment of glass/door/PIR sensors require 50-100MB of bad APKs to use; rarely, if ever, have a plain HTTP interface, and usually die when the vendor phases them out/shuts down the server/files for bankruptcy. 

But if you setup one of these to your local (iot) network, hooking it up to MQTT makes more sense: access it from anywhere, any OS, any interface and cut the dependency to the manufacturer's ecosystem.

The following devices have musq modules available and have been tested:

* D-LINK W215, via [pyw215](https://github.com/LinuxChristian/pyW215) by LinuxChristian. Needs: one-time setup with their dedicated APK to enter ssid/password (SSID/password cannot be entered by connecting to the device in AP mode); will also need installing the python library `pip3 install pyw215`
* HS-100, via [pyHS100](https://github.com/GadgetReactor/pyHS100) by GadgetReactor. Needs: one time setup from APK; will also need installing the python library `pip3 install pyHS100`


Hats and modules supported
--------------------------

* Pimoroni Unicorn HAT (Standard, 8x8) - GPIO

Planned:
--------
* Full RPi v1 and RPI v3
* NanoPi NEO
* Support for hardware libs for peripheral access (I^2C, SPI, serial links...)

Features planned
----------------
* Cross-platform compatible GPIO access
* Cross-platform peripheral access

<!-- Pushed this file to trigger github's activity thingie 2 -->
