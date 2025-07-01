$thisFile = $MyInvocation.MyCommand.Path
$appFolder = $thisFile | Split-Path | Split-Path
cd $appFolder

pylupdate5 `
    .\src\windows\mainWindow.py `
    .\resources\ui\mainWindow.ui `
    .\src\managers\serial.py `
    .\src\managers\cycles.py `
    -ts .\resources\translation\mainWindow_es_ES.ts
pylupdate5 `
    .\src\windows\mainWindow.py `
    .\resources\ui\mainWindow.ui `
    .\src\managers\serial.py `
    .\src\managers\cycles.py `
    -ts .\resources\translation\mainWindow_pt_PT.ts

qt5-tools lrelease .\resources\translation\mainWindow_es_ES.ts -qm .\resources\translation\mainWindow_es_ES.qm
qt5-tools lrelease .\resources\translation\mainWindow_pt_PT.ts -qm .\resources\translation\mainWindow_pt_PT.qm
pyrcc5 .\resources\qrc\uiResources.qrc -o .\src\ui\uiResourcesRc.py
pyuic5 -x .\resources\ui\mainWindow.ui -o .\src\ui\mainWindowUi.py --from-imports --resource-suffix=Rc