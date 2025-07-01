from typing import Any, Callable, NoReturn

from managers import (CyclicVoltammetryManager, PotentiometryManager,
                      SerialManager)
from PyQt5.QtCore import QCoreApplication, QTranslator, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from pyUtils import (ConfigDict, ConfigFileManager, ProjectPathsDict, debugLog,
                     infoLog, ppaths)
from ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    strReceived = pyqtSignal(str, name= 'strReceived', arguments= ['string'])
    
    def __init__(self, *args, **kwargs) -> None:
        QMainWindow.__init__(self, *args, **kwargs)
        self.app: QCoreApplication = QApplication.instance()
        self.translator = QTranslator(self.app)
        debugLog('Creating main window')
        self.cfg = ConfigFileManager(ppaths[ProjectPathsDict.CONFIG_FILE_PATH])
        self.setupUi(self)
        self.initWidgets()
        self.setCallbacks()
        self.debug(f'{self.cfg.app.name}-V{self.cfg.app.version}', infoLog)

    def _exit(self) -> NoReturn:
        self.debug(self.tr('Exit program...'), infoLog)
        exit(0)

    def debug(self, msg: Any, lvl: Callable = debugLog) -> None:
        lvl(msg)
        if lvl == infoLog:
            self.statusbar.showMessage(str(msg))

    def initWidgets(self) -> None:
        self.initSerialManager()
        self.initCyclesManager()

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

    def setCallbacks(self) -> None:
        self.strReceived.connect(lambda rcvStr: self.parseCmd(rcvStr))
        self.actionSpanish.triggered.connect(lambda: self.changeLanguage('es_ES'))
        self.actionPortugues.triggered.connect(lambda: self.changeLanguage('pt_PT'))
        self.actionEnglish.triggered.connect(lambda: self.changeLanguage('en_GB'))

    def sendInitCmds(self) -> None:
        ...

    def parseCmd(self, rcvStr: str) -> None:
        cmds: ConfigDict = self.cfg.serial.commands
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
        ...

    def changeLanguage(self, language: str = 'es_ES') -> None:
        if self.translator.load(language, ':/translations'):
            self.app.installTranslator(self.translator)
        else:
            self.app.removeTranslator(self.translator)
        self.retranslateUi(self)
