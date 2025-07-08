from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING, Callable, ClassVar

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QComboBox, QSpinBox, QDoubleSpinBox
from pyUtils import ConfigDict, ConfigFileManager, ProjectPathsDict, ppaths

if TYPE_CHECKING:
    from ..windows import MainWindow


@dataclass
class CalculatorManager:
    parent: MainWindow
    vRangeMinValue: QDoubleSpinBox
    vRangeMaxValue: QDoubleSpinBox
    r2Value: QSpinBox
    r3Value: QSpinBox
    r4Value: QSpinBox
    cRangeMinValue: QDoubleSpinBox
    cRangeMaxValue: QDoubleSpinBox
    r5Value: QSpinBox
    r6Value: QSpinBox
    boardSelector: QComboBox
    tr: ClassVar[Callable] = partial(QCoreApplication.translate, 'CalculatorManager')

    def __post_init__(self) -> None:
        cfg = ConfigFileManager(ppaths[ProjectPathsDict.CONFIG_FILE_PATH])
        self.cfg: ConfigDict = cfg.circuit
        self.boards: ConfigDict = cfg.boards
        self._send: Callable = self.parent.sendCmd

    def init(self) -> None:
        self.setWidgets()
        self.setCallbacks()

    def setWidgets(self) -> None:
        self.r2Value.setValue(self.cfg.r2)
        self.r3Value.setValue(self.cfg.r3)
        self.r4Value.setValue(self.cfg.r4)
        self.r5Value.setValue(self.cfg.r5)
        self.r6Value.setValue(self.cfg.r6)
        self.vRangeMinValue.setValue(self.parent.vRangeMinValue.value())
        self.vRangeMaxValue.setValue(self.parent.vRangeMaxValue.value())
        self.cRangeMinValue.setValue(self.parent.cRangeMinValue.value())
        self.cRangeMaxValue.setValue(self.parent.cRangeMaxValue.value())
        for board in self.boards.keys():
            self.boardSelector.addItem(board)
        self.boardSelector.setCurrentIndex(0)

    def setCallbacks(self) -> None:
        self.boardSelector.currentIndexChanged.connect(lambda _: self.updateResistorsValues())
        self.parent.opampVccPValue.valueChanged.connect(lambda _: self.updateResistorsValues())
        self.parent.opampVccNValue.valueChanged.connect(lambda _: self.updateResistorsValues())
        self.parent.opampHRValue.valueChanged.connect(lambda _: self.updateResistorsValues())
        self.parent.opampBRValue.valueChanged.connect(lambda _: self.updateResistorsValues())
        self.vRangeMaxValue.valueChanged.connect(lambda _: self.updateVoltageResistorsValues())
        self.r3Value.valueChanged.connect(lambda _: self.updateVoltageResistorsValues())
        self.parent.vb1Value.valueChanged.connect(lambda _: self.updateVoltageResistorsValues())
        self.cRangeMaxValue.valueChanged.connect(lambda _: self.updateCurrentResistorsValues())
        self.parent.vb2Value.valueChanged.connect(lambda _: self.updateCurrentResistorsValues())

    def updateResistorsValues(self) -> None:
        self.updateVoltageResistorsValues()
        self.updateCurrentResistorsValues()

    def updateVoltageResistorsValues(self) -> None:
        board: ConfigDict = self.boards[self.boardSelector.currentText()]
        vcc: float = board['vcc']
        vb1: float = self.parent.vb1Value.value()
        r3: int = self.r3Value.value()
        r2: float = - r3 * vcc / (2 * vb1)
        self.r2Value.setValue(int(r2))
        r4: float = - r3 * (self.vRangeMaxValue.value() / vb1)
        self.r4Value.setValue(int(r4))
        self.vRangeMinValue.setValue(- self.vRangeMaxValue.value())

    def updateCurrentResistorsValues(self) -> None:
        board: ConfigDict = self.boards[self.boardSelector.currentText()]
        vcc: float = board['vcc']
        vb2: float = self.parent.vb2Value.value()
        r5: float = - vb2 / (self.cRangeMaxValue.value() / 1000000)
        self.r5Value.setValue(int(r5))
        r6: float = - r5 * (vcc / (2 * vb2))
        self.r6Value.setValue(int(r6))
        self.cRangeMinValue.setValue(- self.cRangeMaxValue.value())
