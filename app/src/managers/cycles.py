from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from pathlib import Path
from pickle import dump, load
from typing import TYPE_CHECKING, Callable, ClassVar, Optional

from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtWidgets import (QDoubleSpinBox, QFileDialog, QGridLayout,
                             QPushButton, QSpinBox)
from pyqtgraph import LegendItem, PlotCurveItem, PlotWidget
from pyUtils import ConfigDict
from utils import MY_APP, MY_CFG

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
    saveButton: QPushButton
    loadButton: QPushButton
    closeButton: QPushButton
    plotView: QGridLayout
    tr: ClassVar[Callable] = partial(QCoreApplication.translate, 'PotentiometryManager')
    dataFileExtension: ClassVar[str] = '.pt'

    def __post_init__(self) -> None:
        self.cfg: ConfigDict = MY_CFG.cycles.potentiometry
        self.cmds: ConfigDict = MY_CFG.serial.commands
        self.pltCfg: ConfigDict = MY_CFG.plot
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
        self.plot: PlotWidget = PlotWidget()
        self.plot.showGrid(x= True, y= True)
        self.plot.showAxis('left')
        self.plot.showAxis('right')
        self.plot.setLabels(
            bottom= self.tr('Time (s)'),
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
        self.saveButton.clicked.connect(lambda _: self.saveButtonClicked())
        self.loadButton.clicked.connect(lambda _: self.loadButtonClicked())
        self.closeButton.clicked.connect(lambda _: self.closeButtonClicked())
        self.plotTimer.timeout.connect(lambda: self.plotTimerTimeout())

    def enableSend(self, flag: bool = True) -> None:
        self.sendButton.setEnabled(flag)
        self.taskDelayButton.setEnabled(flag)
        self.voltageButton.setEnabled(flag)
        self.durationButton.setEnabled(flag)
        self.thresholdButton.setEnabled(flag)
        self.playButton.setEnabled(flag)
        self.saveButton.setEnabled(flag)

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
        self.resetPlot()
        self.plotTimer.start(self.pltCfg.updateInterval)
        self.loadButton.setEnabled(False)
        self.closeButton.setEnabled(False)
        return rcvStr

    def processStop(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.stop):]
        self.playButton.setChecked(False)
        self.plotTimer.stop()
        self.loadButton.setEnabled(True)
        self.closeButton.setEnabled(True)
        return rcvStr

    def processEnd(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.stop):]
        self.playButton.setChecked(False)
        self.plotTimer.stop()
        return rcvStr

    def processMeasure(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.timestamp):]
        ts: str = rcvStr.split('$')[0][:-1]
        rcvStr = rcvStr[len(ts + self.cmds.voltage) + 1:]
        voltage: str = rcvStr.split('$')[0][:-1]
        rcvStr = rcvStr[len(voltage + self.cmds.current) + 1:]
        current: str = rcvStr.split('$')[0][:-1]
        rcvStr = rcvStr[len(current):]
        if len(self.measures['timestamp']) == 0:
            self.startTimestamp = int(ts)
        self.measures['timestamp'].append((int(ts) - self.startTimestamp) / 1000.0)
        self.measures['voltage'].append(float(voltage))
        self.measures['current'].append(float(current))
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
        self.measures: dict[str, list[Optional[int | float | complex]]] = {
            'timestamp': [],
            'voltage': [],
            'current': []
        }
        self.plot.clear()
        self.lines: dict[str, PlotCurveItem] = {
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

    def saveButtonClicked(self) -> None:
        fileName = Path(
            QFileDialog.getSaveFileName(
                caption = self.tr('Save test data'),
                directory = str(MY_APP['DATA']),
                filter = self.tr('Data (*.pt)')
            )[0]
        )
        with open(fileName, 'wb') as f:
            dump(self.measures, f)

    def loadButtonClicked(self) -> None:
        fileName = Path(
            QFileDialog.getOpenFileName(
                caption = self.tr('Load test data'),
                directory = str(MY_APP['DATA']),
                filter = self.tr('Data (*.pt)')
            )[0]
        )
        with open(fileName, 'rb') as f:
            self.measures = load(f)
        self.plotTimerTimeout()

    def closeButtonClicked(self) -> None:
        self.resetPlot()

    def exportData(self, file: Path) -> None:
        ...


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
    saveButton: QPushButton
    loadButton: QPushButton
    closeButton: QPushButton
    plotView: QGridLayout
    tr: ClassVar[Callable] = partial(QCoreApplication.translate, 'CyclicVoltammetryManager')
    dataFileExtension: ClassVar[str] = '.cv'

    def __post_init__(self) -> None:
        self.cfg: ConfigDict = MY_CFG.cycles.cyclicVoltammetry
        self.cmds: ConfigDict = MY_CFG.serial.commands
        self.pltCfg: ConfigDict = MY_CFG.plot
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
        self.saveButton.clicked.connect(lambda _: self.saveButtonClicked())
        self.loadButton.clicked.connect(lambda _: self.loadButtonClicked())
        self.closeButton.clicked.connect(lambda _: self.closeButtonClicked())
        self.plotTimer.timeout.connect(lambda: self.plotTimerTimeout())

    def enableSend(self, flag: bool = True) -> None:
        self.sendButton.setEnabled(flag)
        self.taskDelayButton.setEnabled(flag)
        self.cyclesButton.setEnabled(flag)
        self.slewRateButton.setEnabled(flag)
        self.startVoltageButton.setEnabled(flag)
        self.peakVoltageButton.setEnabled(flag)
        self.stopVoltageButton.setEnabled(flag)
        self.playButton.setEnabled(flag)
        self.saveButton.setEnabled(flag)

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

    def processCmd(self, rcvStr: str) -> str:
        options: dict = {
            self.cmds.start: self.processStart,
            self.cmds.stop: self.processStop,
            self.cmds.end: self.processEnd,
            self.cmds.cycle: self.processMeasure,
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
        self.resetPlot()
        self.plotTimer.start(self.pltCfg.updateInterval)
        self.loadButton.setEnabled(False)
        self.closeButton.setEnabled(False)
        return rcvStr

    def processStop(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.stop):]
        self.playButton.setChecked(False)
        self.plotTimer.stop()
        self.loadButton.setEnabled(True)
        self.closeButton.setEnabled(True)
        return rcvStr

    def processEnd(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.stop):]
        self.playButton.setChecked(False)
        self.plotTimer.stop()
        return rcvStr

    def processMeasure(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.cycle):]
        cc: str = rcvStr.split('$')[0][:-1]
        rcvStr = rcvStr[len(cc + self.cmds.timestamp) + 1:]
        ts: str = rcvStr.split('$')[0][:-1]
        rcvStr = rcvStr[len(ts + self.cmds.voltage) + 1:]
        voltage: str = rcvStr.split('$')[0][:-1]
        rcvStr = rcvStr[len(voltage + self.cmds.current) + 1:]
        current: str = rcvStr.split('$')[0][:-1]
        rcvStr = rcvStr[len(current):]
        if len(self.measures['timestamp']) == 0:
            self.startTimestamp = int(ts)            
        self.measures['cycle'].append(int(cc))
        self.measures['timestamp'].append((int(ts) - self.startTimestamp) / 1000.0)
        self.measures['voltage'].append(float(voltage))
        self.measures['current'].append(float(current))
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
        self.measures: dict[str, list[Optional[int | float | complex]]] = {
            'cycle': [],
            'timestamp': [],
            'voltage': [],
            'current': []
        }
        self.plot.clear()
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

    def saveButtonClicked(self) -> None:
        fileName = Path(
            QFileDialog.getSaveFileName(
                caption = self.tr('Save test data'),
                directory = str(MY_APP['DATA']),
                filter = self.tr('Data (*.cv)')
            )[0]
        )
        with open(fileName, 'wb') as f:
            dump(self.measures, f)

    def loadButtonClicked(self) -> None:
        fileName = Path(
            QFileDialog.getOpenFileName(
                caption = self.tr('Load test data'),
                directory = str(MY_APP['DATA']),
                filter = self.tr('Data (*.cv)')
            )[0]
        )
        with open(fileName, 'rb') as f:
            self.measures = load(f)
        self.plotTimerTimeout()

    def closeButtonClicked(self) -> None:
        self.resetPlot()


@dataclass
class SquareWaveVoltammetryManager:
    parent: MainWindow
    sendButton: QPushButton
    startVoltageValue: QDoubleSpinBox
    startVoltageButton: QPushButton
    stopVoltageValue: QDoubleSpinBox
    stopVoltageButton: QPushButton
    stepSizeValue: QSpinBox
    stepSizeButton: QPushButton
    pulseAmplitudeValue: QSpinBox
    pulseAmplitudeButton: QPushButton
    frequencyValue: QDoubleSpinBox
    frequencyButton: QPushButton
    maxCurrentValue: QSpinBox
    maxCurrentButton: QPushButton
    equilTimeValue: QDoubleSpinBox
    equilTimeButton: QPushButton
    playButton: QPushButton
    saveButton: QPushButton
    loadButton: QPushButton
    closeButton: QPushButton
    plotView: QGridLayout
    tr: ClassVar[Callable] = partial(QCoreApplication.translate, 'SquareWaveVoltammetryManager')
    dataFileExtension: ClassVar[str] = '.swv'

    def __post_init__(self) -> None:
        self.cfg: ConfigDict = MY_CFG.cycles.squareWaveVoltammetry
        self.cmds: ConfigDict = MY_CFG.serial.commands
        self.pltCfg: ConfigDict = MY_CFG.plot
        self._send: Callable = self.parent.sendCmd
        self.getStartVCmd: partial[str] = partial(self.getConfigCmd, True, False, False, False, False, False, False)
        self.getStopVCmd: partial[str] = partial(self.getConfigCmd, False, True, False, False, False, False, False)
        self.getSSCmd: partial[str] = partial(self.getConfigCmd, False, False, True, False, False, False, False)
        self.getPACmd: partial[str] = partial(self.getConfigCmd, False, False, False, True, False, False, False)
        self.getFQCmd: partial[str] = partial(self.getConfigCmd, False, False, False, False, True, False, False)
        self.getMCCmd: partial[str] = partial(self.getConfigCmd, False, False, False, False, False, True, False)
        self.getETCmd: partial[str] = partial(self.getConfigCmd, False, False, False, False, False, False, True)
        self.plotTimer: QTimer = QTimer()

    def init(self) -> None:
        self.setWidgets()
        self.enableSend(False)
        self.setCallbacks()

    def setWidgets(self) -> None:
        self.startVoltageValue.setValue(self.cfg.startVoltage)
        self.stopVoltageValue.setValue(self.cfg.stopVoltage)
        self.stepSizeValue.setValue(self.cfg.stepSize)
        self.pulseAmplitudeValue.setValue(self.cfg.pulseAmplitude)
        self.frequencyValue.setValue(self.cfg.frequency)
        self.maxCurrentValue.setValue(self.cfg.maxCurrent)
        self.equilTimeValue.setValue(self.cfg.equilTime)
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
        self.startVoltageButton.clicked.connect(lambda _: self._send(self.getStartVCmd()))
        self.stopVoltageButton.clicked.connect(lambda _: self._send(self.getStopVCmd()))
        self.stepSizeButton.clicked.connect(lambda _: self._send(self.getSSCmd()))
        self.pulseAmplitudeButton.clicked.connect(lambda _: self._send(self.getPACmd()))
        self.frequencyButton.clicked.connect(lambda _: self._send(self.getFQCmd()))
        self.maxCurrentButton.clicked.connect(lambda _: self._send(self.getMCCmd()))
        self.equilTimeButton.clicked.connect(lambda _: self._send(self.getETCmd()))
        self.playButton.clicked.connect(lambda checked: self.playButtonClicked(checked))
        self.saveButton.clicked.connect(lambda _: self.saveButtonClicked())
        self.loadButton.clicked.connect(lambda _: self.loadButtonClicked())
        self.closeButton.clicked.connect(lambda _: self.closeButtonClicked())
        self.plotTimer.timeout.connect(lambda: self.plotTimerTimeout())

    def enableSend(self, flag: bool = True) -> None:
        self.sendButton.setEnabled(flag)
        self.startVoltageButton.setEnabled(flag)
        self.stopVoltageButton.setEnabled(flag)
        self.stepSizeButton.setEnabled(flag)
        self.pulseAmplitudeButton.setEnabled(flag)
        self.frequencyButton.setEnabled(flag)
        self.maxCurrentButton.setEnabled(flag)
        self.equilTimeButton.setEnabled(flag)
        self.playButton.setEnabled(flag)
        self.saveButton.setEnabled(flag)

    def getConfigCmd(
        self,
        startVFlag: bool = True,
        stopVFlag: bool = True,
        ssFlag: bool = True,
        paFlag: bool = True,
        fqFlag: bool = True,
        mcFlag: bool = True,
        etFlag: bool = True
    ) -> str:
        header: str = f'{self.cmds.squareWaveVoltammetry}'
        startV: str = f'{self.cmds.startVoltage}{self.startVoltageValue.value()}' * startVFlag
        stopV: str = f'{self.cmds.stopVoltage}{self.stopVoltageValue.value()}' * stopVFlag
        ss: str = f'{self.cmds.taskDelay}{self.stepSizeValue.value()}' * ssFlag
        pa: str = f'{self.cmds.totalCycle}{self.pulseAmplitudeValue.value()}' * paFlag
        fq: str = f'{self.cmds.slewRate}{self.frequencyValue.value()}' * fqFlag
        mc: str = f'{self.cmds.peakVoltage}{self.maxCurrentValue.value()}' * mcFlag
        et: str = f'{self.cmds.peakVoltage}{self.equilTimeValue.value()}' * etFlag
        return f'{header}{startV}{stopV}{ss}{pa}{fq}{mc}{et}'

    def playButtonClicked(self, checked: bool) -> None:
        self.playButton.setChecked(not checked)
        if checked:
            self._send(f'{self.cmds.squareWaveVoltammetry}{self.cmds.start}')
        else:
            self._send(f'{self.cmds.squareWaveVoltammetry}{self.cmds.stop}')

    def processCmd(self, rcvStr: str) -> str:
        options: dict = {
            self.cmds.start: self.processStart,
            self.cmds.stop: self.processStop,
            self.cmds.end: self.processEnd,
            self.cmds.cycle: self.processMeasure,
            self.cmds.startVoltage: self.saveStartVoltage,
            self.cmds.stopVoltage: self.saveStopVoltage,
            self.cmds.stepSize: self.saveStepSize,
            self.cmds.pulseAmplitude: self.savePulseAmplitude,
            self.cmds.frequency: self.saveFrequency,
            self.cmds.maxCurrent: self.saveMaxCurrent,
            self.cmds.equilTime: self.saveEquilTime
        }
        while rcvStr.startswith(tuple(options.keys())):
            for key in options.keys():
                if rcvStr.startswith(key):
                    rcvStr = options[key](rcvStr)
        return rcvStr

    def processStart(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.start):]
        self.playButton.setChecked(True)
        self.resetPlot()
        self.plotTimer.start(self.pltCfg.updateInterval)
        self.loadButton.setEnabled(False)
        self.closeButton.setEnabled(False)
        return rcvStr

    def processStop(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.stop):]
        self.playButton.setChecked(False)
        self.plotTimer.stop()
        self.loadButton.setEnabled(True)
        self.closeButton.setEnabled(True)
        return rcvStr

    def processEnd(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.stop):]
        self.playButton.setChecked(False)
        self.plotTimer.stop()
        return rcvStr

    def processMeasure(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.timestamp):]
        ts: str = rcvStr.split('$')[0][:-1]
        rcvStr = rcvStr[len(ts + self.cmds.fordwardVoltage) + 1:]
        fv: str = rcvStr.split('$')[0][:-1]
        rcvStr = rcvStr[len(fv + self.cmds.fordwardCurrent) + 1:]
        fc: str = rcvStr.split('$')[0][:-1]
        rcvStr = rcvStr[len(fc + self.cmds.reverseVoltage) + 1:]
        rv: str = rcvStr.split('$')[0][:-1]
        rcvStr = rcvStr[len(rv + self.cmds.reverseCurrent) + 1:]
        rc: str = rcvStr.split('$')[0][:-1]
        rcvStr = rcvStr[len(rc + self.cmds.diffCurrent) + 1:]
        dc: str = rcvStr.split('$')[0][:-1]
        if len(self.measures['timestamp']) == 0:
            self.startTimestamp = int(ts)  
        self.measures['timestamp'].append((int(ts) - self.startTimestamp) / 1000.0)
        self.measures['fordward_voltage'].append(float(fv))
        self.measures['fordward_current'].append(float(fc))
        self.measures['reverse_voltage'].append(float(rv))
        self.measures['reverse_current'].append(float(rc))
        self.measures['step_voltage'].append((float(fv) + float(rv)) / 2)
        self.measures['diff_current'].append(float(dc))
        return rcvStr

    def saveStartVoltage(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.startVoltage):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.startVoltageValue.setValue(float(value))
        self.cfg.startVoltage = float(value)
        return rcvStr

    def saveStopVoltage(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.stopVoltage):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.stopVoltageValue.setValue(float(value))
        self.cfg.stopVoltage = float(value)
        return rcvStr

    def saveStepSize(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.stepSize):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.stepSizeValue.setValue(float(value))
        self.cfg.stepSize = float(value)
        return rcvStr

    def savePulseAmplitude(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.pulseAmplitude):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.pulseAmplitudeValue.setValue(float(value))
        self.cfg.pulseAmplitude = float(value)
        return rcvStr

    def saveFrequency(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.frequency):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.frequencyValue.setValue(float(value))
        self.cfg.frequency = float(value)
        return rcvStr

    def saveMaxCurrent(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.maxCurrent):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.maxCurrentValue.setValue(float(value))
        self.cfg.maxCurrent = float(value)
        return rcvStr

    def saveEquilTime(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.equilTime):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.equilTimeValue.setValue(float(value))
        self.cfg.equilTime = float(value)
        return rcvStr

    def resetPlot(self) -> None:
        self.measures: dict[str, list[Optional[int | float | complex]]] = {
            'timestamp': [],
            'fordward_voltage': [],
            'fordward_current': [],
            'reverse_voltage': [],
            'reverse_current': [],
            'step_voltage': [],
            'diff_current': []
        }
        self.plot.clear()
        self.line: PlotCurveItem = self.plot.plot(
            self.measures['step_voltage'],
            self.measures['diff_current'],
            name = self.tr('Voltage/Current'),
            color = self.pltCfg.colors[0],
            pen = f'#{self.pltCfg.colors[0]}',
            width = self.pltCfg.lineWidth
        )

    def plotTimerTimeout(self) -> None:
        self.line.setData(
            self.measures['step_voltage'],
            self.measures['diff_current']
        )

    def saveButtonClicked(self) -> None:
        fileName = Path(
            QFileDialog.getSaveFileName(
                caption = self.tr('Save test data'),
                directory = str(MY_APP['DATA']),
                filter = self.tr('Data (*.swv)')
            )[0]
        )
        with open(fileName, 'wb') as f:
            dump(self.measures, f)

    def loadButtonClicked(self) -> None:
        fileName = Path(
            QFileDialog.getOpenFileName(
                caption = self.tr('Load test data'),
                directory = str(MY_APP['DATA']),
                filter = self.tr('Data (*.swv)')
            )[0]
        )
        with open(fileName, 'rb') as f:
            self.measures = load(f)
        self.plotTimerTimeout()

    def closeButtonClicked(self) -> None:
        self.resetPlot()
