#ifndef CIRCUIT_H

  #define CIRCUIT_H

  #include  "Board.h"
  #include  "Commands.h"

  #if defined(ARDUINO_ESP32_DEV)

    /*
    Parameters for:
      - Op-Amp: LM324
      - Voltage range: [-1.0569, 1.1]
      - Current range: [-208.33, 208.33]
    */
    #define   DEFAULT_R1            10000
    #define   DEFAULT_R2            330
    #define   DEFAULT_R3            1000
    #define   DEFAULT_R4            220
    #define   DEFAULT_R5            47000
    #define   DEFAULT_R6            15000
    #define   DEFAULT_VB1           -5
    #define   DEFAULT_VB2           -5
    #define   DEFAULT_OPAMP_VCC_P   12.0
    #define   DEFAULT_OPAMP_VCC_N   -12.0
    #define   DEFAULT_OPAMP_HR      1.5
    #define   DEFAULT_OPAMP_BR      0.002

  #endif  //#if defined(ARDUINO_ESP32_DEV)

  class Circuit {
    public:
      Circuit();
      uint32_t    R1 =              DEFAULT_R1;
      uint32_t    R2 =              DEFAULT_R2;
      uint32_t    R3 =              DEFAULT_R3;
      uint32_t    R4 =              DEFAULT_R4;
      uint32_t    R5 =              DEFAULT_R5;
      uint32_t    R6 =              DEFAULT_R6;
      float       Vb1 =             DEFAULT_VB1;
      float       Vb2 =             DEFAULT_VB2;
      float       opAmpVccP =       DEFAULT_OPAMP_VCC_P;
      float       opAmpVccN =       DEFAULT_OPAMP_VCC_N;
      float       opAmpHeadroom =   DEFAULT_OPAMP_HR;
      float       opAmpBottomroom = DEFAULT_OPAMP_BR;
      void        begin();
      void        setWEVoltage(float voltage);
      float       readWECurrent();
      void        readAndTransmit(String header);
      void        processCmd(String &cmd);
      //
      esp_adc_cal_characteristics_t adcChars;
      float       ceVoltageToPWMVoltage(float voltage);
      float       pwmVoltageToCEVoltage(float pwmVoltage);
      float       voltageToWECurrent(float voltage);
      float       weCurrentToVoltage(float current);
    private:
  };

#endif  //#ifndef CIRCUIT_H