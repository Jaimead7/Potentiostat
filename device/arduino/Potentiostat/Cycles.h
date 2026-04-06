#include  "Commands.h"
#include  "Board.h"
#include  "Circuit.h"


class Potentiometry {
  public:
    Potentiometry(Circuit &myCircuit);
    bool        run =             false;
    void        cycle();
    void        processCmd(String &cmd);
  private:
    // Common
    Circuit*    pCircuit;
    uint32_t    taskDelay =       50;               // ms
    bool        started =         false;
    float       redLimit =        50;               // uA
    float       yellowLimit =     25;               // uA
    // Params
    float       voltageSP =       0.6;              // V
    uint32_t    duration =        120000;           // ms
    float       startThreshold =  50.;
    // Vars
    uint32_t    initTime;
    uint32_t    lastRead;
    // Func
    void        checkStart();
    void        ledsResult();
};


class CyclicVoltammetry {
  public:
    CyclicVoltammetry(Circuit &myCircuit);
    bool        run =             false;
    void        cycle();
    void        processCmd(String &cmd);
  private:
    // Common
    Circuit*    pCircuit;
    uint32_t    taskDelay =       50;               // ms
    bool        started =         false;
    float       redLimit =        50;               // uA
    float       yellowLimit =     25;               // uA
    // Params
    float       slewRate =        100.0;            // mV/s
    uint8_t     totalCycles =     1;
    float       startVoltage =    -0.5;             // V
    float       stopVoltage =     -0.5;             // V
    float       peakVoltage =     0.9;              // V
    // Vars
    uint8_t     currentCycle =    0;
    float       currentVoltage =  0.0;
    int8_t      direction =       1;                // 1 positive slewRate, -1 negative slewRate
    uint32_t    lastVoltChange;
    // Func
    void        setStartConditions();
    void        ledsResult();
    void        checkEnd();
    void        changeVoltage();
};

class SquareWaveVoltammetry {
  public:
    SquareWaveVoltammetry(Circuit &myCircuit);
    bool        run =             false;
    void        cycle();
    void        processCmd(String &cmd);
  private:
    // Common
    Circuit*    pCircuit;
    uint32_t    taskDelay =       50;               // ms
    bool        started =         false;
    float       redLimit =        50;               // uA
    float       yellowLimit =     25;               // uA
    // Params
    float       startVoltage =    -0.2;             // V
    float       stopVoltage =     1.0;              // V
    float       stepSize =        0.005;            // V
    float       pulseAmplitude =  0.050;            // V
    float       frequency =       2.0;              // Hz
    float       maxCurrent =      1000.0;           // uA
    uint32_t    equilTime =       5000;             // ms
    // Vars
    float       currentVoltage =  0.0;
    float       vFordward =       0.0;              // V
    float       iFordward =       0.0;              // uA
    float       vReverse =        0.0;              // V
    float       iReverse =        0.0;              // uA
    uint32_t    initTime;
    // Func
    void        setStartConditions();
    void        ledsResult();
    void        checkEnd();
    void        changeVoltage();
};
