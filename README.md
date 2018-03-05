musq
====

Run scripts and toggle GPIO on Raspberry PI (clones, and various SBC boards) by MQTT subscriptions. You can either subscribe shell scripts to topics or write python3 modules using your favourite libs.

musq is mqtt glue.


What's supported?
-----------------

The following have been tested:
* RPI v3 model B
* Vanilla x64 debian9
* Raspberry Pi Zero, Unicorn HAT
* Orange PI, GPIO only

Standalone 'smart' devices
--------------------------

Modern 'smart' consumer IoT devices, like relays (such as D-LINK W215 or TP-Link HS100), or the various assortment of glass/door/PIR sensors require 50-100MB of bad APKs to use; rarely, if ever, have a plain HTTP interface, and usually die when the vendor phases them out/shuts down the server/files for bankruptcy. 

But if you setup one of these to your local (iot) network, hooking it up to MQTT makes more sense: access it from anywhere, any OS, any interface and cut the dependency to the manufacturer's ecosystem.

The following devices have musq modules available and have been tested:

* D-LINK W215, via [pyw215](https://github.com/LinuxChristian/pyW215). Needs: one-time setup with their dedicated apk to enter ssid/password (SSID/password cannot be entered by connecting to the device in AP mode)


Hats and modules supported
--------------------------

* Pimoroni Unicorn HAT (Standard, 8x8) - GPIO

Planned:
--------
* Full RPi v1 and RPI v3
* NanoPi NEO
* Support for hardware libs for peripheral access (I^2C, SPI, serial links...)
* TP-LINK HS-100

Features planned
----------------
* Cross-platform compatible GPIO access
* Cross-platform peripheral access

<!-- Pushed this file to trigger github's activity thingie 2 -->
