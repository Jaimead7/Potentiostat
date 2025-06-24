#include  "Cycles.h"

#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_MEGA2560)

  /**************** POTENTIOMETRY ****************/

  Potentiometry::Potentiometry(Circuit &myCircuit) {
    pCircuit = myCircuit;
  }

  void Potentiometry::cycle() {
    /*
    Cycle loop for the potentiometry.
    Call it cyclically on the main loop.
    */
    if (run) {
      if (!started) {
        pCircuit.setWEVoltage(voltageSP);
        checkStart();
      } else {
        if (millis() - initTime < duration) {
          if (taskDelay <= millis() - lastRead) {
            pCircuit.readAndTransmit(PT_CMD);
            lastRead = millis();
          }
        } else {
          pCircuit.setWEVoltage(0.0);
          run = false;
          Serial.println(PT_CMD + END_CMD);
        }
      }
    } else {
      started = false;
    }
  }

  void  Potentiometry::checkStart() {
    /*
    Check if the sample is on the sensor.
    If there is any sample, the current will flow.
    */
    if (abs(pCircuit.readWECurrent()) > startThreshold) {
      initTime = millis();
      started = true;
      Serial.println(PT_CMD + START_CMD);
    }
  }

  void  Potentiometry::processCmd(String &cmd) {
    /*
    Process potentiometry commands.
    Ex: $PT$START
    */
    if (cmd.substring(0, PT_CMD.length()) == PT_CMD) {
      cmd = cmd.substring(PT_CMD.length());
      if (cmd.substring(0, START_CMD.length()) == START_CMD) {
        run = true;
        cmd = cmd.substring(START_CMD.length());
        Serial.println("$OK->" + PT_CMD + START_CMD);
      }
      if (cmd.substring(0, STOP_CMD.length()) == STOP_CMD) {
        run = false;
        cmd = cmd.substring(STOP_CMD.length());
        Serial.println("$OK->" + PT_CMD + STOP_CMD);
      }
    }
  }

  /**************** CYCLIC VOLTAMMETRY ****************/

  CyclicVoltammetry::CyclicVoltammetry(Circuit &myCircuit) {
    pCircuit = myCircuit;
  }

  void CyclicVoltammetry::cycle() {
    /*
    Cycle loop for the cyclic voltammetry.
    Call it cyclically on the main loop.
    */
    if (run) {
      if (!started) {
        setStartConditions();
        started = true;
      } else {
        if (taskDelay <= millis() - lastVoltChange && currentCycle < totalCycles) {
          pCircuit.readAndTransmit(CV_CMD + CURRENT_CYCLE_CMD + String(currentCycle + 1) + ",");
          changeVoltage();
        }
        checkEnd();
      }
    } else {
      started = false;
    }
  }

  void  CyclicVoltammetry::processCmd(String &cmd) {
    /*
    Process cyclic voltammetry commands.
    Ex: $CV$START
    */
    if (cmd.substring(0, CV_CMD.length()) == CV_CMD) {
      cmd = cmd.substring(CV_CMD.length());
      if (cmd.substring(0, START_CMD.length()) == START_CMD) {
        run = true;
        cmd = cmd.substring(START_CMD.length());
        Serial.println("$OK->" + CV_CMD + START_CMD);
      }
      if (cmd.substring(0, STOP_CMD.length()) == STOP_CMD) {
        run = false;
        cmd = cmd.substring(STOP_CMD.length());
        Serial.println("$OK->" + CV_CMD + STOP_CMD);
      }
    }
  }

  void  CyclicVoltammetry::setStartConditions() {
    /*
    Set the conditions for the start of the cyclic voltammetry.
    */
    currentCycle = 0;
    direction = 1;
    lastVoltChange = millis();
    currentVoltage = startVoltage;
    pCircuit.setWEVoltage(currentVoltage);
  }

  void  CyclicVoltammetry::checkEnd() {
    /*
    Check the conditions os the end of the cyclic voltammetry.
    */
    if (currentCycle >= totalCycles) {
      pCircuit.setWEVoltage(0.0);
      run = false;
      started = false;
      Serial.println(CV_CMD + END_CMD);
    }
  }

  void  CyclicVoltammetry::changeVoltage() {
    /*
    Calculate next step and change voltage.
    */
    uint32_t currentTime = millis();
    uint32_t elapsedTime = currentTime - lastVoltChange;
    currentVoltage += direction * (float(elapsedTime) / 1000) * (float(slewRate) / 1000);
    if (direction == 1 && currentVoltage >= peakVoltage) {
      currentVoltage = peakVoltage;
      direction = -1;
    }
    if (direction == -1 && currentVoltage <= stopVoltage) {
      direction = 1;
      currentCycle += 1;
    }
    pCircuit.setWEVoltage(currentVoltage);
    lastVoltChange = currentTime;
  }

#endif  //#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_MEGA2560)