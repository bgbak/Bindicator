// Adafruit IO RGB LED Output Example
//
// Adafruit invests time and resources providing this open source code.
// Please support Adafruit and open source hardware by purchasing
// products from Adafruit!
//
// Written by Todd Treece for Adafruit Industries
// Copyright (c) 2016-2017 Adafruit Industries
// Licensed under the MIT license.
//
// All text above must be included in any redistribution.

/************************** Configuration ***********************************/

// edit the config.h tab and enter your Adafruit IO credentials
// and any additional configuration needed for WiFi, cellular,
// or ethernet clients.

#include "config.h"
#include "Adafruit_NeoPixel.h"

#define PIXEL_PIN D2
#define PIXEL_COUNT 2
#define PIXEL_TYPE NEO_GRB + NEO_KHZ800

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(PIXEL_COUNT, PIXEL_PIN, PIXEL_TYPE);

// set up feeds for the two indicators
AdafruitIO_Feed *bin1 = io.feed("bindicator-1");
AdafruitIO_Feed *bin2 = io.feed("bindicator-2");

void initPixels()
{
  // Intialize pixels
  pixels.begin();
  pixels.show();
}

// Handle messages for color 1
void handleBin1(AdafruitIO_Data *data)
{
  Serial.println("Received HEX: ");
  Serial.println(data->value());
  long color = data->toNeoPixel();
  pixels.setPixelColor(0, color);
  pixels.show();
}

// Handle messages for color 2
void handleBin2(AdafruitIO_Data *data)
{
  Serial.println("Received HEX: ");
  Serial.println(data->value());
  long color = data->toNeoPixel();
  pixels.setPixelColor(1, color);
  pixels.show();
}

void setup()
{
  initPixels();

  // start the serial connection
  Serial.begin(115200);

  // connect to io.adafruit.com
  Serial.print("Connecting to Adafruit IO");
  io.connect();

  // set up a message handler for the 'color' feed.
  // the handleMessage function (defined below)
  // will be called whenever a message is
  // received from adafruit io.
  bin1->onMessage(handleBin1);
  bin2->onMessage(handleBin2);

  // wait for a connection
  while (io.status() < AIO_CONNECTED)
  {
    Serial.print(".");
    delay(500);
  }

  // we are connected
  Serial.println();
  Serial.println(io.statusText());
  bin1->get();
  bin2->get();
}

void loop()
{

  // io.run(); is required for all sketches.
  // it should always be present at the top of your loop
  // function. it keeps the client connected to
  // io.adafruit.com, and processes any incoming data.
  io.run();
}