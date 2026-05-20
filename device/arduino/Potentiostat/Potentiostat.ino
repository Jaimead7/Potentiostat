// Libraries
#include  "Cycles.h"


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
    while (true) {
      if (serialInput.substring(0, CIR_CMD.length()) == CIR_CMD) {
        myCircuit.processCmd(serialInput);
      }
      else if (serialInput.substring(0, PT_CMD.length()) == PT_CMD) {
        pt.processCmd(serialInput);
      }
      else if (serialInput.substring(0, CV_CMD.length()) == CV_CMD) {
        cv.processCmd(serialInput);
      }
      else if (serialInput.substring(0, SWV_CMD.length()) == SWV_CMD) {
        swv.processCmd(serialInput);
      }
      else {
        break;
      }
    }
  }
}

void setup() {
  Serial.begin(115200);
  myCircuit.begin();
  Serial.println("Setup completed.");
  pinMode(GREEN_LED_PIN, OUTPUT);  //RED LED
  pinMode(YELLOW_LED_PIN, OUTPUT);  //YELLOW LED
  pinMode(GREEN_LED_PIN, OUTPUT);  //GREEN LED
  delay(1000);
}

void loop() {
  readSerial();
  pt.cycle();
  cv.cycle();
  swv.cycle();
}
