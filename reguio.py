#!/usr/bin/env python

import sys
from PyQt4 import QtGui

class ReGui(QtGui.QMainWindow):
    def __init__(self):
        super(ReGui, self).__init__()

        self.initUI()

    def initUI(self):
        self.initActions()
        self.initMainWindow()
        self.initStatusBar()
        self.initSearchBtn()
        self.initToolBar()
        self.show()

    def initMainWindow(self):
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('ReGui')

    def initSearchBtn(self):
        searchBtn = QtGui.QPushButton('Search', self)
        searchBtn.resize(searchBtn.sizeHint())
        searchBtn.move(50, 50)

    def initStatusBar(self):
         self.statusBar().showMessage('Ready')

    def initToolBar(self):
        self.toolbar = self.addToolBar('ToolBar')
        self.toolbar.addAction(self.openAction)
        self.toolbar.addAction(self.exitAction)

    def initActions(self):
        self.openAction = QtGui.QAction(
                self.style().standardIcon(
                    QtGui.QStyle.SP_DialogOpenButton),
                '&Open', self)
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.setStatusTip('Open an XML file')

        self.exitAction = QtGui.QAction(
                self.style().standardIcon(
                    QtGui.QStyle.SP_DialogCloseButton),
                '&Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(QtGui.qApp.quit)

def main():
    app = QtGui.QApplication(sys.argv)
    regui = ReGui()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()

     
