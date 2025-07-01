from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING, Callable, ClassVar

from PyQt5.QtCore import QCoreApplication, QIODevice
from PyQt5.QtGui import QTextCursor
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import (QAction, QComboBox, QLineEdit, QPlainTextEdit,
                             QPushButton)
from pyUtils import (ConfigDict, ConfigFileManager, ProjectPathsDict, errorLog,
                     infoLog, ppaths)

if TYPE_CHECKING:
    from ..windows import MainWindow


@dataclass
class SerialManager:
    parent: MainWindow
    actionUpdateDevices: QAction
    actionConnectDevice: QAction
    selector: QComboBox
    statusBar: QLineEdit
    customCmdValue: QLineEdit
    customCmdButton: QPushButton
    rcvCmds: QPlainTextEdit
    tr: ClassVar[Callable] = partial(QCoreApplication.translate, 'SerialManager')

    def __post_init__(self) -> None:
        cfg = ConfigFileManager(ppaths[ProjectPathsDict.CONFIG_FILE_PATH])
        self.cfg: ConfigDict = cfg.serial
        self.cmds: ConfigDict = cfg.serial.commands

    def init(self) -> None:
        self.setConfig()
        self.setWidgets()
        self.enableSend(False)
        self.setCallbacks()

    def setConfig(self) -> None:
        self.serialPort: QSerialPort = QSerialPort()
        self.serialPort.setBaudRate(self.cfg.baudRate)
        self.serialPort.setDataBits(self.cfg.dataBits)
        self.serialPort.setParity(self.cfg.parity)
        self.serialPort.setStopBits(self.cfg.stopBits)

    def setWidgets(self) -> None:
        self.statusBar.setText(self.tr('Disconnected'))

    def setCallbacks(self) -> None:
        self.actionUpdateDevices.triggered.connect(lambda: self.actionUpdateDevicesTriggered())
        self.actionConnectDevice.toggled.connect(lambda: self.actionConnectDeviceToggled())
        self.serialPort.readyRead.connect(lambda: self.serialPortReadyRead())
        self.serialPort.errorOccurred.connect(lambda error: self.serialPortErrorOccurred(error))
        self.selector.currentIndexChanged.connect(lambda: self.selectorCurrentIndexChanged())
        self.customCmdButton.clicked.connect(lambda _: self.sendCustomCmd())

    def actionUpdateDevicesTriggered(self) -> None:
        self.parent.debug(self.tr('Updating serial devices...'))
        self.selector.clear()
        for port in QSerialPortInfo.availablePorts():
            self.selector.addItem(f'{port.portName()}: {port.description()}')
        self.selector.setCurrentIndex(-1)
        self.parent.debug(self.tr('Serial devices updated'), infoLog)

    def actionConnectDeviceToggled(self) -> None:
        if self.actionConnectDevice.isChecked():
            self.parent.debug(self.tr(f'Connecting to {self.serialPort.portName()}...'))
            self.serialPort.open(QIODevice.ReadWrite)
            self.parent.enableSend(True)
            self.statusBar.setText(self.tr('Connected'))
            self.parent.debug(self.tr(f'Configuring {self.serialPort.portName()}...'), infoLog)
            self.parent.sendInitCmds()
            self.parent.debug(self.tr(f'{self.serialPort.portName()} initialized'), infoLog)
        else:
            self.serialPort.close()
            self.parent.enableSend(False)
            self.statusBar.setText(self.tr('Disconnected'))
            self.parent.debug(self.tr(f'{self.serialPort.portName()} disconnected'), infoLog)

    def selectorCurrentIndexChanged(self) -> None:
        self.actionConnectDevice.setChecked(False)
        if self.selector.currentText() != '':
            self.actionConnectDevice.setEnabled(True)
            self.serialPort.setPortName(self.selector.currentText().split(':')[0])
            self.statusBar.setText(self.tr('Disconnected'))
        else:
            self.actionConnectDevice.setEnabled(False)
            self.statusBar.setText('')

    def serialPortReadyRead(self) -> None:
        while self.serialPort.canReadLine():
            rcvStr: str = f'{self.serialPort.readLine()}'.replace("b'", "").replace("'", "").strip(self.cfg.endCharacter)
            self.parent.debug(self.tr(f'Received from {self.serialPort.portName()}: {rcvStr}'))
            self.addLineToRcvCmds(rcvStr)
            self.parent.strReceived.emit(rcvStr)

    def serialPortErrorOccurred(self, error: QSerialPort.SerialPortError) -> None:
        if error != QSerialPort.SerialPortError.NoError:
            self.parent.debug(self.tr(f'Error on serial port: {error}->{self.serialPort.errorString()}'), errorLog)
            self.actionUpdateDevices.trigger()

    def sendCmd(self, cmd: str) -> None:
        if not isinstance(cmd, str):
            cmd = str(cmd)
        if self.serialPort.write(cmd.encode()) > 0:
            self.parent.debug(self.tr(f'Sended: {cmd}'))

    def sendCustomCmd(self) -> None:
        self.sendCmd(self.customCmdValue.text())
        self.customCmdValue.setText('')

    def addLineToRcvCmds(self, newLine: str) -> None:
        lines: list = self.rcvCmds.toPlainText().split('\n')
        if len(lines) > 20:
            self.rcvCmds.setPlainText('\n'.join(lines[-20:]))
        self.rcvCmds.appendPlainText(newLine)
        cursor: QTextCursor = self.rcvCmds.textCursor()
        cursor.movePosition(cursor.End)
        self.rcvCmds.setTextCursor(cursor)
        self.rcvCmds.ensureCursorVisible()

    def enableSend(self, flag: bool = True) -> None:
        self.selector.setEnabled(not flag)
        self.actionUpdateDevices.setEnabled(not flag)
        self.customCmdButton.setEnabled(flag)
