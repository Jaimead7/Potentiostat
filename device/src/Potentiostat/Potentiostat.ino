// Libraries
#include  "Cycles.h"
#include  "Board.h"


Circuit                 myCircuit = Circuit();
Potentiometry           pt = Potentiometry(myCircuit);
CyclicVoltammetry       cv = CyclicVoltammetry(myCircuit);
SquareWaveVoltammetry   swv = SquareWaveVoltammetry(myCircuit);


void readSerial() {
  /*
  Read serial data.
  */
  String  serialInput = "";
  while (Serial.available()) {
    while (Serial.available() > 0) {
      serialInput = Serial.readString();
    }
    if (serialInput.substring(0, CIR_CMD.length()) == CIR_CMD) {
      myCircuit.processCmd(serialInput);
    }
    if (serialInput.substring(0, PT_CMD.length()) == PT_CMD) {
      pt.processCmd(serialInput);
    }
    if (serialInput.substring(0, CV_CMD.length()) == CV_CMD) {
      cv.processCmd(serialInput);
    }
    if (serialInput.substring(0, SWV_CMD.length()) == SWV_CMD) {
      swv.processCmd(serialInput);
    }
  }
}

void setup() {
  Serial.begin(115200);
  myCircuit.begin();
  pt.begin();
  cv.begin();
  swv.begin();
  Serial.println("Setup completed.");
  delay(1000);
}

void loop() {
  readSerial();
  uint32_t  mV;
  esp_adc_cal_get_voltage(ADC_CHANNEL, &myCircuit.adcChars, &mV);
  float_t V = float_t(mV)/1000.0;
  Serial.println("------------");
  Serial.println(V);
  Serial.println(myCircuit.voltageToWECurrent(float_t(mV)/1000.0) * 1000000.0);
  delay(1000);
}
