from PyQt5.QtWidgets import QMainWindow

from .templates.mainWindow import  Ui_MainWindow
from .productWidget import ProductWidget

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, account, parent=None):
        self.account = account
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self._init_product_widgets()

    def _init_product_widgets(self):
        for product in self.account.products.keys():
            widget = ProductWidget(self.account, product)
            self.tabs_products.addTab(widget, product)