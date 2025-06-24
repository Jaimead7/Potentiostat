<#
 # @file serialToCSV.ps1
 #
 # @section intro Introduction
 # 
 # This powershell script read serial data from a serial port and write it to a .csv.
 #
 # @section author Author
 #
 # Written by Jaime Alvarez for Grupo Copo
 #
 # @section license License
 #
 # Copyright 2025 Grupo Copo
 # Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation
 # files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy,
 # modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
 # is furnished to do so, subject to the following conditions:
 #
 # The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
 # WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 # HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 #
 #>

<######################################################################>

<# Set debug mode #>
$DEBUG = $true
if ($DEBUG) {
    $DEBUGMODE = "Continue"
} else {
    $DEBUGMODE = "SilentlyContinue"
}

<# Properties class for System.IO.Ports.SerialPort object #>
class PortProperties {
    [string] $portName
    [int] $baudRate
    [System.IO.Ports.Parity] $parity
    [int] $dataBits
    [System.IO.Ports.StopBits] $stopBits
    [System.IO.Ports.Handshake] $handshake
    [string] $newLine
    [string] $outFile
}

<# Class for commands buffer #>
class SerialCommand {
    [string] $value
    [datetime] $date
}

<# Serial port class to manage serial ports comunications #>
class SerialPort {
    <# Variables #>
    [System.IO.Ports.SerialPort] $port = [System.IO.Ports.SerialPort]::new()
    [SerialCommand[]]$readBuffer = @()
    [String] $outFile

    <# Init class #>
    SerialPort([PortProperties] $props) {
        try {
            $this.port.PortName = [string] $props.portName
            $this.port.BaudRate = [int] $props.baudRate
            $this.port.Parity = [System.IO.Ports.Parity] $props.parity
            $this.port.DataBits = [int] $props.dataBits
            $this.port.StopBits = [System.IO.Ports.StopBits] $props.stopBits
            $this.port.Handshake = [System.IO.Ports.Handshake] $props.handshake
            $this.port.NewLine = [string] $props.newLine
            $this.port.DtrEnable = $true
            $this.port.RtsEnable = $true
            $this.outFile = $props.outFile
        } catch {
            Write-Debug "Error initializing port"
        }
    }

    <# Open the port #>
    openPort() {
        try {
            Write-Debug "Opening port"
            $this.port.Open()
            Start-Sleep -Milliseconds 1000
            $this.clearData()
            Write-Debug "Port is open"
        } catch {
            Write-Debug "Could not open port SerialPort::openPort()"
            Write-Error $_.ScriptStackTrace
        }
    }

    <# Check port Open/Close #>
    [bool] isOpen() {
        if ($this.port.IsOpen) {
            return $true
        } else {
            return $false
        }
    }

    <# Send data #>
    sendData([string] $data) {
        if ($this.isOpen()) {
            if ($null -eq $data) {
                return
            }
            $data = $data + "`r"
            $this.port.Write($data)
            Write-Debug "Sended: $data"
            Start-Sleep -Milliseconds 20
        }
    }

    <#
     # Event to handle data reception
     # Messages are not display on current sesion
     #>
    initEventSub() {
        $act = {
            if ($Event.MessageData.serial) {
                if ($Sender.BytesToRead) {
                    $Event.MessageData.serial.processData($Sender.ReadLine())
                }
            } else {
                Write-Debug "No object exists to handle the data."
                Write-Debug "You must create an object in global scope so the method can be accessed"
            }
        }
        <# Create event launched on data reception #>
        Register-ObjectEvent -InputObject $this.port -EventName "DataReceived" -Action $act -MessageData @{serial = $this}
        Write-Debug """DataReceived"" event created"
    }

    <# Process the received data #>
    processData([string] $data) {
        [SerialCommand] $command = [SerialCommand]::new()
        $command.value = $data
        $command.date = Get-Date
        $this.readBuffer += $command
        "$($command.date),$($command.value)" | Out-File -FilePath $this.outFile -Append -Force
        Write-Debug "Received Data (Added to readBuffer): $($data)"
    }

    <# Read data form buffer #>
    [SerialCommand] readData() {
        $data = $this.readBuffer[0]
        if ($this.readBuffer.Length -gt 1) {
            $this.readBuffer = $this.readBuffer[1..($this.readBuffer.Length-1)]
        } else {
            $this.readBuffer = @()
        }
        return $data
    }

    <# Clear data buffer #>
    clearData() {
        $this.port.DiscardInBuffer()
        $this.port.DiscardOutBuffer()
        $this.readBuffer = @()
        Write-Debug "Data buffer cleared"
    }

    <# Data available #>
    [int] dataAvailable() {
        return $this.readBuffer.Length
    }

    <# Releases resources #>
    Dispose() {
        Write-Debug "Closing port"
        $this.port.Close()
        Start-Sleep -Milliseconds 1000
        $this.port.Dispose()  # Releases all resources from port
        <# Close all events in this sesion #>
        Get-EventSubscriber | ForEach-Object {
            Unregister-Event -SubscriptionId $_.SubscriptionId
        }
        Write-Debug "Port is closed"
    }
}


<# Class for manage the program #>
class MyProgram {
    <# Variables #>
    <# Serial port #>
    [PortProperties] $comProps = [PortProperties]::new()
    [string] $portSelected
    [SerialPort] $serialPort
    [datetime] $lastSerialSend = [datetime](Get-Date)
    [bool] $serialDataSended = $false
    [double] $READDELAY = 1000  # ms
    <# Program #>
    [bool] $endProgram = $false
    [string] $dataPath = (Join-Path -Path (Get-Item $PSScriptRoot).parent.FullName -ChildPath "data")
    [string] $commandToSend

    <# Init class #>
    MyProgram() {
        <# Set port properties #>
        $this.comProps.baudRate = 115200
        $this.comProps.dataBits = 8
        $this.comProps.handshake = [System.IO.Ports.Handshake]::None
        $this.comProps.newLine = "`r"
        $this.comProps.parity = [System.IO.Ports.Parity]::None
        $this.comProps.stopBits = [System.IO.Ports.StopBits]::One
    }

    <# Program init #>
    init() {
        <# Selecting port #>
        Write-Host "`nPorts Availables:"
        [System.IO.Ports.SerialPort]::getportnames() | ForEach-Object { Write-Host " - $_"}
        $this.portSelected = Read-Host "Select port"
        Write-Host "`n"
        if (![System.IO.Ports.SerialPort]::getportnames().Contains($this.portSelected)) {
            Write-Error "Invalid port" -Category "InvalidData"
            exit(1)
        }
        $this.comProps.portName = $this.portSelected
        $this.comProps.outFile = (Join-Path -Path $this.dataPath -ChildPath "data.csv")

        <# Set comunication port #>
        $this.serialPort = [SerialPort]::new($this.comProps)
        $this.serialPort.openPort()
        $this.serialPort.initEventSub()

        <# Send command #>
        $this.commandToSend = Read-Host "Command to send"
        $this.serialPort.sendData($this.commandToSend)
    }

    <# Program loop #>
    loop() {
        do {
            <# Manage serial port read #>
            if ($this.serialPort.dataAvailable() -gt 0) {
                [SerialCommand] $data = $this.serialPort.readData()
                Write-Host "[$($data.date)] Received: $($data.value)"
                <#
                switch ($data.Substring(0, 2)) {
                    "OK" {
                        Write-Debug "Received OK from power source"
                        switch ($this.serverTCPIP.lastCommand.Substring(0, 4)) {
                            "VOLT" {
                                Write-Host "[$(Get-Date)] Voltage changed to: $($this.serverTCPIP.lastCommand)"
                            }
                            "SOUT" {
                                Write-Host "[$(Get-Date)] Power source state changed to: $($this.serverTCPIP.lastCommand)"
                            }
                        }
                        $this.serialDataSended = $false
                    }
                }
                #>
            }
        
            <# Exit on Esc press #>
            if ([System.Console]::KeyAvailable) {
                $key = [System.Console]::ReadKey('NoEcho').Key
                if ($key -eq '27') {
                    $this.endProgram = $true
                    Write-Host "`nStopping program`n"
                }
            }
        } until ($this.endProgram)

        <# Releases port resources #>
        $this.serialPort.Dispose()
    }

    <# Run the program #>
    run() {
        $this.init()
        $this.loop()
    }
}

<######################################################################>

$DebugPreference = $DEBUGMODE

[MyProgram] $myProgram = [MyProgram]::new()
$myProgram.run()

$DebugPreference = "SilentlyContinue"