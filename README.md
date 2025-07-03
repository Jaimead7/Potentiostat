# Simple potentiostat for electrochemical sensors


## Contact:  
> **Jaime Ávarez Díaz**  
> *R&D Porject manager*  
> Centro Tecnológico Grupo Copo S.L.U.  
> *e-mail:* jadiaz@grupocopo.com  
> *Mov:* +34 683 462 905  
>  
> <a href="https://www.grupocopo.com/"><img title="Grupo Copo" src="https://www.grupocopo.com/wp-content/uploads/2021/07/logonuevo.png" height="40"></a>  

> **Nuna Gabriela Lima da Costa**  
> *PhD student*  
> Universidade do Minho  
> *e-mail:* id10704@alumnos.uminho.pt  
>  
> <a href="https://www.grupocopo.com/"><img title="2c2t Logo" src="https://2c2t.uminho.pt/wp-content/uploads/2024/02/logo-white-icon.png" height="40"> <img title="2c2t" src="https://2c2t.uminho.pt/wp-content/uploads/2024/02/logo-white.png" height="40"> <img title="uminho" src="https://2c2t.uminho.pt/wp-content/uploads/2024/01/Un-minho.svg" height="40"></a>  


## Description:  
The aim of this project is to provide a simple, low cost potentiostat for three electrode electrochemical sensors.  

Potentiostat based on *[Building a Microcontroller based potentiostat: A Inexpensive and versatile platform for teaching electrochemistry and instrumentation](https://pubs.acs.org/doi/10.1021/acs.jchemed.5b00961)* by **Gabriel N. Meloni** (*Universidade de São Paulo*).  


## Device  


## App  
Python base app was developed in order to provide an user interface for controlling and monitoring the sensor.  

### Installation  
#### Option 1: Compiled app  
- Extract files on any folder  
- Execute ***Potentiostat.exe***  
#### Option 2: Source code  *(with Powershell)*  
Python >= 3.10 needed.  
- Clone or download repository  
    ```powershell
    git clone https://github.com/Jaime-CET/CopoFoamat.git
    ```
- Install dependencies  
    ```powershell
    cd <repoFolder>\app\
    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    py -m pip install .
    ```
- Run program  
    ```powershell
    cd <repoFolder>\app\
    .\.venv\Scripts\Activate.ps1
    py .\src\main.py
    ```
### Compile app  
- Install dependencies  
    ```powershell
    cd <repoFolder>\app\
    .\.venv\Scripts\Activate.ps1
    py -m pip install .[dev]
    ```
- Compile project  
    ```powershell
    cd <repoFolder>\app\
    .\.venv\Scripts\Activate.ps1
    pyinstaller --name Potentiostat --onefile --windowed --icon=.\resources\icons\icon.ico .src\main\py
    ```
- Execute ***Potentiostat.exe***  

### Usage  
#### Connect device  
#### Run cycle  
#### Save data  
#### Load data  



> File structure:
> ```
> Potentiostat
> |--- dist
> |    |--- config
> |    |    `--- config.toml -> configuration parameters
> |    |--- data -> default folder for saving test data
> |    `--- themes -> folder for app themes
> `--- potentiostat.exe -> app executable
> ```