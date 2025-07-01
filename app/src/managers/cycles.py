from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from numbers import Number
from typing import TYPE_CHECKING, Callable, ClassVar, Optional

from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtWidgets import QDoubleSpinBox, QGridLayout, QPushButton, QSpinBox
from pyqtgraph import (DateAxisItem, LabelItem, LegendItem, PlotCurveItem,
                       PlotWidget)
from pyUtils import ConfigDict, ConfigFileManager, ProjectPathsDict, ppaths

if TYPE_CHECKING:
    from ..windows import MainWindow


@dataclass
class PotentiometryManager:
    parent: MainWindow
    sendButton: QPushButton
    taskDelayValue: QSpinBox
    taskDelayButton: QPushButton
    voltageValue: QDoubleSpinBox
    voltageButton: QPushButton
    durationValue: QSpinBox
    durationButton: QPushButton
    thresholdValue: QDoubleSpinBox
    thresholdButton: QPushButton
    playButton: QPushButton
    plotView: QGridLayout
    tr: ClassVar[Callable] = partial(QCoreApplication.translate, 'PotentiometryManager')

    def __post_init__(self) -> None:
        cfg = ConfigFileManager(ppaths[ProjectPathsDict.CONFIG_FILE_PATH])
        self.cfg: ConfigDict = cfg.cycles.potentiometry
        self.cmds: ConfigDict = cfg.serial.commands
        self.pltCfg: ConfigDict = cfg.plot
        self._send: Callable = self.parent.sendCmd
        self.getTDCmd: partial[str] = partial(self.getConfigCmd, True, False, False, False)
        self.getVCmd: partial[str] = partial(self.getConfigCmd, False, True, False, False)
        self.getDCmd: partial[str] = partial(self.getConfigCmd, False, False, True, False)
        self.getThCmd: partial[str] = partial(self.getConfigCmd, False, False, False, True)
        self.plotTimer: QTimer = QTimer()

    def init(self) -> None:
        self.setWidgets()
        self.enableSend(False)
        self.setCallbacks()

    def setWidgets(self) -> None:
        self.taskDelayValue.setValue(self.cfg.taskDelay)
        self.voltageValue.setValue(self.cfg.voltageSP)
        self.durationValue.setValue(self.cfg.duration)
        self.thresholdValue.setValue(self.cfg.threshold)
        self.setPlot()

    def setPlot(self) -> None:
        self.plot: PlotWidget = PlotWidget(
            axisItems= {
                'bottom': DateAxisItem(utcOffet= 0)
            }
        )
        self.plot.showGrid(x= True, y= True)
        self.plot.showAxis('left')
        self.plot.showAxis('right')
        self.plot.setLabels(
            bottom= self.tr('Time (ms)'),
            left= self.tr('Voltage (V)'),
            right= self.tr('Current (uA)')
        )
        self.legend: LegendItem = self.plot.addLegend()
        self.plotView.addWidget(self.plot, 0, 0)
        self.resetPlot()

    def setCallbacks(self) -> None:
        self.sendButton.clicked.connect(lambda _: self._send(self.getConfigCmd()))
        self.taskDelayButton.clicked.connect(lambda _: self._send(self.getTDCmd()))
        self.voltageButton.clicked.connect(lambda _: self._send(self.getVCmd()))
        self.durationButton.clicked.connect(lambda _: self._send(self.getDCmd()))
        self.thresholdButton.clicked.connect(lambda _: self._send(self.getThCmd()))
        self.playButton.clicked.connect(lambda checked: self.playButtonClicked(checked))
        self.playButton.toggled.connect(lambda: self.playButtonToggled())
        self.plotTimer.timeout.connect(lambda: self.plotTimerTimeout())

    def enableSend(self, flag: bool = True) -> None:
        #self.sendButton.setEnabled(flag)   #TODO: Check why arduino only send one OK at a time
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
        v: str = f'{self.cmds.voltageSP}{self.voltageValue.value()}' * vFlag
        d: str = f'{self.cmds.duration}{self.durationValue.value()}' * dFlag
        th: str = f'{self.cmds.threshold}{self.thresholdValue.value()}' * thFlag
        return f'{header}{td}{v}{d}{th}'

    def playButtonClicked(self, checked: bool) -> None:
        self.playButton.setChecked(not checked)
        if checked:
            self._send(f'{self.cmds.potentiometry}{self.cmds.start}')
            self.resetPlot()
            self.plotTimer.start(self.pltCfg.updateInterval)
        else:
            self._send(f'{self.cmds.potentiometry}{self.cmds.stop}')

    def playButtonToggled(self) -> None:
        if self.playButton.isChecked():
            self.resetPlot()
            self.plotTimer.start(self.pltCfg.updateInterval)
        else:
            self.plotTimer.stop()

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
        self.playButton.setChecked(False)
        ... #TODO: Save test
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
        self.thresholdValue.setValue(float(value))
        self.cfg.threshold = float(value)
        return rcvStr

    def resetPlot(self) -> None:
        self.measures: dict[list[Optional[Number]]] = {
            'timestamp': [],
            'voltage': [],
            'current': []
        }
        self.lines: list[PlotCurveItem] = {
            'voltage' : self.plot.plot(
                self.measures['timestamp'],
                self.measures['voltage'],
                name = self.tr('Voltage'),
                color = self.pltCfg.colors[0],
                pen = f'#{self.pltCfg.colors[0]}',
                width = self.pltCfg.lineWidth
            ),
            'current' : self.plot.plot(
                self.measures['timestamp'],
                self.measures['current'],
                name = self.tr('Current'),
                color = self.pltCfg.colors[1],
                pen = f'#{self.pltCfg.colors[1]}',
                width = self.pltCfg.lineWidth
            )
        }

    def plotTimerTimeout(self) -> None:
        self.lines['voltage'].setData(
            self.measures['timestamp'],
            self.measures['voltage']
        )
        self.lines['current'].setData(
            self.measures['timestamp'],
            self.measures['current']
        )


@dataclass
class CyclicVoltammetryManager:
    parent: MainWindow
    sendButton: QPushButton
    taskDelayValue: QSpinBox
    taskDelayButton: QPushButton
    cyclesValue: QSpinBox
    cyclesButton: QPushButton
    slewRateValue: QDoubleSpinBox
    slewRateButton: QPushButton
    startVoltageValue: QDoubleSpinBox
    startVoltageButton: QPushButton
    peakVoltageValue: QDoubleSpinBox
    peakVoltageButton: QPushButton
    stopVoltageValue: QDoubleSpinBox
    stopVoltageButton: QPushButton
    playButton: QPushButton
    plotView: QGridLayout
    tr: ClassVar[Callable] = partial(QCoreApplication.translate, 'CyclicVoltammetryManager')

    def __post_init__(self) -> None:
        cfg = ConfigFileManager(ppaths[ProjectPathsDict.CONFIG_FILE_PATH])
        self.cfg: ConfigDict = cfg.cycles.cyclicVoltammetry
        self.cmds: ConfigDict = cfg.serial.commands
        self.pltCfg: ConfigDict = cfg.plot
        self._send: Callable = self.parent.sendCmd
        self.getTDCmd: partial[str] = partial(self.getConfigCmd, True, False, False, False, False, False)
        self.getTCCmd: partial[str] = partial(self.getConfigCmd, False, True, False, False, False, False)
        self.getSRCmd: partial[str] = partial(self.getConfigCmd, False, False, True, False, False, False)
        self.getStartVCmd: partial[str] = partial(self.getConfigCmd, False, False, False, True, False, False)
        self.getPeakVCmd: partial[str] = partial(self.getConfigCmd, False, False, False, False, True, False)
        self.getStopVCmd: partial[str] = partial(self.getConfigCmd, False, False, False, False, False, True)
        self.plotTimer: QTimer = QTimer()

    def init(self) -> None:
        self.setWidgets()
        self.enableSend(False)
        self.setCallbacks()

    def setWidgets(self) -> None:
        self.taskDelayValue.setValue(self.cfg.taskDelay)
        self.cyclesValue.setValue(self.cfg.cycles)
        self.slewRateValue.setValue(self.cfg.slewRate)
        self.startVoltageValue.setValue(self.cfg.startVoltage)
        self.peakVoltageValue.setValue(self.cfg.peakVoltage)
        self.stopVoltageValue.setValue(self.cfg.stopVoltage)
        self.setPlot()
    
    def setPlot(self) -> None:
        self.plot: PlotWidget = PlotWidget()
        self.plot.showGrid(x= True, y= True)
        self.plot.showAxis('left')
        self.plot.showAxis('right')
        self.plot.setLabels(
            left= self.tr('Current (uA)'),
            bottom= self.tr('Voltage (V)')
        )
        self.plotView.addWidget(self.plot, 0, 0)
        self.resetPlot()

    def setCallbacks(self) -> None:
        self.sendButton.clicked.connect(lambda _: self._send(self.getConfigCmd()))
        self.taskDelayButton.clicked.connect(lambda _: self._send(self.getTDCmd()))
        self.cyclesButton.clicked.connect(lambda _: self._send(self.getTCCmd()))
        self.slewRateButton.clicked.connect(lambda _: self._send(self.getSRCmd()))
        self.startVoltageButton.clicked.connect(lambda _: self._send(self.getStartVCmd()))
        self.peakVoltageButton.clicked.connect(lambda _: self._send(self.getPeakVCmd()))
        self.stopVoltageButton.clicked.connect(lambda _: self._send(self.getStopVCmd()))
        self.playButton.clicked.connect(lambda checked: self.playButtonClicked(checked))
        self.playButton.toggled.connect(lambda: self.playButtonToggled())
        self.plotTimer.timeout.connect(lambda: self.plotTimerTimeout())

    def enableSend(self, flag: bool = True) -> None:
        #self.sendButton.setEnabled(flag)   #TODO: Check why arduino only send one OK at a time
        self.taskDelayButton.setEnabled(flag)
        self.cyclesButton.setEnabled(flag)
        self.slewRateButton.setEnabled(flag)
        self.startVoltageButton.setEnabled(flag)
        self.peakVoltageButton.setEnabled(flag)
        self.stopVoltageButton.setEnabled(flag)
        self.playButton.setEnabled(flag)

    def getConfigCmd(
        self,
        tdFlag: bool = True,
        tcFlag: bool = True,
        srlag: bool = True,
        startVFlag: bool = True,
        peakVFlag: bool = True,
        stopVFlag: bool = True
    ) -> str:
        header: str = f'{self.cmds.cyclicVoltammetry}'
        td: str = f'{self.cmds.taskDelay}{self.taskDelayValue.value()}' * tdFlag
        tc: str = f'{self.cmds.totalCycle}{self.cyclesValue.value()}' * tcFlag
        sr: str = f'{self.cmds.slewRate}{self.slewRateValue.value()}' * srlag
        startV: str = f'{self.cmds.startVoltage}{self.startVoltageValue.value()}' * startVFlag
        peakV: str = f'{self.cmds.peakVoltage}{self.peakVoltageValue.value()}' * peakVFlag
        stopV: str = f'{self.cmds.stopVoltage}{self.stopVoltageValue.value()}' * stopVFlag
        return f'{header}{td}{tc}{sr}{startV}{peakV}{stopV}'

    def playButtonClicked(self, checked: bool) -> None:
        self.playButton.setChecked(not checked)
        if checked:
            self._send(f'{self.cmds.cyclicVoltammetry}{self.cmds.start}')
        else:
            self._send(f'{self.cmds.cyclicVoltammetry}{self.cmds.stop}')

    def playButtonToggled(self) -> None:
        if self.playButton.isChecked():
            self.resetPlot()
            self.plotTimer.start(self.pltCfg.updateInterval)
        else:
            self.plotTimer.stop()

    def processCmd(self, rcvStr: str) -> str:
        options: dict = {
            self.cmds.start: self.processStart,
            self.cmds.stop: self.processStop,
            self.cmds.end: self.processEnd,
            self.cmds.timestamp: self.processMeasure,
            self.cmds.taskDelay: self.saveTaskDelay,
            self.cmds.totalCycle: self.saveTotalCycle,
            self.cmds.slewRate: self.saveSlewRate,
            self.cmds.startVoltage: self.saveStartVoltage,
            self.cmds.peakVoltage: self.savePeakVoltage,
            self.cmds.stopVoltage: self.saveStopVoltage
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
        self.playButton.setChecked(False)
        ... #TODO: Save test
        return rcvStr

    def processMeasure(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.timestamp):]
        ts: str = rcvStr.split('$')[0]
        self.measures['timestamp'].append(int(ts))
        rcvStr = rcvStr[len(ts + self.cmds.voltage) + 1:]
        voltage: str = rcvStr.split('$')[0]
        self.measures['voltage'].append(float(voltage))
        rcvStr = rcvStr[len(voltage + self.cmds.current) + 1:]
        current: str = rcvStr.split('$')[0]
        self.measures['current'].append(float(current))
        rcvStr = rcvStr[len(current):]
        return rcvStr

    def saveTaskDelay(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.taskDelay):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.taskDelayValue.setValue(int(value))
        self.cfg.taskDelay = int(value)
        return rcvStr

    def saveTotalCycle(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.totalCycle):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.cyclesValue.setValue(int(value))
        self.cfg.cycles = int(value)
        return rcvStr

    def saveSlewRate(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.slewRate):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.slewRateValue.setValue(float(value))
        self.cfg.slewRate = float(value)
        return rcvStr

    def saveStartVoltage(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.startVoltage):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.startVoltageValue.setValue(float(value))
        self.cfg.startVoltage = float(value)
        return rcvStr

    def savePeakVoltage(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.peakVoltage):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.peakVoltageValue.setValue(float(value))
        self.cfg.peakVoltage = float(value)
        return rcvStr

    def saveStopVoltage(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.stopVoltage):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.stopVoltageValue.setValue(float(value))
        self.cfg.stopVoltage = float(value)
        return rcvStr

    def resetPlot(self) -> None:
        self.measures: dict[list[Optional[Number]]] = {
            'timestamp': [],
            'voltage': [],
            'current': []
        }
        self.line: PlotCurveItem = self.plot.plot(
            self.measures['voltage'],
            self.measures['current'],
            name = self.tr('Voltage/Current'),
            color = self.pltCfg.colors[0],
            pen = f'#{self.pltCfg.colors[0]}',
            width = self.pltCfg.lineWidth
        )

    def plotTimerTimeout(self) -> None:
        self.line.setData(
            self.measures['voltage'],
            self.measures['current']
        )
