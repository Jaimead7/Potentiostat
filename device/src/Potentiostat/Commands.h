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
  #define   START_VOLTAGE_CMD       String("$SRTV:")
  #define   PEAK_VOLTAGE_CMD        String("$PV:")
  #define   STOP_VOLTAGE_CMD        String("$STPV:")
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
