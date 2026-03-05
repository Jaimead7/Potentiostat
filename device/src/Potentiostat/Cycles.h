#ifndef   CYCLES_H

  #define   CYCLES_H

  #include  "Commands.h"
  #include  "Board.h"
  #include  "Circuit.h"
  #include  "Leds.h"


  void ptCycleWrapper(void* arg);

  class Potentiometry {
    public:
      Potentiometry(Circuit &circuit, MyLed &greenLed, MyLed &yellowLed, MyLed &redLed);
      void          begin();
      void          cycle();
      void          processCmd(String &cmd);
    private:
      // Common
      Circuit*      pCircuit;
      MyLed*        gLed;
      MyLed*        yLed;
      MyLed*        rLed;
      TaskHandle_t  task;
      uint32_t      taskDelay =       50;               // ms
      bool          stop =            false;
      float         redLimit =        50;               // uA
      float         yellowLimit =     25;               // uA
      // Params
      float         voltageSP =       0.6;              // V
      uint32_t      duration =        120000;           // ms
      float         startThreshold =  50.;              // uA
      // Vars
      uint32_t      initTime;
      // Func
      void          start();
      void          ledsResult();
  };


  void cvCycleWrapper(void* arg);

  class CyclicVoltammetry {
    public:
      CyclicVoltammetry(Circuit &myCircuit, MyLed &greenLed, MyLed &yellowLed, MyLed &redLed);
      void          begin();
      void          cycle();
      void          processCmd(String &cmd);
    private:
      // Common
      Circuit*      pCircuit;
      MyLed*        gLed;
      MyLed*        yLed;
      MyLed*        rLed;
      TaskHandle_t  task;
      uint32_t      taskDelay =       50;               // ms
      bool          stop =            false;
      float         redLimit =        50;               // uA
      float         yellowLimit =     25;               // uA
      // Params
      float         slewRate =        100.0;            // mV/s
      uint8_t       totalCycles =     1;
      float         startVoltage =    -0.5;             // V
      float         stopVoltage =     -0.5;             // V
      float         peakVoltage =     0.9;              // V
      // Vars
      uint8_t       currentCycle =    0;
      float         currentVoltage =  0.0;              // V
      int8_t        direction =       1;                // 1 positive slewRate, -1 negative slewRate
      uint32_t      lastVoltChange;
      // Func
      void          start();
      void          ledsResult();
      void          changeVoltage();
  };


  void swvCycleWrapper(void* arg);

  class SquareWaveVoltammetry {
    public:
      SquareWaveVoltammetry(Circuit &myCircuit, MyLed &greenLed, MyLed &yellowLed, MyLed &redLed);
      void          begin();
      void          cycle();
      void          processCmd(String &cmd);
    private:
      // Common
      Circuit*      pCircuit;
      MyLed*        gLed;
      MyLed*        yLed;
      MyLed*        rLed;
      TaskHandle_t  task;
      uint32_t      taskDelay =       50;               // ms
      bool          stop =            false;
      float         redLimit =        50;               // uA
      float         yellowLimit =     25;               // uA
      // Params
      float         startVoltage =    -0.2;             // V
      float         stopVoltage =     1.0;              // V
      float         stepSize =        0.005;            // V
      float         pulseAmplitude =  0.05;             // V
      float         frequency =       2.0;              // Hz
      float         maxCurrent =      1000.0;           // uA
      float         equilTime =       5000;             // ms
      // Vars
      float         currentVoltage =  0.0;              // V
      float         vStair =          0.0;              // V
      float         vPulse =          0.0;              // V
      float         vFordward =       0.0;              // V
      float         iFordward =       0.0;              // uA
      float         vReverse =        0.0;              // V
      float         iReverse =        0.0;              // uA
      uint32_t      initTime;
      // Func
      void          start();
      void          ledsResult();
      void          changeVoltage();
      bool          checkEnd();
      void          transmit();
  };

#endif  //#ifndef   CYCLES_H
