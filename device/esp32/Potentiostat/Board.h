#ifndef   BOARD_H

  #define   BOARD_H

  #if defined(ARDUINO_ESP32_DEV)

    #include  <math.h>
    #include  <Arduino.h>
    #include  <SimpleKalmanFilter.h>

    #define   BOARD_VCC         3.3
    // PWM
    #define   PWM_PIN           25
    #define   PWM_RES           11
    #define   PWM_CHANNEL       0
    #define   PWM_FREQ          30000
    #define   PWM_MAX_VALUE     (pow(2, PWM_RES) - 1)
    // ADC
    #define   ADC_PIN           34
    #define   ADC_RES           12
    #define   ADC_MAX_VALUE     (pow(2, ADC_RES) - 1)
    #define   ADC_ATTEN         ADC_11db
    #define   ADC_REF_V         1.1
    // GPIO
    #define   GREEN_LED_PIN     33
    #define   YELLOW_LED_PIN    32
    #define   RED_LED_PIN       26

  #endif  //#if defined(ARDUINO_ESP32_DEV)

  static inline __attribute__((always_inline))
  uint32_t voltageToDutyCycle(float voltage) {
    /*
    Return the duty cycle of the PWM to achive <voltage> when filtered.
    The function limit the voltage on the board PWM range.
    */
    uint32_t result = uint32_t(voltage * float(PWM_MAX_VALUE) / float(BOARD_VCC));
    result = (result > PWM_MAX_VALUE) ? uint32_t(PWM_MAX_VALUE) : uint32_t(result);
    result = (result < 0) ? 0 : uint32_t(result);
    return result;
  }

  static inline __attribute__((always_inline))
  float dutyCycleToVoltage(uint32_t dutyCycle) {
    /*
    Return the voltage output from a PWM duty cycle.
    */
    dutyCycle = (dutyCycle > PWM_MAX_VALUE) ? uint32_t(PWM_MAX_VALUE) : dutyCycle;
    return float(dutyCycle) * float(BOARD_VCC) / float(PWM_MAX_VALUE);
  }

  static inline __attribute__((always_inline))
  float adcToVoltage(uint32_t adcValue) {
    /*
    Convert ADC value to voltage.
    */
    return (float(adcValue) * float(BOARD_VCC)) / float(ADC_MAX_VALUE);
  }

  static inline __attribute__((always_inline))
  float parseDecimal(String &str) {
    /*
    Extract decimal number from string
    */
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