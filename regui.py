#!/usr/bin/env python

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import lxml.etree
import _thread
from mainwin import *
import find

class ReGui(QMainWindow, Ui_MainWindow):
    stopped = False
    update_progress = pyqtSignal(int, name='updateProgress')
    change_status = pyqtSignal(str, name='changeStatus')
    file_ready = pyqtSignal(name='fileLoadDone')

    def __init__(self):
        super(ReGui, self).__init__()
        self.setupUi(self)
        
        self.__init_table()

        self.__init_statusbar()
        self.__init_actions()

        self.__init_slots() 

        self.show()

    def __init_table(self):
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(
                ['ID', 'Sentence', 'Dependency'])
        
    def __init_slots(self):
        self.lineEdit.returnPressed.connect(self.__search)
        self.update_progress.connect(self.progressBar.setValue)
        self.change_status.connect(self.statusbar.showMessage)
        self.file_ready.connect(self.__on_file_ready)

    def __init_statusbar(self):
        self.statusbar.showMessage('Please load an XML file.')

    def __init_actions(self):
        self.action_open.setIcon(self.style().standardIcon(
                QStyle.SP_DialogOpenButton))
        self.action_exit_2.setIcon(self.style().standardIcon(
                QStyle.SP_DialogCloseButton))
        self.action_about.setIcon(self.style().standardIcon(
                QStyle.SP_MessageBoxInformation))
        self.action_search.setIcon(self.style().standardIcon(
                QStyle.SP_MediaPlay))
        self.action_stop.setIcon(self.style().standardIcon(
                QStyle.SP_MediaStop))
        self.action_clear.setIcon(self.style().standardIcon(
                QStyle.SP_DialogDiscardButton))

        self.action_about_qt.triggered.connect(QApplication.aboutQt)
        self.action_search.triggered.connect(self.__search)
        self.action_stop.triggered.connect(self.__do_stop)
        self.action_open.triggered.connect(self.__do_open)
        self.action_exit_2.triggered.connect(qApp.quit)
        self.action_about.triggered.connect(self.__about)
        self.action_clear.triggered.connect(self.lineEdit.clear)

    def __about(self):
        QMessageBox.information(self, 'About',
                'zsy 2012\nzsy056@gmail.com')

    def __get_sen_text(self, node):
        it = node.itertext()
        ret = ''
        try:
            while True:
                s = next(it).replace('\n', '').replace('$', '').strip()
                if s =='': continue
                ret = ret + s + ' '
        except StopIteration:
            pass
        return ret

    def __get_depen(self, node):
        ret = ''
        if node == None: return ret
        deps = node.findall('Item')
        for dep in deps:
            words = dep.findall('word')
            if len(words) != 2: continue
            s1 = words[0].text
            if s1==None: s1 = ''
            s2 = words[1].text
            if s2==None: s2 = ''
            ret = ret + dep.get('type') + '(' + s1 \
                    + '-' + words[0].get('value') + ', ' + s2 \
                    + '-' + words[1].get('value') + ')' + ' | '
        return ret


    def __do_search(self, query):
        self.action_stop.setEnabled(True)
        self.change_status.emit('Search...')
        self.update_progress.emit(0)
        i = 0
        counter = 0;
        length = len(self.sens)
        sel_sen = []
        for sen in self.sens:
            if self.stopped:
                self.change_status.emit('Stopped, found '
                        +str(counter)+' sentences')
                self.update_progress.emit(100)
                self.stopped = False
                return
            if find.is_sel(sen, query):
                counter = counter + 1
                sel_sen.append(sen)
            i = i + 1
            self.update_progress.emit(int(100*i/length))
        self.tableWidget.setRowCount(counter)
        self.change_status.emit('Ready, found '+str(counter)+' sentences')
        counter = 0
        for sen in sel_sen:
            counter = counter + 1
            itemId = QTableWidgetItem(sen.get('id'))
            itemId.setFlags(itemId.flags() & (~Qt.ItemIsEditable))
            self.tableWidget.setItem(counter-1, 0, itemId)
            itemText = QTableWidgetItem(
                    self.__get_sen_text(sen.find('ROOT')))
            itemText.setFlags(itemText.flags() & (~Qt.ItemIsEditable))
            self.tableWidget.setItem(counter-1, 1, itemText)
            itemDepend = QTableWidgetItem(
                    self.__get_depen(sen.find('Dependency')))
            itemDepend.setFlags(itemDepend.flags() & (~Qt.ItemIsEditable))
            self.tableWidget.setItem(counter-1, 2, itemDepend)
            itemLabel = QTableWidgetItem(str(counter))
            self.tableWidget.setVerticalHeaderItem(counter-1, itemLabel)

        self.action_stop.setEnabled(False)

    def __search(self):
        _thread.start_new_thread(self.__do_search,
                (self.lineEdit.text(),))

    def __do_stop(self):
        self.stopped = True
        self.action_stop.setEnabled(False)
        return None

    def __do_open(self):
        filename = QFileDialog.getOpenFileName(self,
                'Open English XML File', QDir.currentPath(),
                'XML files (*.xml);; XML files(*.xml)')
        if filename != '':
            self.__load_file(filename)

    def parseFile(self, filename):
        self.change_status.emit('Loading files...')
        self.update_progress.emit(50)
        self.sens = lxml.etree.parse(filename).findall('Sentence')
        self.update_progress.emit(100)
        self.change_status.emit('Ready')
        self.file_ready.emit()


    def __load_file(self, filename):
        _thread.start_new_thread(self.parseFile, (filename,))

    def __on_file_ready(self):
        self.action_search.setEnabled(True)

if __name__=='__main__':
    app = QApplication(sys.argv)
    mainwindow = ReGui()
    sys.exit(app.exec_())
