#ifndef   LEDS_H

  #define   LEDS_H

  #include  <Arduino.h>


  void ledCycleWrapper(void * arg);

  class MyLed {
    public:
      MyLed(uint8_t ledPin);
      bool          stop = false;
      void          begin();
      void          cycle();
      void          blink(float freq, float seconds, float delay);
      void          resetTime();
    private:
      // Common
      uint8_t       pin;
      TaskHandle_t  task;
      // Vars
      uint32_t      msPeriod = 0;
      uint32_t      duration;
      uint32_t      initTime;
      uint32_t      msDelay;
  };

#endif  //#ifndef   LEDS_H