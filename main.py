import os
import sys

import yaml
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from account import Account
from broker_max_amout import BrokerMaxAmount
from gui.mainWindow import MainWindow

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
app = QApplication(sys.argv)
app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

with open("./config.yml", "r") as o:
# with open("./config_sandbox.yml", "r") as o:
    config = yaml.load(o)
with open(config["credentials_file"], "r") as fp:
    key, secret, password = fp.readline().split(":")

my_account = Account(key, secret, password, sandbox=config["sandbox"])
broker = BrokerMaxAmount(account=my_account, config=config)
win = MainWindow(broker)
win.show()
app.exec()
