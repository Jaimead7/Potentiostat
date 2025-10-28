import logging
from pathlib import Path

from pyUtils import (ConfigFileManager, MyLogger, ProjectPathsDict,
                     save_pyutils_logs, set_pyutils_logging_level,
                     set_pyutils_logs_path)

# APP
MY_APP: ProjectPathsDict = ProjectPathsDict().set_app_path(Path(__file__).parents[2])
MY_APP[ProjectPathsDict.DIST_PATH] = MY_APP[ProjectPathsDict.APP_PATH] / 'dist'
MY_APP['DATA'] = MY_APP[ProjectPathsDict.DIST_PATH] / 'data'
MY_APP['THEMES'] = MY_APP[ProjectPathsDict.DIST_PATH] / 'themes'
MY_APP[ProjectPathsDict.CONFIG_PATH] = MY_APP[ProjectPathsDict.DIST_PATH] / 'config'
MY_APP[ProjectPathsDict.CONFIG_FILE_PATH] = MY_APP[ProjectPathsDict.CONFIG_PATH] / 'config.toml'

# LOGGING
LOGGING_LVL: int = MyLogger.get_logging_lvl_from_env('LOGGING_LVL')

my_logger = MyLogger(
    logger_name= f'Potentiostat',
    logging_level= LOGGING_LVL
)

def set_potentiostat_logs_path(new_path: Path | str) -> None:
    my_logger.logs_file_path = new_path
    set_pyutils_logs_path(new_path)

def save_potentiostat_logs(value: bool) -> None:
    my_logger.save_logs = value
    save_pyutils_logs(value)

def set_potentiostat_logging_level(lvl: int = logging.DEBUG) -> None:
    my_logger.set_logging_level(lvl)
    set_pyutils_logging_level(lvl)

set_potentiostat_logging_level(logging.WARNING)
set_potentiostat_logs_path('potentiostat.log')
set_potentiostat_logging_level(LOGGING_LVL)
save_potentiostat_logs(True)


# CONFIG
MY_CFG: ConfigFileManager = ConfigFileManager(MY_APP[ProjectPathsDict.CONFIG_FILE_PATH])
