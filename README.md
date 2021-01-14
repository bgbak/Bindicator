# Bindicator
Indicator for trash pickup. Utilizes Neopixels, an mqtt broker, esp8266, and a 3D printed model of a wheeliebin

## Hardware
* Wemos D1 Mini
* RGB Wheeliebin Reminder Lamp - https://www.thingiverse.com/thing:4097960
* WS2812 or NeoPixel compatible RGB Strip with 2 LEDs.

## Setup
Register for [Adafruit IO](https://io.adafruit.com).
Create feeds bindicator-1 and bindicator-2.
Pupulate src/config.h with your settings.
  * Adafruit IO User
  * Adafruit IO Key
  * WiFi SSID
  * WiFi Password
Flash the Wemos.
Solder D2 on the Wemos to Data In on the strip, 5v to 5v and GND to GND.
Assemble and enjoy.
