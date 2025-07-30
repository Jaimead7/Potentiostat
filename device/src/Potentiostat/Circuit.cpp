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

  void Circuit::processCmd(String &cmd) {
    /*
    Process circuit commands.
    Ex: $CIR$R1:10000
    */
    String result = "";
    if (cmd.substring(0, CIR_CMD.length()) == CIR_CMD) {
      cmd = cmd.substring(CIR_CMD.length());
      if (cmd.substring(0, R1_CMD.length()) == R1_CMD) {
        cmd = cmd.substring(R1_CMD.length());
        R1 = (uint32_t)parseDecimal(cmd);
        result += "$OK->" + CIR_CMD + R1_CMD + String(R1) + "\n";
      }
      if (cmd.substring(0, R2_CMD.length()) == R2_CMD) {
        cmd = cmd.substring(R2_CMD.length());
        R2 = (uint32_t)parseDecimal(cmd);
        result += "$OK->" + CIR_CMD + R2_CMD + String(R2) + "\n";
      }
      if (cmd.substring(0, R3_CMD.length()) == R3_CMD) {
        cmd = cmd.substring(R3_CMD.length());
        R3 = (uint32_t)parseDecimal(cmd);
        result += "$OK->" + CIR_CMD + R3_CMD + String(R3) + "\n";
      }
      if (cmd.substring(0, R4_CMD.length()) == R4_CMD) {
        cmd = cmd.substring(R4_CMD.length());
        R4 = (uint32_t)parseDecimal(cmd);
        result += "$OK->" + CIR_CMD + R4_CMD + String(R4) + "\n";
      }
      if (cmd.substring(0, R5_CMD.length()) == R5_CMD) {
        cmd = cmd.substring(R5_CMD.length());
        R5 = (uint32_t)parseDecimal(cmd);
        result += "$OK->" + CIR_CMD + R5_CMD + String(R5) + "\n";
      }
      if (cmd.substring(0, R6_CMD.length()) == R6_CMD) {
        cmd = cmd.substring(R6_CMD.length());
        R6 = (uint32_t)parseDecimal(cmd);
        result += "$OK->" + CIR_CMD + R6_CMD + String(R6) + "\n";
      }
      if (cmd.substring(0, VB1_CMD.length()) == VB1_CMD) {
        cmd = cmd.substring(VB1_CMD.length());
        Vb1 = parseDecimal(cmd);
        result += "$OK->" + CIR_CMD + VB1_CMD + String(Vb1) + "\n";
      }
      if (cmd.substring(0, VB2_CMD.length()) == VB2_CMD) {
        cmd = cmd.substring(VB2_CMD.length());
        Vb2 = parseDecimal(cmd);
        result += "$OK->" + CIR_CMD + VB2_CMD + String(Vb2) + "\n";
      }
      if (cmd.substring(0, OPAMP_VCC_P_CMD.length()) == OPAMP_VCC_P_CMD) {
        cmd = cmd.substring(OPAMP_VCC_P_CMD.length());
        opAmpVccP = parseDecimal(cmd);
        result += "$OK->" + CIR_CMD + OPAMP_VCC_P_CMD + String(opAmpVccP) + "\n";
      }
      if (cmd.substring(0, OPAMP_VCC_N_CMD.length()) == OPAMP_VCC_N_CMD) {
        cmd = cmd.substring(OPAMP_VCC_N_CMD.length());
        opAmpVccN = parseDecimal(cmd);
        result += "$OK->" + CIR_CMD + OPAMP_VCC_N_CMD + String(opAmpVccN) + "\n";
      }
      if (cmd.substring(0, OPAMP_HR_CMD.length()) == OPAMP_HR_CMD) {
        cmd = cmd.substring(OPAMP_HR_CMD.length());
        opAmpHeadroom = parseDecimal(cmd);
        result += "$OK->" + CIR_CMD + OPAMP_HR_CMD + String(opAmpHeadroom) + "\n";
      }
      if (cmd.substring(0, OPAMP_BR_CMD.length()) == OPAMP_BR_CMD) {
        cmd = cmd.substring(OPAMP_BR_CMD.length());
        opAmpBottomroom = parseDecimal(cmd);
        result += "$OK->" + CIR_CMD + OPAMP_BR_CMD + String(opAmpBottomroom) + "\n";
      }
      Serial.print(result);
    }
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
    return -(- (float(Vb2) / float(R5)) - (float(voltage) / float(R6)));
  }

  float Circuit::weCurrentToVoltage(float current) {
    /*
    Voltage on the board input for a given current.
    */
    return - float(R6) * ((float(Vb2) / float(R5)) + current);
  }

#endif  //#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_MEGA2560)