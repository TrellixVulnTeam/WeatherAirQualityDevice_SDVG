# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\repos\weatherairqualitydevice\src\waqd\ui\widgets\calibration.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(339, 293)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.measure_value_text_label = QtWidgets.QLabel(Dialog)
        self.measure_value_text_label.setObjectName("measure_value_text_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.measure_value_text_label)
        self.measure_value_label = QtWidgets.QLabel(Dialog)
        self.measure_value_label.setText("")
        self.measure_value_label.setObjectName("measure_value_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.measure_value_label)
        self.display_value_text_label = QtWidgets.QLabel(Dialog)
        self.display_value_text_label.setObjectName("display_value_text_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.display_value_text_label)
        self.display_value_label = QtWidgets.QLabel(Dialog)
        self.display_value_label.setText("")
        self.display_value_label.setObjectName("display_value_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.display_value_label)
        self.verticalLayout.addLayout(self.formLayout)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.calib_spin_box = QtWidgets.QSpinBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calib_spin_box.sizePolicy().hasHeightForWidth())
        self.calib_spin_box.setSizePolicy(sizePolicy)
        self.calib_spin_box.setWrapping(True)
        self.calib_spin_box.setReadOnly(False)
        self.calib_spin_box.setAccelerated(True)
        self.calib_spin_box.setProperty("showGroupSeparator", False)
        self.calib_spin_box.setMinimum(-500)
        self.calib_spin_box.setMaximum(500)
        self.calib_spin_box.setSingleStep(10)
        self.calib_spin_box.setObjectName("calib_spin_box")
        self.verticalLayout.addWidget(self.calib_spin_box)
        self.zero_label = QtWidgets.QLabel(Dialog)
        self.zero_label.setWordWrap(True)
        self.zero_label.setObjectName("zero_label")
        self.verticalLayout.addWidget(self.zero_label)
        self.zero_button = QtWidgets.QPushButton(Dialog)
        self.zero_button.setObjectName("zero_button")
        self.verticalLayout.addWidget(self.zero_button)
        self.button_box = QtWidgets.QDialogButtonBox(Dialog)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.button_box.setObjectName("button_box")
        self.verticalLayout.addWidget(self.button_box)

        self.retranslateUi(Dialog)
        self.button_box.accepted.connect(Dialog.accept) # type: ignore
        self.button_box.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.measure_value_text_label.setText(_translate("Dialog", "Measure Value"))
        self.display_value_text_label.setText(_translate("Dialog", "Display Value"))
        self.label.setText(_translate("Dialog", "Manual offset"))
        self.zero_label.setText(_translate("Dialog", "Zero Calibration of Sensor - Please leave the sensor with outside quality air for at least 20 minutes before zeroing!"))
        self.zero_button.setText(_translate("Dialog", "Zero Calibration"))
