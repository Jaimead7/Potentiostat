// Libraries
#include  "Cycles.h"
#include  "Board.h"
#include  "Leds.h"


Circuit                 myCircuit = Circuit();
MyLed                   greenLed = MyLed(GREEN_LED_PIN);
MyLed                   yellowLed = MyLed(YELLOW_LED_PIN);
MyLed                   redLed = MyLed(RED_LED_PIN);
Potentiometry           pt = Potentiometry(myCircuit, greenLed, yellowLed, redLed);
CyclicVoltammetry       cv = CyclicVoltammetry(myCircuit, greenLed, yellowLed, redLed);
SquareWaveVoltammetry   swv = SquareWaveVoltammetry(myCircuit, greenLed, yellowLed, redLed);


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
  //Circuit
  myCircuit.begin();
  //Leds
  greenLed.begin();
  yellowLed.begin();
  redLed.begin();
  //Cycles
  pt.begin();
  cv.begin();
  swv.begin();
  //Timeout
  delay(1000);
  Serial.println("Setup completed.");
}

void loop() {
  readSerial();
}
