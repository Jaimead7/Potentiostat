from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from numbers import Number
from typing import TYPE_CHECKING, Callable, ClassVar, Optional

from PyQt5.QtCore import QCoreApplication, QDateTime, QTimer
from PyQt5.QtWidgets import QGridLayout
from pyqtgraph import (DateAxisItem, LabelItem, LegendItem, PlotCurveItem,
                       PlotWidget)
from pyUtils import ConfigDict, ConfigFileManager, ProjectPathsDict, ppaths

if TYPE_CHECKING:
    from ..windows import MainWindow


@dataclass
class PlotManager:
    parent: MainWindow
    view: QGridLayout
    tr: ClassVar[Callable] = partial(QCoreApplication.translate, 'PlotManager')

    def __post_init__(self) -> None:
        self.gbCfg = ConfigFileManager(ppaths[ProjectPathsDict.CONFIG_FILE_PATH])
        self.cfg: ConfigDict = self.gbCfg.plot
        self.timer: QTimer = QTimer()

    def init(self) -> None:
        self.setWidgets()
        self.setCallbacks()
        self.timer.start(self.cfg.updateInterval)

    def setWidgets(self) -> None:
        self.plot: PlotWidget = PlotWidget(
            axisItems= {
                'bottom': DateAxisItem(utcOffset= 0)
            }
        )
        self.plot.showGrid(x= True, y= True)
        self.plot.showAxis('left')
        self.plot.showAxis('right')
        self.plot.setLabels(bottom= 'Time')
        self.legend: LegendItem = self.plot.addLegend()
        self.view.addWidget(self.plot, 0, 0)
        self.reset()

    def setCallbacks(self) -> None:
        self.timer.timeout.connect(lambda: self.timerTimeout())

    def timerTimeout(self) -> None:
        for sensor, line in self.lines.items():
            line.setData(self.plotXData, self.plotYData[sensor])

    def reset(self) -> None:
        date: QDateTime = QDateTime.currentDateTimeUtc()
        self.plotXData: list[Optional[Number]] = [date.toMSecsSinceEpoch()/1000]
        self.plotYData: dict[list[Optional[Number]]] = {
            i: [0] for i in range(len(self.cfg.lines.values()))
        }
        self.lines: list[PlotCurveItem] = {
            i: self.plot.plot(self.plotXData,
                              yData,
                              name= list(self.cfg.lines.values())[i],
                              color= self.cfg.colors[i],
                              pen= f'#{self.cfg.colors[i]}',
                              width= self.cfg.lineWidth)
            for i, yData in self.plotYData.items()
        }

    def addPoint(self, sensor: int, value: Number) -> None:
        date: QDateTime = QDateTime.currentDateTimeUtc()
        self.plotXData.append(date.toMSecsSinceEpoch()/1000)
        for yData in self.plotYData.values():
            yData.append(yData[-1])
        self.plotYData[sensor][-1] = value
        if len(self.plotXData) > self.cfg.maxPoints * self.gbCfg.sensors.nSensors:
            self.plotXData.pop(0)
            [yData.pop(0) for yData in self.plotYData.values()]

    def setLabels(self, names: list[str]) -> None:
        for sensor, line in self.lines.items():
            label: LabelItem = self.legend.getLabel(line)
            label.setText(names[sensor])
            
