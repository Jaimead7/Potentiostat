#include  "Cycles.h"

#if defined(ARDUINO_ESP32_DEV)

  /**************** POTENTIOMETRY ****************/

  void  ptCycleWrapper(void * arg) {
    /*
    Wrapper for the cycle call form xTaskCreate.
    */
    Potentiometry* pt = static_cast<Potentiometry*>(arg);
    pt->cycle();
  }

  Potentiometry::Potentiometry(Circuit &circuit, MyLed &greenLed, MyLed &yellowLed, MyLed &redLed) {
    pCircuit = &circuit;
    gLed = &greenLed;
    yLed = &yellowLed;
    rLed = &redLed;
  }

  void  Potentiometry::begin() {
    xTaskCreate(ptCycleWrapper, "potentiometry", 4092, this, 2, &task);
  }

  void  Potentiometry::cycle() {
    /*
    Cycle loop for the potentiometry.
    */
    vTaskSuspend(task);
    while (true) {
      stop = false;
      start();
      while (millis() - initTime < duration && !stop) {
        pCircuit->readAndTransmit(PT_CMD);
        gLed->resetTime();
        yLed->resetTime();
        rLed->resetTime();
        delay(taskDelay);
      }
      float raw, filtered;
      pCircuit->readWECurrent(raw, filtered);
      ledsResult();
      stop = false;
      pCircuit->setWEVoltage(0.0);
      Serial.println(PT_CMD + END_CMD + String(filtered, 3));
      vTaskSuspend(task);
    }
  }

  void  Potentiometry::processCmd(String &cmd) {
    /*
    Process potentiometry commands.
    Ex: $PT$START
    */
    String result = "";
    if (cmd.substring(0, PT_CMD.length()) == PT_CMD) {
      cmd = cmd.substring(PT_CMD.length());
      while (true) {
        if (cmd.substring(0, START_CMD.length()) == START_CMD) {
          cmd = cmd.substring(START_CMD.length());
          result += "$OK->" + PT_CMD + START_CMD + "\n";
          vTaskResume(task);
        }
        else if (cmd.substring(0, STOP_CMD.length()) == STOP_CMD) {
          stop = true;
          cmd = cmd.substring(STOP_CMD.length());
          result += "$OK->" + PT_CMD + STOP_CMD + "\n";
        }
        else if (cmd.substring(0, TASK_DELAY_CMD.length()) == TASK_DELAY_CMD) {
          cmd = cmd.substring(TASK_DELAY_CMD.length());
          taskDelay = (uint32_t)parseDecimal(cmd);
          result += "$OK->" + PT_CMD + TASK_DELAY_CMD + String(taskDelay) + "\n";
        }
        else if (cmd.substring(0, VOLTAGE_SETPOINT_CMD.length()) == VOLTAGE_SETPOINT_CMD) {
          cmd = cmd.substring(VOLTAGE_SETPOINT_CMD.length());
          voltageSP = parseDecimal(cmd);
          result += "$OK->" + PT_CMD + VOLTAGE_SETPOINT_CMD + String(voltageSP, 3) + "\n";
        }
        else if (cmd.substring(0, DURATION_CMD.length()) == DURATION_CMD) {
          cmd = cmd.substring(DURATION_CMD.length());
          duration = (uint32_t)parseDecimal(cmd);
          result += "$OK->" + PT_CMD + DURATION_CMD + String(duration) + "\n";
        }
        else if (cmd.substring(0, THRESHOLD_CMD.length()) == THRESHOLD_CMD) {
          cmd = cmd.substring(THRESHOLD_CMD.length());
          startThreshold = parseDecimal(cmd);
          result += "$OK->" + PT_CMD + THRESHOLD_CMD + String(startThreshold, 3) + "\n";
        }
        else if (cmd.substring(0, RED_LIMIT_CMD.length()) == RED_LIMIT_CMD) {
          cmd = cmd.substring(RED_LIMIT_CMD.length());
          redLimit = parseDecimal(cmd);
          result += "$OK->" + PT_CMD + RED_LIMIT_CMD + String(redLimit, 3) + "\n";
        }
        else if (cmd.substring(0, YELLOW_LIMIT_CMD.length()) == YELLOW_LIMIT_CMD) {
          cmd = cmd.substring(YELLOW_LIMIT_CMD.length());
          yellowLimit = parseDecimal(cmd);
          result += "$OK->" + PT_CMD + YELLOW_LIMIT_CMD + String(yellowLimit, 3) + "\n";
        }
        else if (cmd.substring(0, PARAMS_CMD.length()) == PARAMS_CMD) {
          cmd = cmd.substring(PARAMS_CMD.length());
          result += PT_CMD + PARAMS_CMD + TASK_DELAY_CMD + String(taskDelay) + VOLTAGE_SETPOINT_CMD + String(voltageSP, 3) + DURATION_CMD + String(duration) + THRESHOLD_CMD + String(startThreshold, 3) + RED_LIMIT_CMD + String(redLimit, 3) + YELLOW_LIMIT_CMD + String(yellowLimit, 3) + "\n";
        }
        else {
          break;
        }
      }
      Serial.print(result);
    }
  }

  void  Potentiometry::start() {
    /*
    Check if the sample is on the sensor.
    If there is any sample, the current will flow.
    */
    pCircuit->resetFilter();
    pCircuit->setWEVoltage(voltageSP);
    yLed->blink(2, (taskDelay * 2) / 1000., 0);
    float raw, filtered;
    pCircuit->readWECurrent(raw, filtered);
    while (abs(filtered) < startThreshold && !stop) {
      yLed->resetTime();
      delay(taskDelay);
      pCircuit->readWECurrent(raw, filtered);
    }
    initTime = millis();
    rLed->blink(1, (taskDelay * 2) / 1000., 0.);
    gLed->blink(1, (taskDelay * 2) / 1000., 0.25);
    yLed->blink(1, (taskDelay * 2) / 1000., 0.5);
    Serial.println(PT_CMD + START_CMD);
  }

  void  Potentiometry::ledsResult() {
    /*
    Show result on the board leds
    */
    float raw, filtered;
    pCircuit->readWECurrent(raw, filtered);
    if (filtered >= redLimit) {
      rLed->blink(float(stop * 3), 5., 0.);
    } else if (filtered >= yellowLimit) {
      yLed->blink(float(stop * 3), 5., 0.);
    } else {
      gLed->blink(float(stop * 3), 5., 0.);
    }
  }

  /**************** CYCLIC VOLTAMMETRY ****************/

  void  cvCycleWrapper(void * arg) {
    /*
    Wrapper for the cycle call form xTaskCreate.
    */
    CyclicVoltammetry* cv = static_cast<CyclicVoltammetry*>(arg);
    cv->cycle();
  }

  CyclicVoltammetry::CyclicVoltammetry(Circuit &myCircuit, MyLed &greenLed, MyLed &yellowLed, MyLed &redLed) {
    pCircuit = &myCircuit;
    gLed = &greenLed;
    yLed = &yellowLed;
    rLed = &redLed;
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
      stop = false;
      start();
      while (currentCycle < totalCycles && !stop) {
        pCircuit->readAndTransmit(CV_CMD + CURRENT_CYCLE_CMD + String(currentCycle + 1) + ",");
        changeVoltage();
        gLed->resetTime();
        yLed->resetTime();
        rLed->resetTime();
        delay(taskDelay);
      }
      ledsResult();
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
      while (true) {
        if (cmd.substring(0, START_CMD.length()) == START_CMD) {
          cmd = cmd.substring(START_CMD.length());
          result += "$OK->" + CV_CMD + START_CMD + "\n";
          vTaskResume(task);
        }
        else if (cmd.substring(0, STOP_CMD.length()) == STOP_CMD) {
          stop = true;
          cmd = cmd.substring(STOP_CMD.length());
          result += "$OK->" + CV_CMD + STOP_CMD + "\n";
        }
        else if (cmd.substring(0, TASK_DELAY_CMD.length()) == TASK_DELAY_CMD) {
          cmd = cmd.substring(TASK_DELAY_CMD.length());
          taskDelay = (uint32_t)parseDecimal(cmd);
          result += "$OK->" + CV_CMD + TASK_DELAY_CMD + String(taskDelay) + "\n";
        }
        else if (cmd.substring(0, TOTAL_CYCLES_CMD.length()) == TOTAL_CYCLES_CMD) {
          cmd = cmd.substring(TOTAL_CYCLES_CMD.length());
          totalCycles = (uint8_t)parseDecimal(cmd);
          result += "$OK->" + CV_CMD + TOTAL_CYCLES_CMD + String(totalCycles) + "\n";
        }
        else if (cmd.substring(0, SLEW_RATE_CMD.length()) == SLEW_RATE_CMD) {
          cmd = cmd.substring(SLEW_RATE_CMD.length());
          slewRate = parseDecimal(cmd);
          result += "$OK->" + CV_CMD + SLEW_RATE_CMD + String(slewRate, 3) + "\n";
        }
        else if (cmd.substring(0, START_VOLTAGE_CMD.length()) == START_VOLTAGE_CMD) {
          cmd = cmd.substring(START_VOLTAGE_CMD.length());
          startVoltage = parseDecimal(cmd);
          result += "$OK->" + CV_CMD + START_VOLTAGE_CMD + String(startVoltage, 3) + "\n";
        }
        else if (cmd.substring(0, STOP_VOLTAGE_CMD.length()) == STOP_VOLTAGE_CMD) {
          cmd = cmd.substring(STOP_VOLTAGE_CMD.length());
          stopVoltage = parseDecimal(cmd);
          result += "$OK->" + CV_CMD + STOP_VOLTAGE_CMD + String(stopVoltage, 3) + "\n";
        }
        else if (cmd.substring(0, PEAK_VOLTAGE_CMD.length()) == PEAK_VOLTAGE_CMD) {
          cmd = cmd.substring(PEAK_VOLTAGE_CMD.length());
          peakVoltage = parseDecimal(cmd);
          result += "$OK->" + CV_CMD + PEAK_VOLTAGE_CMD + String(peakVoltage, 3) + "\n";
        }
        else if (cmd.substring(0, RED_LIMIT_CMD.length()) == RED_LIMIT_CMD) {
          cmd = cmd.substring(RED_LIMIT_CMD.length());
          redLimit = parseDecimal(cmd);
          result += "$OK->" + CV_CMD + RED_LIMIT_CMD + String(redLimit, 3) + "\n";
        }
        else if (cmd.substring(0, YELLOW_LIMIT_CMD.length()) == YELLOW_LIMIT_CMD) {
          cmd = cmd.substring(YELLOW_LIMIT_CMD.length());
          yellowLimit = parseDecimal(cmd);
          result += "$OK->" + CV_CMD + YELLOW_LIMIT_CMD + String(yellowLimit, 3) + "\n";
        }
        else if (cmd.substring(0, PARAMS_CMD.length()) == PARAMS_CMD) {
          cmd = cmd.substring(PARAMS_CMD.length());
          result += CV_CMD + PARAMS_CMD + TASK_DELAY_CMD + String(taskDelay) + TOTAL_CYCLES_CMD + String(totalCycles) + SLEW_RATE_CMD + String(slewRate, 3) + START_VOLTAGE_CMD + String(startVoltage, 3) + STOP_VOLTAGE_CMD + String(stopVoltage, 3) + PEAK_VOLTAGE_CMD + String(peakVoltage, 3) + RED_LIMIT_CMD + String(redLimit, 3) + YELLOW_LIMIT_CMD + String(yellowLimit, 3) + "\n";
        }
        else {
          break;
        }
      }
      Serial.print(result);
    }
  }

  void  CyclicVoltammetry::start() {
    /*
    Set the conditions for the start of the cyclic voltammetry.
    */
    pCircuit->resetFilter();
    currentCycle = 0;
    direction = 1;
    rLed->blink(1, (taskDelay * 2) / 1000., 0.);
    gLed->blink(1, (taskDelay * 2) / 1000., 0.25);
    yLed->blink(1, (taskDelay * 2) / 1000., 0.5);
    currentVoltage = startVoltage;
    pCircuit->setWEVoltage(currentVoltage);
    lastVoltChange = millis();
  }

  void  CyclicVoltammetry::ledsResult() {
    float value = 0;
    if (value >= redLimit) {
      rLed->blink(float(stop * 3), 5., 0.);
    } else if (value >= yellowLimit) {
      yLed->blink(float(stop * 3), 5., 0.);
    } else {
      gLed->blink(float(stop * 3), 5., 0.);
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

  SquareWaveVoltammetry::SquareWaveVoltammetry(Circuit &myCircuit, MyLed &greenLed, MyLed &yellowLed, MyLed &redLed) {
    pCircuit = &myCircuit;
    gLed = &greenLed;
    yLed = &yellowLed;
    rLed = &redLed;
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
      stop = false;
      start();
      while (!checkEnd() && !stop) {
        transmit();
        changeVoltage();
        gLed->resetTime();
        yLed->resetTime();
        rLed->resetTime();
        delay(taskDelay);
      }
      ledsResult();
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
      while (true) {
        if (cmd.substring(0, START_CMD.length()) == START_CMD) {
          cmd = cmd.substring(START_CMD.length());
          result += "$OK->" + SWV_CMD + START_CMD + "\n";
          vTaskResume(task);
        }
        else if (cmd.substring(0, STOP_CMD.length()) == STOP_CMD) {
          stop = true;
          cmd = cmd.substring(STOP_CMD.length());
          result += "$OK->" + SWV_CMD + STOP_CMD + "\n";
        }
        else if (cmd.substring(0, TASK_DELAY_CMD.length()) == TASK_DELAY_CMD) {
          cmd = cmd.substring(TASK_DELAY_CMD.length());
          taskDelay = (uint32_t)parseDecimal(cmd);
          result += "$OK->" + SWV_CMD + TASK_DELAY_CMD + String(taskDelay) + "\n";
        }
        else if (cmd.substring(0, START_VOLTAGE_CMD.length()) == START_VOLTAGE_CMD) {
          cmd = cmd.substring(START_VOLTAGE_CMD.length());
          startVoltage = parseDecimal(cmd);
          result += "$OK->" + SWV_CMD + START_VOLTAGE_CMD + String(startVoltage, 3) + "\n";
        }
        else if (cmd.substring(0, STOP_VOLTAGE_CMD.length()) == STOP_VOLTAGE_CMD) {
          cmd = cmd.substring(STOP_VOLTAGE_CMD.length());
          stopVoltage = parseDecimal(cmd);
          result += "$OK->" + SWV_CMD + STOP_VOLTAGE_CMD + String(stopVoltage, 3) + "\n";
        }
        else if (cmd.substring(0, STEP_SIZE_CMD.length()) == STEP_SIZE_CMD) {
          cmd = cmd.substring(STEP_SIZE_CMD.length());
          stepSize = parseDecimal(cmd);
          result += "$OK->" + SWV_CMD + STEP_SIZE_CMD + String(stepSize, 3) + "\n";
        }
        else if (cmd.substring(0, PULSE_AMPLITUDE_CMD.length()) == PULSE_AMPLITUDE_CMD) {
          cmd = cmd.substring(PULSE_AMPLITUDE_CMD.length());
          pulseAmplitude = parseDecimal(cmd);
          result += "$OK->" + SWV_CMD + PULSE_AMPLITUDE_CMD + String(pulseAmplitude, 3) + "\n";
        }
        else if (cmd.substring(0, FREQUENCY_CMD.length()) == FREQUENCY_CMD) {
          cmd = cmd.substring(FREQUENCY_CMD.length());
          frequency = parseDecimal(cmd);
          result += "$OK->" + SWV_CMD + FREQUENCY_CMD + String(frequency, 3) + "\n";
        }
        else if (cmd.substring(0, MAX_CURRENT_CMD.length()) == MAX_CURRENT_CMD) {
          cmd = cmd.substring(MAX_CURRENT_CMD.length());
          maxCurrent = parseDecimal(cmd);
          result += "$OK->" + SWV_CMD + MAX_CURRENT_CMD + String(maxCurrent, 3) + "\n";
        }
        else if (cmd.substring(0, EQUIL_TIME_CMD.length()) == EQUIL_TIME_CMD) {
          cmd = cmd.substring(EQUIL_TIME_CMD.length());
          equilTime = (uint32_t)parseDecimal(cmd);
          result += "$OK->" + SWV_CMD + EQUIL_TIME_CMD + String(equilTime) + "\n";
        }
        else if (cmd.substring(0, RED_LIMIT_CMD.length()) == RED_LIMIT_CMD) {
          cmd = cmd.substring(RED_LIMIT_CMD.length());
          redLimit = parseDecimal(cmd);
          result += "$OK->" + SWV_CMD + RED_LIMIT_CMD + String(redLimit, 3) + "\n";
        }
        else if (cmd.substring(0, YELLOW_LIMIT_CMD.length()) == YELLOW_LIMIT_CMD) {
          cmd = cmd.substring(YELLOW_LIMIT_CMD.length());
          yellowLimit = parseDecimal(cmd);
          result += "$OK->" + SWV_CMD + YELLOW_LIMIT_CMD + String(yellowLimit, 3) + "\n";
        }
        else if (cmd.substring(0, PARAMS_CMD.length()) == PARAMS_CMD) {
          cmd = cmd.substring(PARAMS_CMD.length());
          result += SWV_CMD + PARAMS_CMD + TASK_DELAY_CMD + String(taskDelay) + START_VOLTAGE_CMD + String(startVoltage, 3) + STOP_VOLTAGE_CMD + String(stopVoltage, 3) + STEP_SIZE_CMD + String(stepSize, 3) + PULSE_AMPLITUDE_CMD + String(pulseAmplitude, 3) + FREQUENCY_CMD + String(frequency, 3) + MAX_CURRENT_CMD + String(maxCurrent, 3) + EQUIL_TIME_CMD + String(equilTime) + RED_LIMIT_CMD + String(redLimit, 3) + YELLOW_LIMIT_CMD + String(yellowLimit, 3) + "\n";
        }
        else {
          break;
        }
      }
      Serial.print(result);
    }
  }

  void  SquareWaveVoltammetry::start() {
    /*
    Set the conditions for the start of the square wave voltammetry.
    */
    pCircuit->resetFilter();
    currentVoltage = startVoltage;
    yLed->blink(2, equilTime, 0);
    initTime = millis();
    while ((millis() - initTime) <= (equilTime)) {
      pCircuit->setWEVoltage(startVoltage);
      delay(taskDelay);
    }
    rLed->blink(1, (taskDelay * 2) / 1000., 0.);
    gLed->blink(1, (taskDelay * 2) / 1000., 0.25);
    yLed->blink(1, (taskDelay * 2) / 1000., 0.5);
    currentVoltage = startVoltage;
    pCircuit->setWEVoltage(currentVoltage);
    vFordward = 0.0;
    iFordward = 0.0;
    vReverse = 0.0;
    iReverse = 0.0;
    initTime = millis();
  }

  void  SquareWaveVoltammetry::ledsResult() {
    float value = iFordward - iReverse;
    if (value >= redLimit) {
      rLed->blink(float(stop * 3), 5., 0.);
    } else if (value >= yellowLimit) {
      yLed->blink(float(stop * 3), 5., 0.);
    } else {
      gLed->blink(float(stop * 3), 5., 0.);
    }
  }

  void  SquareWaveVoltammetry::changeVoltage() {
    /*
    Calculate next step and change voltage.
    */
    uint32_t now = millis();
    float elapsedTime = float(now - initTime);
    float msPeriod = (1. / frequency) * 1000.;
    float vStair = float(stepSize) * float(int(elapsedTime / msPeriod));
    float vPulse = float(pulseAmplitude) * float(int(elapsedTime / (msPeriod / 2)) % 2);
    float raw, filtered;
    pCircuit->readWECurrent(raw, filtered);
    if (currentVoltage < vStair + vPulse + startVoltage) {
      iReverse = filtered;
      vReverse = currentVoltage;
    }
    if (currentVoltage > vStair + vPulse + startVoltage) {
      iFordward = filtered;
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
    Serial.print(vFordward, 3);
    Serial.print(",");
    Serial.print(FORDWARD_CURRENT_CMD);
    Serial.print(iFordward, 3);
    Serial.print(",");
    Serial.print(REVERSE_VOLTAGE_CMD);
    Serial.print(vReverse, 3);
    Serial.print(",");
    Serial.print(REVERSE_CURRENT_CMD);
    Serial.print(iReverse, 3);
    Serial.print(",");
    Serial.print(DIFF_CURRENT_CMD);
    Serial.print(iFordward - iReverse, 3);
    Serial.println();
  }

  bool  SquareWaveVoltammetry::checkEnd() {
    /*
    Check the conditions os the end of the square wave voltammetry.
    */
    return (currentVoltage >= stopVoltage || iFordward >= maxCurrent || iReverse >= maxCurrent);
  }

#endif  //#if defined(ARDUINO_ESP32_DEV)