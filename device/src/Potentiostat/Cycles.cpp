#include  "Cycles.h"

#if defined(ARDUINO_ESP32_DEV)

  /**************** POTENTIOMETRY ****************/

  void ptCycleWrapper(void * arg) {
    /*
    Wrapper for the cycle call form xTaskCreate.
    */
    Potentiometry* pt = static_cast<Potentiometry*>(arg);
    pt->cycle();
  }

  Potentiometry::Potentiometry(Circuit &myCircuit) {
    pCircuit = &myCircuit;
  }

  void Potentiometry::begin() {
    xTaskCreate(ptCycleWrapper, "potentiometry", 4092, this, 2, &task);
  }

  void Potentiometry::cycle() {
    /*
    Cycle loop for the potentiometry.
    */
    vTaskSuspend(task);
    while (true) {
      start();
      while (millis() - initTime < duration && !stop) {
        pCircuit->readAndTransmit(PT_CMD);
        delay(taskDelay);
      }
      //TODO: leds
      stop = false;
      pCircuit->setWEVoltage(0.0);
      Serial.println(PT_CMD + END_CMD);
      vTaskSuspend(task);
    }
  }

  void  Potentiometry::start() {
    /*
    Check if the sample is on the sensor.
    If there is any sample, the current will flow.
    */
    pCircuit->setWEVoltage(voltageSP);
    while (abs(pCircuit->readWECurrent()) < startThreshold && !stop) {
      delay(taskDelay);
    }
    initTime = millis();
    Serial.println(PT_CMD + START_CMD);
  }

  void  Potentiometry::processCmd(String &cmd) {
    /*
    Process potentiometry commands.
    Ex: $PT$START
    */
    String result = "";
    if (cmd.substring(0, PT_CMD.length()) == PT_CMD) {
      cmd = cmd.substring(PT_CMD.length());
      if (cmd.substring(0, START_CMD.length()) == START_CMD) {
        vTaskResume(task);
        cmd = cmd.substring(START_CMD.length());
        result += "$OK->" + PT_CMD + START_CMD + "\n";
      }
      if (cmd.substring(0, STOP_CMD.length()) == STOP_CMD) {
        stop = true;
        cmd = cmd.substring(STOP_CMD.length());
        result += "$OK->" + PT_CMD + STOP_CMD + "\n";
      }
      if (cmd.substring(0, TASK_DELAY_CMD.length()) == TASK_DELAY_CMD) {
        cmd = cmd.substring(TASK_DELAY_CMD.length());
        taskDelay = (uint16_t)parseDecimal(cmd);
        result += "$OK->" + PT_CMD + TASK_DELAY_CMD + String(taskDelay) + "\n";
      }
      if (cmd.substring(0, VOLTAGE_SETPOINT_CMD.length()) == VOLTAGE_SETPOINT_CMD) {
        cmd = cmd.substring(VOLTAGE_SETPOINT_CMD.length());
        voltageSP = parseDecimal(cmd);
        result += "$OK->" + PT_CMD + VOLTAGE_SETPOINT_CMD + String(voltageSP) + "\n";
      }
      if (cmd.substring(0, DURATION_CMD.length()) == DURATION_CMD) {
        cmd = cmd.substring(DURATION_CMD.length());
        duration = (uint32_t)parseDecimal(cmd);
        result += "$OK->" + PT_CMD + DURATION_CMD + String(duration) + "\n";
      }
      if (cmd.substring(0, THRESHOLD_CMD.length()) == THRESHOLD_CMD) {
        cmd = cmd.substring(THRESHOLD_CMD.length());
        startThreshold = parseDecimal(cmd);
        result += "$OK->" + PT_CMD + THRESHOLD_CMD + String(startThreshold) + "\n";
      }
      if (cmd.substring(0, PARAMS_CMD.length()) == PARAMS_CMD) {
        cmd = cmd.substring(PARAMS_CMD.length());
        result += PT_CMD + PARAMS_CMD + TASK_DELAY_CMD + String(taskDelay) + VOLTAGE_SETPOINT_CMD + String(voltageSP) + DURATION_CMD + String(duration) + THRESHOLD_CMD + String(startThreshold) + "\n";
      }
      Serial.print(result);
    }
  }

  /**************** CYCLIC VOLTAMMETRY ****************/

  void cvCycleWrapper(void * arg) {
    /*
    Wrapper for the cycle call form xTaskCreate.
    */
    CyclicVoltammetry* cv = static_cast<CyclicVoltammetry*>(arg);
    cv->cycle();
  }

  CyclicVoltammetry::CyclicVoltammetry(Circuit &myCircuit) {
    pCircuit = &myCircuit;
  }

  void CyclicVoltammetry::begin() {
    xTaskCreate(cvCycleWrapper, "cyclicVoltammetry", 4092, this, 2, &task);
  }

  void CyclicVoltammetry::cycle() {
    /*
    Cycle loop for the cyclic voltammetry.
    */
    vTaskSuspend(task);
    while (true) {
      start();
      while (currentCycle < totalCycles && !stop) {
        pCircuit->readAndTransmit(CV_CMD + CURRENT_CYCLE_CMD + String(currentCycle + 1) + ",");
        changeVoltage();
        delay(taskDelay);
      }
      //TODO: leds
      stop = false;
      pCircuit->setWEVoltage(0.0);
      Serial.println(CV_CMD + END_CMD);
      vTaskSuspend(task);
    }
  }
  void  CyclicVoltammetry::processCmd(String &cmd) {
    /*
    Process cyclic voltammetry commands.
    Ex: $CV$START
    */
    String result = "";
    if (cmd.substring(0, CV_CMD.length()) == CV_CMD) {
      cmd = cmd.substring(CV_CMD.length());
      if (cmd.substring(0, START_CMD.length()) == START_CMD) {
        vTaskResume(task);
        cmd = cmd.substring(START_CMD.length());
        result += "$OK->" + CV_CMD + START_CMD + "\n";
      }
      if (cmd.substring(0, STOP_CMD.length()) == STOP_CMD) {
        stop = true;
        cmd = cmd.substring(STOP_CMD.length());
        result += "$OK->" + CV_CMD + STOP_CMD + "\n";
      }
      if (cmd.substring(0, TASK_DELAY_CMD.length()) == TASK_DELAY_CMD) {
        cmd = cmd.substring(TASK_DELAY_CMD.length());
        taskDelay = (uint16_t)parseDecimal(cmd);
        result += "$OK->" + CV_CMD + TASK_DELAY_CMD + String(taskDelay) + "\n";
      }
      if (cmd.substring(0, TOTAL_CYCLES_CMD.length()) == TOTAL_CYCLES_CMD) {
        cmd = cmd.substring(TOTAL_CYCLES_CMD.length());
        totalCycles = (uint8_t)parseDecimal(cmd);
        result += "$OK->" + CV_CMD + TOTAL_CYCLES_CMD + String(totalCycles) + "\n";
      }
      if (cmd.substring(0, SLEW_RATE_CMD.length()) == SLEW_RATE_CMD) {
        cmd = cmd.substring(SLEW_RATE_CMD.length());
        slewRate = parseDecimal(cmd);
        result += "$OK->" + CV_CMD + SLEW_RATE_CMD + String(slewRate) + "\n";
      }
      if (cmd.substring(0, START_VOLTAGE_CMD.length()) == START_VOLTAGE_CMD) {
        cmd = cmd.substring(START_VOLTAGE_CMD.length());
        startVoltage = parseDecimal(cmd);
        result += "$OK->" + CV_CMD + START_VOLTAGE_CMD + String(startVoltage) + "\n";
      }
      if (cmd.substring(0, PEAK_VOLTAGE_CMD.length()) == PEAK_VOLTAGE_CMD) {
        cmd = cmd.substring(PEAK_VOLTAGE_CMD.length());
        peakVoltage = parseDecimal(cmd);
        result += "$OK->" + CV_CMD + PEAK_VOLTAGE_CMD + String(peakVoltage) + "\n";
      }
      if (cmd.substring(0, STOP_VOLTAGE_CMD.length()) == STOP_VOLTAGE_CMD) {
        cmd = cmd.substring(STOP_VOLTAGE_CMD.length());
        stopVoltage = parseDecimal(cmd);
        result += "$OK->" + CV_CMD + STOP_VOLTAGE_CMD + String(stopVoltage) + "\n";
      }
      if (cmd.substring(0, PARAMS_CMD.length()) == PARAMS_CMD) {
        cmd = cmd.substring(PARAMS_CMD.length());
        result += CV_CMD + PARAMS_CMD + TOTAL_CYCLES_CMD + String(totalCycles) + SLEW_RATE_CMD + String(slewRate) + START_VOLTAGE_CMD + String(startVoltage) + PEAK_VOLTAGE_CMD + String(peakVoltage) + STOP_VOLTAGE_CMD + String(stopVoltage) + "\n";
      }
      Serial.print(result);
    }
  }

  void  CyclicVoltammetry::start() {
    /*
    Set the conditions for the start of the cyclic voltammetry.
    */
    currentCycle = 0;
    direction = 1;
    currentVoltage = startVoltage;
    pCircuit->setWEVoltage(currentVoltage);
    lastVoltChange = millis();
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
      currentVoltage = startVoltage;
      currentCycle += 1;
    }
    pCircuit->setWEVoltage(currentVoltage);
    lastVoltChange = currentTime;
  }

  /**************** SQUARE WAVE VOLTAMMETRY ****************/

  void swvCycleWrapper(void * arg) {
    /*
    Wrapper for the cycle call form xTaskCreate.
    */
    SquareWaveVoltammetry* swv = static_cast<SquareWaveVoltammetry*>(arg);
    swv->cycle();
  }

  SquareWaveVoltammetry::SquareWaveVoltammetry(Circuit &myCircuit) {
    pCircuit = &myCircuit;
  }

  void SquareWaveVoltammetry::begin() {
    xTaskCreate(swvCycleWrapper, "squareWaveVoltammetry", 4092, this, 2, &task);
  }

  void SquareWaveVoltammetry::cycle() {
    /*
    Cycle loop for the square wave voltammetry.
    */
    vTaskSuspend(task);
    while (true) {
      start();
      while (!checkEnd() && !stop) {
        transmit();
        changeVoltage();
        delay(taskDelay);
      }
      //TODO: leds
      stop = false;
      pCircuit->setWEVoltage(0.0);
      Serial.println(SWV_CMD + END_CMD);
      vTaskSuspend(task);
    }
  }

  void  SquareWaveVoltammetry::processCmd(String &cmd) {
    /*
    Process square wave voltammetry commands.
    Ex: $SWV$START
    */
    String result = "";
    if (cmd.substring(0, SWV_CMD.length()) == SWV_CMD) {
      cmd = cmd.substring(SWV_CMD.length());
      if (cmd.substring(0, START_CMD.length()) == START_CMD) {
        vTaskResume(task);
        cmd = cmd.substring(START_CMD.length());
        result += "$OK->" + SWV_CMD + START_CMD + "\n";
      }
      if (cmd.substring(0, STOP_CMD.length()) == STOP_CMD) {
        stop = true;
        cmd = cmd.substring(STOP_CMD.length());
        result += "$OK->" + SWV_CMD + STOP_CMD + "\n";
      }
      if (cmd.substring(0, START_VOLTAGE_CMD.length()) == START_VOLTAGE_CMD) {
        cmd = cmd.substring(START_VOLTAGE_CMD.length());
        startVoltage = parseDecimal(cmd);
        result += "$OK->" + SWV_CMD + START_VOLTAGE_CMD + String(startVoltage) + "\n";
      }
      if (cmd.substring(0, STOP_VOLTAGE_CMD.length()) == STOP_VOLTAGE_CMD) {
        cmd = cmd.substring(STOP_VOLTAGE_CMD.length());
        stopVoltage = parseDecimal(cmd);
        result += "$OK->" + SWV_CMD + DURATION_CMD + String(stopVoltage) + "\n";
      }
      if (cmd.substring(0, STEP_SIZE_CMD.length()) == STEP_SIZE_CMD) {
        cmd = cmd.substring(STEP_SIZE_CMD.length());
        stepSize = (uint16_t)parseDecimal(cmd);
        result += "$OK->" + SWV_CMD + STEP_SIZE_CMD + String(stepSize) + "\n";
      }
      if (cmd.substring(0, PULSE_AMPLITUDE_CMD.length()) == PULSE_AMPLITUDE_CMD) {
        cmd = cmd.substring(PULSE_AMPLITUDE_CMD.length());
        pulseAmplitude = (uint32_t)parseDecimal(cmd);
        result += "$OK->" + SWV_CMD + PULSE_AMPLITUDE_CMD + String(pulseAmplitude) + "\n";
      }
      if (cmd.substring(0, FREQUENCY_CMD.length()) == FREQUENCY_CMD) {
        cmd = cmd.substring(FREQUENCY_CMD.length());
        frequency = parseDecimal(cmd);
        result += "$OK->" + SWV_CMD + FREQUENCY_CMD + String(frequency) + "\n";
      }
      if (cmd.substring(0, MAX_CURRENT_CMD.length()) == MAX_CURRENT_CMD) {
        cmd = cmd.substring(MAX_CURRENT_CMD.length());
        maxCurrent = parseDecimal(cmd);
        result += "$OK->" + SWV_CMD + MAX_CURRENT_CMD + String(maxCurrent) + "\n";
      }
      if (cmd.substring(0, EQUIL_TIME_CMD.length()) == EQUIL_TIME_CMD) {
        cmd = cmd.substring(EQUIL_TIME_CMD.length());
        equilTime = parseDecimal(cmd);
        result += "$OK->" + SWV_CMD + EQUIL_TIME_CMD + String(equilTime) + "\n";
      }
      if (cmd.substring(0, PARAMS_CMD.length()) == PARAMS_CMD) {
        cmd = cmd.substring(PARAMS_CMD.length());
        result += SWV_CMD + PARAMS_CMD + START_VOLTAGE_CMD + String(startVoltage) + STOP_VOLTAGE_CMD + String(stopVoltage) + STEP_SIZE_CMD + String(stepSize) + PULSE_AMPLITUDE_CMD + String(pulseAmplitude) + FREQUENCY_CMD + String(frequency) + MAX_CURRENT_CMD + String(maxCurrent) + EQUIL_TIME_CMD + String(equilTime) + "\n";
      }
      Serial.print(result);
    }
  }

  void  SquareWaveVoltammetry::start() {
    /*
    Set the conditions for the start of the square wave voltammetry.
    */
    currentVoltage = startVoltage;
    while ((millis() - initTime) <= (equilTime * 1000.)) {
      pCircuit->setWEVoltage(startVoltage);
    }
    currentVoltage = startVoltage;
    pCircuit->setWEVoltage(currentVoltage);
    initTime = millis();
  }

  void  SquareWaveVoltammetry::changeVoltage() {
    /*
    Calculate next step and change voltage.
    */
    uint32_t now = millis();
    vStair = (float)stepSize * float(int(((float)now - (float)initTime) / ((1. / frequency) * 1000.)));
    vPulse = (float)pulseAmplitude * float(int(((float)now - (float)initTime) / ((1. / (frequency * 2)) * 1000.)) % 2);
    if (currentVoltage < vStair + vPulse + startVoltage) {
      iReverse = pCircuit->readWECurrent();
      vReverse = currentVoltage;
    }
    if (currentVoltage > vStair + vPulse + startVoltage) {
      iFordward = pCircuit->readWECurrent();
      vFordward = currentVoltage;
    }
    currentVoltage = vStair + vPulse + startVoltage;
    pCircuit->setWEVoltage(currentVoltage);
  }

  void SquareWaveVoltammetry::transmit() {
    Serial.print(SWV_CMD);
    Serial.print(TIMESTAMP_CMD);
    Serial.print(millis());
    Serial.print(",");
    Serial.print(FORDWARD_VOLTAGE_CMD);
    Serial.print(vFordward);
    Serial.print(",");
    Serial.print(FORDWARD_CURRENT_CMD);
    Serial.print(iFordward);
    Serial.print(",");
    Serial.print(REVERSE_VOLTAGE_CMD);
    Serial.print(vReverse);
    Serial.print(",");
    Serial.print(REVERSE_CURRENT_CMD);
    Serial.print(iReverse);
    Serial.print(",");
    Serial.print(DIFF_CURRENT_CMD);
    Serial.print(iFordward - iReverse);
    Serial.println();
  }

  bool  SquareWaveVoltammetry::checkEnd() {
    /*
    Check the conditions os the end of the square wave voltammetry.
    */
    return (currentVoltage >= stopVoltage || iFordward >= maxCurrent || iReverse >= maxCurrent);
  }

#endif  //#if defined(ARDUINO_ESP32_DEV)