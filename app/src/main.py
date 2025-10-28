from sys import argv

from PyQt5.QtWidgets import QApplication
from utils import MY_APP, MY_CFG
from windows import MainWindow


def main() -> None:
    app = QApplication(argv)
    styleSheetFile: str = MY_APP['THEMES'] / f'{MY_CFG.app.theme}.qss'
    with open(styleSheetFile, 'r') as f:
        _style: str = f.read()
        app.setStyleSheet(_style)
    window: MainWindow = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
