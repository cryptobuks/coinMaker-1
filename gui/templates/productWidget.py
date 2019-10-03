# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'productWidget.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(535, 311)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.graphicsView = GraphicsLayoutWidget(Form)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout.addWidget(self.graphicsView, 0, 1, 1, 1)
        self.frame_overview = QtWidgets.QFrame(Form)
        self.frame_overview.setMaximumSize(QtCore.QSize(180, 16777215))
        self.frame_overview.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_overview.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_overview.setObjectName("frame_overview")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame_overview)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout.addWidget(self.frame_overview, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
from pyqtgraph import GraphicsLayoutWidget
