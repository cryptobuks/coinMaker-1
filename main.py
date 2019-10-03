import sys
import os

import yaml
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from account import Account
from broker import Broker
from bookFeed import BookFeed
from gui.mainWindow import MainWindow

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
app = QApplication(sys.argv)
app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

with open("./config.yml", "r") as o:
    config = yaml.load(o)
if config["sandbox"]:
    with open("sandbox_credentials.cfg", "r") as fp:
        key, secret, password = fp.readline().split(":")
else:
    with open("credentials.cfg", "r") as fp:
        key, secret, password = fp.readline().split(":")

my_account = Account(key, secret, password, sandbox=config["sandbox"])
broker = Broker(account=my_account, product_list=config["product_list"])

win = MainWindow(broker)
win.show()
app.exec()