from typing import Any, Callable, NoReturn

from managers import PlotManager, SerialManager
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
        self.initPlotManager()

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

    def initPlotManager(self) -> None:
        self.plotManager = PlotManager(
            self,
            self.ptPlotView
        )
        self.plotManager.init()

    def setCallbacks(self) -> None:
        self.strReceived.connect(lambda rcvStr: self.parseCmd(rcvStr))
        self.actionSpanish.triggered.connect(lambda: self.changeLanguage('es_ES'))
        self.actionPortugues.triggered.connect(lambda: self.changeLanguage('pt_PT'))
        self.actionEnglish.triggered.connect(lambda: self.changeLanguage('en_GB'))

    def sendInitCmds(self) -> None:
        ...

    def parseCmd(self, rcvStr: str) -> None:
        cmds: ConfigDict = self.cfg.serial.commands
        # while rcvStr.startswith(''): #TODO
        #     rcvStr = rcvStr[len(' '):]
        #     ...

    def enableSend(self, flag: bool) -> None:
        self.serialManager.enableSend(flag)

    def changeLanguage(self, language: str = 'es_ES') -> None:
        if self.translator.load(language, ':/translations'):
            self.app.installTranslator(self.translator)
        else:
            self.app.removeTranslator(self.translator)
        self.retranslateUi(self)
        self.plotManager.setLabels(['Voltage', 'Current']) #FIXME
