from pyUtils import Styles, debugLog

from .cycles import CyclicVoltammetryManager, PotentiometryManager
from .plot import PlotManager
from .serial import SerialManager

debugLog('Module loaded: managers', Styles.GREEN)
