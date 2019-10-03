# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'bookOverview.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(157, 284)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.table_buy = QtWidgets.QTableView(Form)
        self.table_buy.setDragDropOverwriteMode(False)
        self.table_buy.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.table_buy.setShowGrid(False)
        self.table_buy.setGridStyle(QtCore.Qt.NoPen)
        self.table_buy.setObjectName("table_buy")
        self.table_buy.horizontalHeader().setVisible(False)
        self.table_buy.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.table_buy, 0, 0, 1, 1)
        self.table_sell = QtWidgets.QTableView(Form)
        self.table_sell.setDragDropOverwriteMode(False)
        self.table_sell.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.table_sell.setShowGrid(False)
        self.table_sell.setGridStyle(QtCore.Qt.NoPen)
        self.table_sell.setObjectName("table_sell")
        self.table_sell.horizontalHeader().setVisible(False)
        self.table_sell.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.table_sell, 1, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
