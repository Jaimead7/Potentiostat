#include  "Leds.h"

#if defined(ARDUINO_ESP32_DEV)

  void ledCycleWrapper(void * arg) {
    /*
    Wrapper for the cycle call form xTaskCreate.
    */
    MyLed* led = static_cast<MyLed*>(arg);
    led->cycle();
  }

  MyLed::MyLed(uint8_t ledPin) {
    pin = ledPin;
  }

  void MyLed::begin() {
    pinMode(pin, OUTPUT);
    String taskName = "myLed-" + String(pin);
    xTaskCreate(ledCycleWrapper, taskName.c_str(), 4092, this, 2, &task);
  }

  void MyLed::cycle() {
    vTaskSuspend(task);
    while (true) {
      delay(msDelay);
      stop = false;
      while (millis() - initTime < duration && !stop) {
        digitalWrite(pin, HIGH);
        delay(msPeriod);
        digitalWrite(pin, LOW);
        delay(msPeriod);
      }
      stop = false;
      digitalWrite(pin, LOW);
      vTaskSuspend(task);
    }
  }

  void MyLed::blink(float freq, float seconds, float delay) {
    if (freq <= 0) {
      msPeriod = uint32_t(0);
    } else {
      msPeriod = uint32_t(((1. / freq) / 2.) * 1000.);
    }
    duration = seconds * 1000.;
    msDelay = delay * 1000.;
    resetTime();
    vTaskResume(task);
  }

  void MyLed::resetTime() {
    initTime = millis();
  }

#endif  //#if defined(ARDUINO_ESP32_DEV)