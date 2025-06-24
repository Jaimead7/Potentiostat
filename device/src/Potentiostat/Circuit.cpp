#include  "Circuit.h"

#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_MEGA2560)

  Circuit::Circuit() {}

  void Circuit::begin(
    uint8_t   sendPin,
    uint8_t   readPin
  ) {
    /*
    Circuit setup.
    */
    pwmPin = sendPin;
    adcPin = readPin;
    TCCR1B = PWM_FREQ;
    pinMode(pwmPin, OUTPUT);
    pinMode(adcPin, INPUT);
    setWEVoltage(0.0);
    Serial.println("Circuit setup completed.");
  }

  void Circuit::setWEVoltage(float voltage) {
    /*
    Set the voltage on the WE to <voltage>.
    The voltage is set on the CE.
    As the WE is set to virtual ground, the voltage set on the CE is set to negative <voltage>.
    */
    uint16_t dutyCycle  = voltageToDutyCycle(ceVoltageToPWMVoltage(-voltage));
    lastDutyCycle = dutyCycle;
    analogWrite(pwmPin, dutyCycle);
  }

  float Circuit::readWECurrent() {
    /*
    Read the current (uA) on the WE.
    Positive values indicates that current is flowing from the WE to the CE (oxidation).
    Negative values indicates that current is flowing from the CE to the WE (reduction).
    */
    return voltageToWECurrent(adcToVoltage(analogRead(adcPin))) * 1000000.0;
  }

  void Circuit::readAndTransmit(String header) {
    Serial.print(header);
    Serial.print(TIMESTAMP_CMD);
    Serial.print(millis());
    Serial.print(",");
    Serial.print(VOLTAGE_CMD);
    Serial.print(-pwmVoltageToCEVoltage(dutyCycleToVoltage(lastDutyCycle)));
    Serial.print(",");
    Serial.print(CURRENT_CMD);
    Serial.print(readWECurrent());
    Serial.println();
  }

  /**************** PRIVATE ****************/

  float Circuit::ceVoltageToPWMVoltage(float ceVoltage) {
    /*
    Return the voltage needed on the output of the PWM to achive <ceVoltage> on the CE.
    The opAmp is on inverting summing amplifier mode (Vb1 + PWMVoltage).
    The PWMVoltage is limited to the range [0, BOARD_VCC].
    */
    float result = - float(R2) * ((float(Vb1) / float(R3)) + (float(ceVoltage) / float(R4)));
    result = (result > BOARD_VCC) ? float(BOARD_VCC) : result;
    result = (result < 0) ? 0. : result;
    return result;
  }

  float Circuit::pwmVoltageToCEVoltage(float pwmVoltage) {
    /*
    Return CE voltage from PWM voltage.
    The PWM voltage is limited by the opAmp characteristics.
    The CE voltage is limited by the opAmp characteristics.
    */
    pwmVoltage = (pwmVoltage > opAmpVccP - opAmpHeadroom) ? float(opAmpVccP - opAmpHeadroom) : pwmVoltage;
    pwmVoltage = (pwmVoltage < opAmpVccN + opAmpBottomroom) ? float(opAmpVccN + opAmpBottomroom) : pwmVoltage;
    float result = - float(R4) * ((float(pwmVoltage) / float(R2)) + ((float(Vb1) / float(R3))));
    result = (result > opAmpVccP - opAmpHeadroom) ? float(opAmpVccP - opAmpHeadroom) : result;
    result = (result < opAmpVccN + opAmpBottomroom) ? float(opAmpVccN + opAmpBottomroom) : result;
    return result;
  }

  float Circuit::voltageToWECurrent(float voltage) {
    /*
    Return the current (A) on the WE from the voltage.
    The opAmp combinates a current to voltage converter with an inverting summing amplifier mode (Vb2 + iWE).
    */
    return - (float(Vb2) / float(R5)) - (float(voltage) / float(R6));
  }

  float Circuit::weCurrentToVoltage(float current) {
    /*
    Voltage on the board input for a given current.
    */
    return - float(R6) * ((float(Vb2) / float(R5)) + current);
  }

#endif  //#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_MEGA2560)