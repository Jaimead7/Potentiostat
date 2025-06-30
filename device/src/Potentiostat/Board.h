#ifndef   BOARD_H

  #define   BOARD_H

  #if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_MEGA2560)

    #include  <math.h>
    #include  <Arduino.h>

    #define   BOARD_VCC         5
    // PWM
    #define   PWM_RES           8
    #define   PWM_FREQ          TCCR1B & B11111000 | B00000001
    #define   PWM_MAX_VALUE     (pow(2, PWM_RES) - 1)
    // ADC
    #define   ADC_RES           10
    #define   ADC_MAX_VALUE     (pow(2, ADC_RES) - 1)

  #endif  //#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_MEGA2560)

  static inline  __attribute__((always_inline))
  uint16_t  voltageToDutyCycle(float voltage) {
    /*
    Return the duty cycle of the PWM to achive <voltage> when filtered.
    The function limit the voltage on the board PWM range.
    */
    uint16_t result = uint16_t(voltage * float(PWM_MAX_VALUE) / float(BOARD_VCC));
    result = (result > PWM_MAX_VALUE) ? uint16_t(PWM_MAX_VALUE) : uint16_t(result);
    result = (result < 0) ? 0 : uint16_t(result);
    return result;
  }

  static inline  __attribute__((always_inline))
  float dutyCycleToVoltage(uint16_t dutyCycle) {
    /*
    Return the voltage output from a PWM duty cycle.
    */
    dutyCycle = (dutyCycle > PWM_MAX_VALUE) ? uint16_t(PWM_MAX_VALUE) : dutyCycle;
    return float(dutyCycle) * float(BOARD_VCC) / float(PWM_MAX_VALUE);
  }

  static inline  __attribute__((always_inline))
  float adcToVoltage(uint16_t adcValue) {
    /*
    Convert ADC value to voltage.
    */
    return (float(adcValue) * float(BOARD_VCC)) / float(ADC_MAX_VALUE);
  }

  static inline  __attribute__((always_inline))
  float parseDecimal(String &str) {
    int charPos = str.indexOf('$');
    if (charPos == -1) {
      float number = str.toFloat();
      str = "";
      return number;
    }
    float number = str.substring(0, charPos).toFloat();
    str = str.substring(charPos);
    return number;
  }

#endif  //#ifndef   BOARD_H