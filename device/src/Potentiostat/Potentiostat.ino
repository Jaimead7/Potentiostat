// Libraries
#include  "Cycles.h"

#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_MEGA2560)
  #define   PWM_PIN           10
  #define   ADC_PIN           A0
#endif  //#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_MEGA2560)


Circuit             myCircuit = Circuit();
Potentiometry       pt = Potentiometry(myCircuit);
CyclicVoltammetry   cv = CyclicVoltammetry(myCircuit);


void readSerial() {
  /*
  Read serial data.
  */
  String  serialInput = "";
  while (Serial.available()) {
    while (Serial.available() > 0) {
      serialInput = Serial.readString();
    }
    if (serialInput.substring(0, PT_CMD.length()) == PT_CMD) {
      pt.processCmd(serialInput);
    }
    if (serialInput.substring(0, CV_CMD.length()) == CV_CMD) {
      cv.processCmd(serialInput);
    }
  }
}

void setup() {
  Serial.begin(115200);
  myCircuit.begin(PWM_PIN, ADC_PIN);
  Serial.println("Setup completed.");
  delay(1000);
}

void loop() {
  readSerial();
  pt.cycle();
  cv.cycle();
}
