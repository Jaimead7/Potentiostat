from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING, Callable, ClassVar

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QGridLayout, QLineEdit, QPushButton
from pyUtils import ConfigDict, ConfigFileManager, ProjectPathsDict, ppaths

if TYPE_CHECKING:
    from ..windows import MainWindow


@dataclass
class PotentiometryManager:
    parent: MainWindow
    button: QPushButton
    taskDelayValue: QLineEdit
    taskDelayButton: QPushButton
    voltageValue: QLineEdit
    voltageButton: QPushButton
    durationValue: QLineEdit
    durationButton: QPushButton
    thresholdValue: QLineEdit
    thresholdButton: QPushButton
    playButton: QPushButton
    plotView: QGridLayout
    tr: ClassVar[Callable] = partial(QCoreApplication.translate, 'PotentiometryManager')

    def __post_init__(self) -> None:
        cfg = ConfigFileManager(ppaths[ProjectPathsDict.CONFIG_FILE_PATH])
        self.cfg: ConfigDict = cfg.cycles.potentiometry
        self.cmds: ConfigDict = cfg.serial.commands
        self._send: Callable = self.parent.sendCmd
        self.getTDCmd: partial[str] = partial(self.getConfigCmd, True, False, False, False)
        self.getVCmd: partial[str] = partial(self.getConfigCmd, False, True, False, False)
        self.getDCmd: partial[str] = partial(self.getConfigCmd, False, False, True, False)
        self.getThCmd: partial[str] = partial(self.getConfigCmd, False, False, False, True)

    def init(self) -> None:
        self.setWidgets()
        self.enableSend(False)
        self.setCallbacks()

    def setWidgets(self) -> None:
        self.taskDelayValue.setValue(self.cfg.taskDelay)
        self.voltageValue.setValue(self.cfg.voltageSP)
        self.durationValue.setValue(self.cfg.duration)
        self.thresholdValue.setValue(self.cfg.threshold)

    def setCallbacks(self) -> None:
        self.taskDelayButton.clicked.connect(lambda _: self._send(self.getTDCmd()))
        self.voltageButton.clicked.connect(lambda _: self._send(self.getVCmd()))
        self.durationButton.clicked.connect(lambda _: self._send(self.getDCmd()))
        self.thresholdButton.clicked.connect(lambda _: self._send(self.getThCmd()))
        self.playButton.clicked.connect(lambda checked: self.playButtonClicked(checked))

    def enableSend(self, flag: bool = True) -> None:
        self.button.setEnabled(flag)
        self.taskDelayButton.setEnabled(flag)
        self.voltageButton.setEnabled(flag)
        self.durationButton.setEnabled(flag)
        self.thresholdButton.setEnabled(flag)
        self.playButton.setEnabled(flag)

    def getConfigCmd(
        self,
        tdFlag: bool = True,
        vFlag: bool = True,
        dFlag: bool = True,
        thFlag: bool = True
    ) -> str:
        header: str = f'{self.cmds.potentiometry}'
        td: str = f'{self.cmds.taskDelay}{self.taskDelayValue.value()}' * tdFlag
        v: str = f'{self.cmds.voltage}{self.voltageValue.value()}' * vFlag
        d: str = f'{self.cmds.duration}{self.durationValue.value()}' * dFlag
        th: str = f'{self.cmds.threshold}{self.thresholdValue.value()}' * thFlag
        return f'{header}{td}{v}{d}{th}'

    def playButtonClicked(self, checked: bool) -> None:
        self.playButton.setChecked(not checked)
        if checked:
            self._send(f'{self.cmds.potentiometry}{self.cmds.start}')
        else:
            self._send(f'{self.cmds.potentiometry}{self.cmds.stop}')

    def processCmd(self, rcvStr: str) -> str:
        options: dict = {
            self.cmds.start: self.processStart,
            self.cmds.stop: self.processStop,
            self.cmds.end: self.processEnd,
            self.cmds.timestamp: self.processMeasure,
            self.cmds.taskDelay: self.saveTaskDelay,
            self.cmds.voltageSP: self.saveVoltageSP,
            self.cmds.duration: self.saveDuration,
            self.cmds.threshold: self.saveThreshold
        }
        while rcvStr.startswith(tuple(options.keys())):
            for key in options.keys():
                if rcvStr.startswith(key):
                    rcvStr = options[key](rcvStr)
        return rcvStr

    def processStart(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.start):]
        self.playButton.setChecked(True)
        return rcvStr

    def processStop(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.stop):]
        self.playButton.setChecked(False)
        return rcvStr

    def processEnd(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.stop):]
        self.switch.setChecked(False)
        return rcvStr

    def processMeasure(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.timestamp):]
        ts: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(ts + self.cmds.voltage) + 1:]
        voltage: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(voltage + self.cmds.current) + 1:]
        current: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(current):]
        ... #TODO: save measure and plot
        return rcvStr

    def saveTaskDelay(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.taskDelay):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.taskDelayValue.setValue(int(value))
        self.cfg.taskDelay = int(value)
        return rcvStr

    def saveVoltageSP(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.voltageSP):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.voltageValue.setValue(float(value))
        self.cfg.voltageSP = float(value)
        return rcvStr

    def saveDuration(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.duration):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.durationValue.setValue(int(value))
        self.cfg.duration = int(value)
        return rcvStr

    def saveThreshold(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.threshold):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.thresholdValue.setValue(int(value))
        self.cfg.threshold = int(value)
        return rcvStr


@dataclass
class CyclicVoltammetryManager:
    parent: MainWindow
    ...
    tr: ClassVar[Callable] = partial(QCoreApplication.translate, 'CyclicVoltammetryManager')