#ifndef   COMMANDS_H

  #define   COMMANDS_H

  // Global commands
  #define   PARAMS_CMD              String("$PARAMS")
  #define   START_CMD               String("$START")
  #define   STOP_CMD                String("$STOP")
  #define   END_CMD                 String("$END")
  #define   TIMESTAMP_CMD           String("$TS:")
  #define   VOLTAGE_CMD             String("$V:")
  #define   CURRENT_CMD             String("$A:")
  #define   TASK_DELAY_CMD          String("$TD:")
  #define   START_VOLTAGE_CMD       String("$SRTV:")
  #define   STOP_VOLTAGE_CMD        String("$STPV:")
  #define   RED_LIMIT_CMD           String("$RL:")
  #define   YELLOW_LIMIT_CMD        String("$YL:")
  // Potentiometry commands
  #define   PT_CMD                  String("$PT")
  #define   VOLTAGE_SETPOINT_CMD    String("$VSP:")
  #define   DURATION_CMD            String("$D:")
  #define   THRESHOLD_CMD           String("$TH:")
  // Cyclic Voltammetry commands
  #define   CV_CMD                  String("$CV")
  #define   CURRENT_CYCLE_CMD       String("$CC:")
  #define   TOTAL_CYCLES_CMD        String("$TC:")
  #define   SLEW_RATE_CMD           String("$SR:")
  #define   PEAK_VOLTAGE_CMD        String("$PV:")
  // Square Wave Voltammetry commands
  #define   SWV_CMD                 String("$SWV")
  #define   STEP_SIZE_CMD           String("$SS:")
  #define   PULSE_AMPLITUDE_CMD     String("$PA:")
  #define   FREQUENCY_CMD           String("$FQ:")
  #define   MAX_CURRENT_CMD         String("$MC:")
  #define   EQUIL_TIME_CMD          String("$ET:")
  #define   FORDWARD_VOLTAGE_CMD    String("$FV:")
  #define   FORDWARD_CURRENT_CMD    String("$FC:")
  #define   REVERSE_VOLTAGE_CMD     String("$RV:")
  #define   REVERSE_CURRENT_CMD     String("$RC:")
  #define   DIFF_CURRENT_CMD        String("$DC:")
  // Circuit commands
  #define   CIR_CMD                 String("$CIR")
  #define   R1_CMD                  String("$R1:")
  #define   R2_CMD                  String("$R2:")
  #define   R3_CMD                  String("$R3:")
  #define   R4_CMD                  String("$R4:")
  #define   R5_CMD                  String("$R5:")
  #define   R6_CMD                  String("$R6:")
  #define   VB1_CMD                 String("$VB1:")
  #define   VB2_CMD                 String("$VB2:")
  #define   OPAMP_VCC_P_CMD         String("$OPAMP_VCC_P:")
  #define   OPAMP_VCC_N_CMD         String("$OPAMP_VCC_N:")
  #define   OPAMP_HR_CMD            String("$OPAMP_HR:")
  #define   OPAMP_BR_CMD            String("$OPAMP_BR:")

#endif  //#ifndef   COMMANDS_H
