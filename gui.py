import os
import pickle
import re
import sys

import requests
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from login import login
from profiledler import ProfileDler
from storydler import StoryDler

qt_app = QApplication(sys.argv)


class Responsive(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setAutoFillBackground(True)
        if sys.platform == 'windows':
            self.dirspace = '\\'
        else:
            self.dirspace = '/'


        self.setWindowTitle('IG-DLer')
        self.setMinimumWidth(400)
        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.targetProfile = QLineEdit(self)
        self.spacer = QLabel(self)
        self.form_layout.addRow(self.spacer)
        self.form_layout.addRow('Target Profile: ', self.targetProfile)
        self.toShow = 0
        self.session = requests.Session()
        self.toformShow = 0
        self.userName = ''
        self.options = [
            'Select the tool you wish to use',
            'Download Dp',
            'Download Post'
        ]
        self.opBox = QComboBox(self)
        self.opBox.addItems(self.options)
        self.opBox.activated.connect(self.filterShow)
        self.errorhb = QHBoxLayout()
        self.errorLabel = QLabel(
            'ERORR! NO TOOLS SECIFIED! PLEASE SELECT THE TOOL FIRST!', self)
        self.errorLabel.hide()
        self.errorhb.addStretch()
        self.errorhb.addWidget(self.errorLabel)
        self.errorhb.addStretch()

        self.radio = QRadioButton(self)
        self.radio.clicked.connect(self.formShow)
        self.radioLabel = QLabel("Login:", self)
        self.form_layout.addRow('Tool:', self.opBox)
        self.form_layout.addRow(self.errorhb)
        self.filter = QLineEdit(self)
        self.label = QLabel('Filter: ', self)

        self.boxLayout = QHBoxLayout()
        self.boxLayout.addWidget(self.radioLabel)
        self.boxLayout.addWidget(self.radio)

        self.boxLayout.addStretch(-50)

        self.boxLayout.addWidget(self.label)
        self.boxLayout.addWidget(self.filter)
        self.form_layout.addRow(self.boxLayout)

        self.userBox = QHBoxLayout()
        self.username = QLineEdit(self)
        self.userLabel = QLabel("Username:", self)
        self.userBox.addWidget(self.userLabel)
        self.userBox.addWidget(self.username)
        self.username.editingFinished.connect(self.user)

        self.form_layout.addRow(self.spacer)
        self.form_layout.addRow(self.userBox)

        self.passBox = QHBoxLayout()
        self.password = QLineEdit(self)
        self.passLabel = QLabel("Password:", self)

        self.passBox.addWidget(self.passLabel)
        self.passBox.addWidget(self.password)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.textEdited.connect(self.passW)

        self.showHide = QToolButton(self.password)
        self.showHide.setText('Show')
        self.showHide.setCursor(Qt.PointingHandCursor)
        self.showHide.setFocusPolicy(Qt.NoFocus)
        self.showHide.setStyleSheet("background: transparent; border: none;")
        self.showHide.clicked.connect(self.showOrHide)

        passLayout = QHBoxLayout(self.password)
        passLayout.addWidget(self.showHide, 0, Qt.AlignRight)

        passLayout.setSpacing(0)
        passLayout.setContentsMargins(5, 5, 5, 5)
        self.form_layout.addRow(self.passBox)

        self.errorBox = QHBoxLayout()
        self.noLogin = QLabel(self)
        self.loginButton = QPushButton('Login', self)
        self.loginButton.hide()
        self.loginButton.clicked.connect(self.loginClicked)
        self.noLogin.hide()
        self.errorBox.addWidget(self.noLogin)
        self.errorBox.addStretch(1)
        self.errorBox.addWidget(self.loginButton)
        self.form_layout.addRow(self.errorBox)

        self.progress = QProgressBar(self)
        self.progress.setValue(0)
        self.runButton = QPushButton('Run', self)
        self.runButton.clicked.connect(self.onClicked)
        self.runBox = QHBoxLayout()
        self.runBox.addWidget(self.runButton, 0, Qt.AlignCenter)
        self.form_layout.addRow(self.spacer)

        self.form_layout.addRow(self.runBox)

        self.form_layout.addRow(self.spacer)
        self.form_layout.addRow(self.spacer)

        self.form_layout.addRow(self.progress)
        self.form_layout.addRow(self.spacer)
        self.quitBtnLayout = QHBoxLayout()
        self.quitBtnLayout.addStretch(1)
        self.quitBtn = QPushButton('Exit', self)
        self.quitBtnLayout.addWidget(self.quitBtn)
        self.quitBtn.clicked.connect(self.close)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.username.hide(), self.userLabel.hide()
        self.passLabel.hide(), self.password.hide()
        self.filter.hide(), self.label.hide()

        self.form_layout.addRow(self.output)
        self.form_layout.addRow(self.quitBtnLayout)
        self.layout.addLayout(self.form_layout)

        self.setLayout(self.layout)

    def passW(self):
        self.passWord = self.password.text()

    def user(self):
        self.userName = self.username.text()
        if os.path.exists('cookies'+self.dirspace+self.userName):
            self.loginButton.hide()
            self.noLogin.hide()
            self.password.hide()
            self.passLabel.hide()
        else:
            self.errorDisplay(
                'No cookiefile for this account found :( Please Login first!')
            self.loginButton.show()
            self.noLogin.show()
            self.password.show()
            self.passLabel.show()

    def loginClicked(self):
        if self.passWord != '' and self.userName != '':
            regex = r'^[a-zA-Z0-9\.\_]+$'
            self.noLogin.hide()
            if re.match(regex, self.userName):
                a = login(self.userName, self.passWord)
                if a == "Login Unsucessful! :(":
                    self.errorDisplay('Login Unsuccessful :( Please try again!')
                    self.noLogin.show()
                else:
                    self.passBox.addWidget(QLabel('Login Successful!',self))
                    self.noLogin.hide()
            else:
                self.errorDisplay(
                    'Invalid Username :( Please specify a valid username!')
                self.noLogin.show()
        else:
            self.errorDisplay(
                'Some fields are empty! Please fill all the fields!')
            self.noLogin.show()
        self.loginButton.hide()

    def run(self):
        self.show()
        qt_app.exec_()

    def onClicked(self):
        self.progress.setValue(0)
        while True:
            self.targetUser = self.targetProfile.text()
            if self.targetUser == '':
                self.errorDisplay('No Target Specified')
                self.noLogin.show()
                break
            else:
                self.noLogin.hide()
            if self.toformShow % 2 != 0:
                if os.path.exists('cookies'+self.dirspace+self.userName):
                    with open(('cookies'+self.dirspace+self.userName), 'rb') as f:
                        self.session.cookies.update(pickle.load(f))
                else:
                    break
            currTool = self.opBox.currentText()
            if currTool != self.options[0]:
                self.errorLabel.hide()
                if currTool == self.options[1]:
                    ProfileDler(self.targetUser, blk=self.output,
                                progress=self.progress).execute()
                elif currTool == self.options[2]:
                    ProfileDler(self.targetUser, blk=self.output,
                                progress=self.progress, session=self.session, _filter=self.filter.text()).profile_iterator()
                elif currTool == 'Download Highlights':
                    StoryDler(self.targetUser, blk=self.output, progress=self.progress,
                              session=self.session, _filter_title=self.filter.text()).getHighlightId()
                elif currTool == 'Download Stories':
                    StoryDler(self.targetUser, blk=self.output, progress=self.progress,
                              session=self.session).download_stories()
                else:
                    pass
            else:
                self.errorLabel.show()
                break
            break

    def errorDisplay(self, text):
        self.noLogin.setText('ERROR: '+text)

    def formShow(self):
        self.toformShow += 1
        if self.toformShow % 2 == 0:
            self.username.hide()
            self.userLabel.hide()
            self.passLabel.hide()
            self.password.hide()
            self.loginButton.hide()
            self.username.setText('')
            self.opBox.removeItem(4)
            self.opBox.removeItem(3)

        else:
            self.username.show()
            self.userLabel.show()
            self.opBox.addItem('Download Stories')
            self.opBox.addItem('Download Highlights')

    def filterShow(self):
        if self.opBox.currentText() != self.options[0]:
            self.errorLabel.hide()
            if self.opBox.currentText().lower() == 'download highlights' or self.opBox.currentText().lower() == 'download post':
                self.filter.show()
                self.label.show()
                if self.opBox.currentText().lower() == 'download highlights':
                    self.filter.setPlaceholderText('highlight name')
                else:
                    self.filter.setPlaceholderText('shortcode')
            else:
                self.filter.hide()
                self.label.hide()
        else:
            self.errorLabel.show()
            self.filter.hide()
            self.label.hide()

    def showOrHide(self):
        self.toShow += 1
        if self.toShow % 2 != 0:
            self.password.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.showHide.setText('Hide')

        else:
            self.password.setEchoMode(QtWidgets.QLineEdit.Password)
            self.showHide.setText('Show')

app = Responsive()
app.run()
