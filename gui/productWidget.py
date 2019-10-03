from collections import deque

import pyqtgraph as pg
from PyQt5.QtCore import QTimer, pyqtSlot
from PyQt5.QtWidgets import QWidget

from gui.bookOverview import BookOverview
from .templates.productWidget import Ui_Form

pg.setConfigOption(u'background', u'w')
pg.setConfigOption(u'foreground', u"k")


class ProductWidget(QWidget, Ui_Form):

    def __init__(self, broker, product, parent=None):
        self.broker = broker
        self.product = product
        QWidget.__init__(self)
        self.speed_histogram_data = (deque([0], maxlen=120), deque([0], maxlen=120))
        self.amount_histogram_data = (deque([0], maxlen=120), deque([0], maxlen=120))
        self.price_histogram_data = (deque([0], maxlen=120), deque([0], maxlen=120))
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_speed_plots)
        self.update_timer.start(1000)
        self.setupUi(self)

    def setupUi(self, Form):
        super().setupUi(Form)
        self._init_speed_histogram()
        self._init_marker_overview()

    def _init_speed_histogram(self):
        self.speed_histogram = self.graphicsView.addPlot(0, 0)
        self.speed_histogram.setLabel(u"left", "Speed", units="tr/min")
        self.speed_a = self.speed_histogram.plot(range(len(self.speed_histogram_data[0]) + 1),
                                                 self.speed_histogram_data[0],
                                                 stepMode=True, fillLevel=0, brush=(0, 255, 0, 150))
        self.speed_b = self.speed_histogram.plot(range(len(self.speed_histogram_data[1]) + 1),
                                                 self.speed_histogram_data[1],
                                                 stepMode=True, fillLevel=0, brush=(255, 0, 0, 150))
        self.amount_histogram = self.graphicsView.addPlot(1, 0)
        self.amount_histogram.setLabel(u"left", "Amount", units="tr/min")
        self.amount_a = self.amount_histogram.plot(range(len(self.amount_histogram_data[0]) + 1),
                                                 self.amount_histogram_data[0],
                                                 stepMode=True, fillLevel=0, brush=(0, 255, 0, 150))
        self.amount_b = self.amount_histogram.plot(range(len(self.amount_histogram_data[1]) + 1),
                                                 self.amount_histogram_data[1],
                                                 stepMode=True, fillLevel=0, brush=(255, 0, 0, 150))
        self.price_histogram = self.graphicsView.addPlot(2, 0)
        self.price_histogram.setLabel(u"left", "Price", units="tr/min")
        self.price_a = self.price_histogram.plot(range(len(self.price_histogram_data[0]) + 1),
                                                   self.price_histogram_data[0],
                                                   stepMode=True, fillLevel=0, brush=(0, 255, 0, 150))
        self.price_b = self.price_histogram.plot(range(len(self.price_histogram_data[1]) + 1),
                                                   self.price_histogram_data[1],
                                                   stepMode=True, fillLevel=0, brush=(255, 0, 0, 150))

    @pyqtSlot()
    def update_speed_plots(self):
        try:
            buy_speed, sell_speed = self.broker.order_book[self.product]["speed"]
            self.speed_histogram_data[0].append(buy_speed)
            self.speed_histogram_data[1].append(sell_speed)
            buy_amount, sell_amount = self.broker.order_book[self.product]["amount"]
            self.amount_histogram_data[0].append(buy_amount)
            self.amount_histogram_data[1].append(sell_amount)
            buy_price, sell_price = self.broker.order_book[self.product]["price"]
            self.price_histogram_data[0].append(buy_price)
            self.price_histogram_data[1].append(sell_price)
            if self.isVisible():
                self.speed_a.setData(range(len(self.speed_histogram_data[0]) + 1), self.speed_histogram_data[0])
                self.speed_b.setData(range(len(self.speed_histogram_data[1]) + 1), self.speed_histogram_data[1])
                self.amount_a.setData(range(len(self.amount_histogram_data[0]) + 1), self.amount_histogram_data[0])
                self.amount_b.setData(range(len(self.amount_histogram_data[1]) + 1), self.amount_histogram_data[1])
                self.price_a.setData(range(len(self.price_histogram_data[0]) + 1), self.price_histogram_data[0])
                self.price_b.setData(range(len(self.price_histogram_data[1]) + 1), self.price_histogram_data[1])
                self.book_overview_widget.slot_update()
        except KeyError:
            pass

    def _init_marker_overview(self):
        self.book_overview_widget = BookOverview(self.product, self.broker.order_book)
        self.frame_overview.layout().addWidget(self.book_overview_widget)

