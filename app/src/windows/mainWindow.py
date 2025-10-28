import csv
from pathlib import Path
from pickle import load
from typing import Any, Callable, NoReturn

from managers import (CalculatorManager, CircuitManager,
                      CyclicVoltammetryManager, PotentiometryManager,
                      SerialManager)
from PyQt5.QtCore import QCoreApplication, QTranslator, pyqtSignal
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow
from pyUtils import ConfigDict
from ui import Ui_MainWindow
from utils import MY_APP, MY_CFG, my_logger
from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet


class MainWindow(QMainWindow, Ui_MainWindow):
    strReceived = pyqtSignal(str, name= 'strReceived')
    
    def __init__(self, *args, **kwargs) -> None:
        QMainWindow.__init__(self, *args, **kwargs)
        self.app: QCoreApplication = QApplication.instance()
        self.translator = QTranslator(self.app)
        my_logger.debug('Creating main window')
        self.setupUi(self)
        self.initWidgets()
        self.setCallbacks()
        self.debug(f'{MY_CFG.app.name}-V{MY_CFG.app.version}', my_logger.info)

    def _exit(self) -> NoReturn:
        self.debug(self.tr('Exit program...'), my_logger.info)
        exit(0)

    def debug(self, msg: Any, lvl: Callable = my_logger.debug) -> None:
        lvl(msg)
        if lvl == my_logger.info:
            self.statusbar.showMessage(str(msg))

    def initWidgets(self) -> None:
        self.initSerialManager()
        self.initCyclesManager()
        self.initCircuitManager()
        self.initCalculatorManager()

    def initSerialManager(self) -> None:
        self.serialManager = SerialManager(
            self,
            self.actionUpdateDevices,
            self.actionConnectDevice,
            self.comSelector,
            self.comStatusField,
            self.customCmdValue,
            self.customCmdButton,
            self.rcvCmds
        )
        self.serialManager.init()
        self.sendCmd: Callable = self.serialManager.sendCmd

    def initCyclesManager(self) -> None:
        self.cycles: dict = {
            'potentiometry': PotentiometryManager(
                self,
                self.ptButton,
                self.ptTDValue,
                self.ptTDButton,
                self.ptSPValue,
                self.ptSPButton,
                self.ptTimeValue,
                self.ptTimeButton,
                self.ptThresholdValue,
                self.ptThresholdButton,
                self.ptPlayButton,
                self.ptSaveButton,
                self.ptLoadButton,
                self.ptCloseButton,
                self.ptPlotView
            ),
            'cyclicVoltammetry': CyclicVoltammetryManager(
                self,
                self.cvButton,
                self.cvTDValue,
                self.cvTDButton,
                self.cvTCValue,
                self.cvTCButton,
                self.cvSRValue,
                self.cvSRButton,
                self.cvStartVValue,
                self.cvStartVButton,
                self.cvPVValue,
                self.cvPVButton,
                self.cvStopVValue,
                self.cvStopVButton,
                self.cvPlayButton,
                self.cvSaveButton,
                self.cvLoadButton,
                self.cvCloseButton,
                self.cvPlotView
            )
        }
        for cycle in self.cycles.values():
            cycle.init()

    def initCircuitManager(self) -> None:
        self.circuitManager = CircuitManager(
            self,
            self.circuitButton,
            self.r1Value,
            self.r1Button,
            self.r2Value,
            self.r2Button,
            self.r3Value,
            self.r3Button,
            self.r4Value,
            self.r4Button,
            self.r5Value,
            self.r5Button,
            self.r6Value,
            self.r6Button,
            self.vb1Value,
            self.vb1Button,
            self.vb2Value,
            self.vb2Button,
            self.opampVccPValue,
            self.opampVccPButton,
            self.opampVccNValue,
            self.opampVccNButton,
            self.opampHRValue,
            self.opampHRButton,
            self.opampBRValue,
            self.opampBRButton,
            self.vRangeMinValue,
            self.vRangeMaxValue,
            self.cRangeMinValue,
            self.cRangeMaxValue,
            self.boardSelector
        )
        self.circuitManager.init()

    def initCalculatorManager(self) -> None:
        self.calculatorManager = CalculatorManager(
            self,
            self.vCalcMinValue,
            self.vCalcMaxValue,
            self.r2CalcValue,
            self.r3CalcValue,
            self.r4CalcValue,
            self.cCalcMinValue,
            self.cCalcMaxValue,
            self.r5CalcValue,
            self.r6CalcValue,
            self.calcBoardSelector
        )
        self.calculatorManager.init()

    def setCallbacks(self) -> None:
        self.strReceived.connect(lambda rcvStr: self.parseCmd(rcvStr))
        self.actionSpanish.triggered.connect(lambda: self.changeLanguage('es_ES'))
        self.actionPortugues.triggered.connect(lambda: self.changeLanguage('pt_PT'))
        self.actionEnglish.triggered.connect(lambda: self.changeLanguage('en_GB'))
        self.actionExport.triggered.connect(lambda: self.actionExportTriggered())

    def sendInitCmds(self) -> None:
        ...

    def parseCmd(self, rcvStr: str) -> None:
        cmds: ConfigDict = MY_CFG.serial.commands
        while rcvStr.startswith(cmds.ok):
            rcvStr = rcvStr[len(cmds.ok):]
        while rcvStr.startswith(cmds.potentiometry):
            rcvStr = rcvStr[len(cmds.potentiometry):]
            self.cycles['potentiometry'].processCmd(rcvStr)
        while rcvStr.startswith(cmds.cyclicVoltammetry):
            rcvStr = rcvStr[len(cmds.cyclicVoltammetry):]
            self.cycles['cyclicVoltammetry'].processCmd(rcvStr)

    def enableSend(self, flag: bool) -> None:
        self.serialManager.enableSend(flag)
        for cycle in self.cycles.values():
            cycle.enableSend(flag)
        self.circuitManager.enableSend(flag)

    def changeLanguage(self, language: str = 'es_ES') -> None:
        if self.translator.load(language, ':/translations'):
            self.app.installTranslator(self.translator)
        else:
            self.app.removeTranslator(self.translator)
        self.retranslateUi(self)

    def actionExportTriggered(self) -> None:
        dataFile = Path(
            QFileDialog.getOpenFileName(
                caption = self.tr('Select test to export'),
                directory = str(MY_APP['DATA']),
                filter = self.tr(f'Data (*.pt; *.cv)')
            )[0]
        )
        exportFile = Path(
            QFileDialog.getSaveFileName(
                caption = self.tr('Export file'),
                directory = str(MY_APP['DATA']),
                filter = self.tr(f'(*.csv);;(*.xlsx)')
            )[0]
        )
        self.exportData(dataFile, exportFile)

    def exportData(self, dataFile: Path, exportFile: Path) -> None:
        with open(dataFile, 'rb') as f:
            data: dict = load(f)
        match exportFile.suffix:
            case '.csv':
                self.exportCSV(data, exportFile)
            case '.xlsx':
                self.exportXLSX(data, exportFile)
        self.debug(self.tr('Data exported'), my_logger.info)

    def exportCSV(self, data: dict, exportFile: Path) -> None:
        with open(exportFile,
                  mode= 'w',
                  newline= '',
                  encoding= 'utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(data.keys())
            writer.writerows(zip(*data.values()))

    def exportXLSX(self, data: dict, exportFile: Path) -> None:
        wb = Workbook(exportFile)
        ws: Worksheet = wb.add_worksheet('Data')
        for col, key in enumerate(data.keys()):
            ws.write(0, col, key)
        for col, values in enumerate(data.values()):
            for row, value in enumerate(values):
                ws.write(row + 1, col, value)
        wb.close()
