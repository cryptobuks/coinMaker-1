from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt5.QtWidgets import QWidget

from .templates.bookOverview import Ui_Form


class BookModel(QAbstractTableModel):

    def __init__(self, product, book, transaction_type):
        self.book_list = book
        self.product = product
        self.header = ["Size", "Price"]
        self.transaction_type = transaction_type
        QAbstractTableModel.__init__(self)

    def rowCount(self, parent):
        try:
            return len(self.book_list[self.product][self.transaction_type])
        except KeyError:
            return 0

    def columnCount(self, parent):
        return len(self.header)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            if self.transaction_type == "asks":
                r = len(self.book_list[self.product][self.transaction_type]) - 1 - index.row()
            else:
                r = index.row()
            if index.column() == 0:
                c = 1
            else:
                c = 0
            return self.book_list[self.product][self.transaction_type][r][c]

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == 1:
            return self.header[section]

class BookOverview(QWidget, Ui_Form):

    def __init__(self, product, book, parent=None):
        self.book = book
        self.product = product
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.table_buy.setModel(BookModel(self.product, self.book, "asks"))
        self.table_sell.setModel(BookModel(self.product, self.book, "bids"))

    def slot_update(self):
        self.table_buy.model().layoutChanged.emit()
        self.table_buy.scrollToBottom()
        self.table_sell.model().layoutChanged.emit()