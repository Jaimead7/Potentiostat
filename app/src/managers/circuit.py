from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING, Callable, ClassVar

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QComboBox, QDoubleSpinBox, QPushButton, QSpinBox
from pyUtils import ConfigDict
from utils import MY_CFG

if TYPE_CHECKING:
    from ..windows import MainWindow


@dataclass
class CircuitManager:
    parent: MainWindow
    sendButton: QPushButton
    r1Value: QSpinBox
    r1Button: QPushButton
    r2Value: QSpinBox
    r2Button: QPushButton
    r3Value: QSpinBox
    r3Button: QPushButton
    r4Value: QSpinBox
    r4Button: QPushButton
    r5Value: QSpinBox
    r5Button: QPushButton
    r6Value: QSpinBox
    r6Button: QPushButton
    vb1Value: QDoubleSpinBox
    vb1Button: QPushButton
    vb2Value: QDoubleSpinBox
    vb2Button: QPushButton
    opampVccPValue: QDoubleSpinBox
    opampVccPButton: QPushButton
    opampVccNValue: QDoubleSpinBox
    opampVccNButton: QPushButton
    opampHRValue: QDoubleSpinBox
    opampHRButton: QPushButton
    opampBRValue: QDoubleSpinBox
    opampBRButton: QPushButton
    vRangeMinValue: QDoubleSpinBox
    vRangeMaxValue: QDoubleSpinBox
    cRangeMinValue: QDoubleSpinBox
    cRangeMaxValue: QDoubleSpinBox
    boardSelector: QComboBox
    tr: ClassVar[Callable] = partial(QCoreApplication.translate, 'CircuitManager')

    def __post_init__(self) -> None:
        self.cfg: ConfigDict = MY_CFG.circuit
        self.cmds: ConfigDict = MY_CFG.serial.commands
        self.boards: ConfigDict = MY_CFG.boards
        self.getR1Cmd: Callable = partial(self.getConfigCmd, True, False, False, False, False, False, False, False, False, False, False, False)
        self.getR2Cmd: Callable = partial(self.getConfigCmd, True, True, False, False, False, False, False, False, False, False, False, False)
        self.getR3Cmd: Callable = partial(self.getConfigCmd, False, False, True, False, False, False, False, False, False, False, False, False)
        self.getR4Cmd: Callable = partial(self.getConfigCmd, False, False, False, True, False, False, False, False, False, False, False, False)
        self.getR5Cmd: Callable = partial(self.getConfigCmd, False, False, False, False, True, False, False, False, False, False, False, False)
        self.getR6Cmd: Callable = partial(self.getConfigCmd, False, False, False, False, False, True, False, False, False, False, False, False)
        self.getVB1Cmd: Callable = partial(self.getConfigCmd, False, False, False, False, False, False, True, False, False, False, False, False)
        self.getVB2Cmd: Callable = partial(self.getConfigCmd, False, False, False, False, False, False, False, True, False, False, False, False)
        self.getOpampVccPCmd: Callable = partial(self.getConfigCmd, False, False, False, False, False, False, False, False, True, False, False, False)
        self.getOpampVccNCmd: Callable = partial(self.getConfigCmd, False, False, False, False, False, False, False, False, False, True, False, False)
        self.getOpampHRCmd: Callable = partial(self.getConfigCmd, False, False, False, False, False, False, False, False, False, False, True, False)
        self.getOpampBRCmd: Callable = partial(self.getConfigCmd, False, False, False, False, False, False, False, False, False, False, False, True)
        self._send: Callable = self.parent.sendCmd

    def init(self) -> None:
        self.setWidgets()
        self.enableSend(False)
        self.setCallbacks()
        self.updateRanges()

    def setWidgets(self) -> None:
        self.r1Value.setValue(self.cfg.r1)
        self.r2Value.setValue(self.cfg.r2)
        self.r3Value.setValue(self.cfg.r3)
        self.r4Value.setValue(self.cfg.r4)
        self.r5Value.setValue(self.cfg.r5)
        self.r6Value.setValue(self.cfg.r6)
        self.vb1Value.setValue(self.cfg.vb1)
        self.vb2Value.setValue(self.cfg.vb2)
        self.opampVccPValue.setValue(self.cfg.opampVccP)
        self.opampVccNValue.setValue(self.cfg.opampVccN)
        self.opampHRValue.setValue(self.cfg.opampHR)
        self.opampBRValue.setValue(self.cfg.opampBR)
        for board in self.boards.keys():
            self.boardSelector.addItem(board)
        self.boardSelector.setCurrentIndex(0)

    def setCallbacks(self) -> None:
        self.sendButton.clicked.connect(lambda _: self._send(self.getConfigCmd()))
        self.r1Button.clicked.connect(lambda _: self._send(self.getR1Cmd()))
        self.r2Button.clicked.connect(lambda _: self._send(self.getR2Cmd()))
        self.r3Button.clicked.connect(lambda _: self._send(self.getR3Cmd()))
        self.r4Button.clicked.connect(lambda _: self._send(self.getR4Cmd()))
        self.r5Button.clicked.connect(lambda _: self._send(self.getR5Cmd()))
        self.r6Button.clicked.connect(lambda _: self._send(self.getR6Cmd()))
        self.vb1Button.clicked.connect(lambda _: self.getVB1Cmd())
        self.vb2Button.clicked.connect(lambda _: self.getVB2Cmd())
        self.opampVccPButton.clicked.connect(lambda _: self.getOpampVccPCmd())
        self.opampVccNButton.clicked.connect(lambda _: self.getOpampVccNCmd())
        self.opampHRButton.clicked.connect(lambda _: self.getOpampHRCmd())
        self.opampBRButton.clicked.connect(lambda _: self.getOpampBRCmd())
        self.boardSelector.currentIndexChanged.connect(lambda _: self.updateRanges())
        self.opampVccPValue.valueChanged.connect(lambda _: self.updateRanges())
        self.opampVccNValue.valueChanged.connect(lambda _: self.updateRanges())
        self.opampHRValue.valueChanged.connect(lambda _: self.updateRanges())
        self.opampBRValue.valueChanged.connect(lambda _: self.updateRanges())
        self.r2Value.valueChanged.connect(lambda _: self.updateVoltageRange())
        self.r3Value.valueChanged.connect(lambda _: self.updateVoltageRange())
        self.r4Value.valueChanged.connect(lambda _: self.updateVoltageRange())
        self.vb1Value.valueChanged.connect(lambda _: self.updateVoltageRange())
        self.r5Value.valueChanged.connect(lambda _: self.updateCurrentRange())
        self.r6Value.valueChanged.connect(lambda _: self.updateCurrentRange())
        self.vb2Value.valueChanged.connect(lambda _: self.updateCurrentRange())

    def enableSend(self, flag: bool) -> None:
        self.sendButton.setEnabled(flag)
        self.r1Button.setEnabled(flag)
        self.r2Button.setEnabled(flag)
        self.r3Button.setEnabled(flag)
        self.r4Button.setEnabled(flag)
        self.r5Button.setEnabled(flag)
        self.r6Button.setEnabled(flag)
        self.vb1Button.setEnabled(flag)
        self.vb2Button.setEnabled(flag)
        self.opampVccPButton.setEnabled(flag)
        self.opampVccNButton.setEnabled(flag)
        self.opampHRButton.setEnabled(flag)
        self.opampBRButton.setEnabled(flag)

    def getConfigCmd(
        self,
        r1Flag: bool = True,
        r2Flag: bool = True,
        r3Flag: bool = True,
        r4Flag: bool = True,
        r5Flag: bool = True,
        r6Flag: bool = True,
        vb1Flag: bool = True,
        vb2Flag: bool = True,
        opampVccPFlag: bool = True,
        opampVccNFlag: bool = True,
        opampHRFlag: bool = True,
        opampBRFlag: bool = True,
    ) -> str:
        header: str = f'{self.cmds.circuit}'
        r1: str = f'{self.cmds.r1}{self.r1Value.value()}' * r1Flag
        r2: str = f'{self.cmds.r2}{self.r2Value.value()}' * r2Flag
        r3: str = f'{self.cmds.r3}{self.r3Value.value()}' * r3Flag
        r4: str = f'{self.cmds.r4}{self.r4Value.value()}' * r4Flag
        r5: str = f'{self.cmds.r5}{self.r5Value.value()}' * r5Flag
        r6: str = f'{self.cmds.r6}{self.r6Value.value()}' * r6Flag
        vb1: str = f'{self.cmds.vb1}{self.vb1Value.value()}' * vb1Flag
        vb2: str = f'{self.cmds.vb2}{self.vb2Value.value()}' * vb2Flag
        opampVccP: str = f'{self.cmds.opampVccP}{self.opampVccPValue.value()}' * opampVccPFlag
        opampVccN: str = f'{self.cmds.opampVccN}{self.opampVccNValue.value()}' * opampVccNFlag
        opampHR: str = f'{self.cmds.opampHR}{self.opampHRValue.value()}' * opampHRFlag
        opampBR: str = f'{self.cmds.opampBR}{self.opampBRValue.value()}' * opampBRFlag
        return f'{header}{r1}{r2}{r3}{r4}{r5}{r6}{vb1}{vb2}{opampVccP}{opampVccN}{opampHR}{opampBR}'

    def saveR1(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.r1):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.r1Value.setValue(int(value))
        self.cfg.r1 = int(value)
        self.parent.debug(self.tr(f"R1 set to {self.cfg.r1} ohm"))
        return rcvStr
        
    def saveR2(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.r2):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.r2Value.setValue(int(value))
        self.cfg.r2 = int(value)
        self.parent.debug(self.tr(f"R2 set to {self.cfg.r2} ohm"))
        return rcvStr

    def saveR3(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.r3):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.r3Value.setValue(int(value))
        self.cfg.r3 = int(value)
        self.parent.debug(self.tr(f"R3 set to {self.cfg.r3} ohm"))
        return rcvStr

    def saveR4(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.r4):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.r4Value.setValue(int(value))
        self.cfg.r4 = int(value)
        self.parent.debug(self.tr(f"R4 set to {self.cfg.r4} ohm"))
        return rcvStr

    def saveR5(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.r5):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.r5Value.setValue(int(value))
        self.cfg.r5 = int(value)
        self.parent.debug(self.tr(f"R5 set to {self.cfg.r5} ohm"))
        return rcvStr

    def saveR6(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.r6):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.r6Value.setValue(int(value))
        self.cfg.r6 = int(value)
        self.parent.debug(self.tr(f"R6 set to {self.cfg.r6} ohm"))
        return rcvStr

    def saveVB1(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.vb1):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.vb1Value.setValue(float(value))
        self.cfg.vb1 = float(value)
        self.parent.debug(self.tr(f"Vb1 set to {self.cfg.vb1} V"))
        return rcvStr

    def saveVB2(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.vb2):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.vb2Value.setValue(float(value))
        self.cfg.vb2 = float(value)
        self.parent.debug(self.tr(f"Vb2 set to {self.cfg.vb2} V"))
        return rcvStr

    def saveOpampVccP(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.opampVccP):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.opampVccPValue.setValue(float(value))
        self.cfg.opampVccP = float(value)
        self.parent.debug(self.tr(f"OpampVcc+ set to {self.cfg.opampVccP} V"))
        return rcvStr

    def saveOpampVccN(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.opampVccN):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.opampVccNValue.setValue(float(value))
        self.cfg.opampVccN = float(value)
        self.parent.debug(self.tr(f"OpampVcc- set to {self.cfg.opampVccN} V"))
        return rcvStr

    def saveOpampHR(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.opampHR):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.opampHRValue.setValue(float(value))
        self.cfg.opampHR = float(value)
        self.parent.debug(self.tr(f"OpampHeadRoom set to {self.cfg.opampHR} V"))
        return rcvStr

    def saveOpampBR(self, rcvStr: str) -> str:
        rcvStr = rcvStr[len(self.cmds.opampBR):]
        value: str = rcvStr.split('$')[0]
        rcvStr = rcvStr[len(value):]
        self.opampBRValue.setValue(float(value))
        self.cfg.opampBR = float(value)
        self.parent.debug(self.tr(f"OpampBottomRoom set to {self.cfg.opampBR} V"))
        return rcvStr
        
    def opampLimits(self, voltage: float) -> float:
        opampVccP: int | float = self.opampVccPValue.value()
        opampVccN: int | float = self.opampVccNValue.value()
        opampHR: int | float = self.opampHRValue.value()
        opampBR: int | float = self.opampBRValue.value()
        return float(min(max(voltage, opampVccN + opampBR), opampVccP - opampHR))

    def boardVToCEV(self, voltage: float) -> float:
        vi: float = self.opampLimits(voltage)
        r2: int | float = self.r2Value.value()
        r3: int | float = self.r3Value.value()
        r4: int | float = self.r4Value.value()
        vb1: int | float = self.vb1Value.value()
        vo: float = float(- r4 * ((vi / r2 ) + (vb1 / r3)))
        return self.opampLimits(vo)

    def boardVToWECurrent(self, voltage: float) -> float:
        r5: int | float = self.r5Value.value()
        r6: int | float = self.r6Value.value()
        vb2: int | float = self.vb2Value.value()
        v: float = self.opampLimits(voltage)
        return float(- ((vb2 / r5) + (v / r6)) * 1000000)

    def updateRanges(self) -> None:
        self.updateVoltageRange()
        self.updateCurrentRange()

    def updateVoltageRange(self) -> None:
        board: dict = self.boards[self.boardSelector.currentText()]
        self.vRangeMinValue.setValue(self.boardVToCEV(board['vcc']))
        self.vRangeMaxValue.setValue(self.boardVToCEV(0))

    def updateCurrentRange(self) -> None:
        board: dict = self.boards[self.boardSelector.currentText()]
        self.cRangeMinValue.setValue(self.boardVToWECurrent(board['vcc']))
        self.cRangeMaxValue.setValue(self.boardVToWECurrent(0))
