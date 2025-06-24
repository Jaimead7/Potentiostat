from sys import argv

from PyQt5.QtWidgets import QApplication
from pyUtils import ConfigFileManager, ProjectPathsDict, ppaths
from windows import *


def main() -> None:
    app = QApplication(argv)
    myCfg = ConfigFileManager(ppaths[ProjectPathsDict.CONFIG_FILE_PATH])
    styleSheetFile: str = ppaths[ProjectPathsDict.DIST_PATH] / 'themes' / f'{myCfg.app.theme}.qss'
    with open(styleSheetFile, 'r') as f:
        _style: str = f.read()
        app.setStyleSheet(_style)
    window: MainWindow = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
