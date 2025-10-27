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
    bool        started =         false;
    uint16_t    taskDelay =       50;               // ms
    float       voltageSP =       0.6;              // V
    uint32_t    duration =        120000;           // ms
    float       startThreshold =  50.;
    uint32_t    initTime;
    uint32_t    lastRead;
    Circuit*    pCircuit;
    void        checkStart();
};


class CyclicVoltammetry {
  public:
    CyclicVoltammetry(Circuit &myCircuit);
    bool        run =             false;
    void        cycle();
    void        processCmd(String &cmd);
  private:
    bool        started =         false;
    uint16_t    taskDelay =       50;               // ms
    uint8_t     currentCycle =    0;
    uint8_t     totalCycles =     1;
    float       slewRate =        100.0;            // mV/s
    float       startVoltage =    -0.5;             // V
    float       peakVoltage =     0.9;              // V
    float       stopVoltage =     -0.5;             // V
    float       currentVoltage =  0.0;
    int8_t      direction =       1;                // 1 positive slewRate, -1 negative slewRate
    uint32_t    lastVoltChange;
    Circuit*    pCircuit;
    void        setStartConditions();
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
    bool        started =         false;
    uint16_t    taskDelay =       50;               // ms
    float       startVoltage =    -0.2;             // V
    float       stopVoltage =     1.0;              // V
    uint16_t    stepSize =        5;                // mV
    uint32_t    pulseAmplitude =  50;               // mV
    float       frequency =       2.0;              // Hz
    float       maxCurrent =      1.0;              // mA
    float       equilTime =       5.0;              // s
    uint32_t    irComp =          50;               // ohm
    float       currentVoltage =  0.0;
    float       vFordward =       0.0;              // V
    float       iFordward =       0.0;              // uA
    float       vReverse =        0.0;              // V
    float       iReverse =        0.0;              // uA
    uint32_t    initTime;
    Circuit*    pCircuit;
    void        setStartConditions();
    void        checkEnd();
    void        changeVoltage();
};
