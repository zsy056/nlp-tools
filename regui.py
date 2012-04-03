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
        hor_labels = ['ID', 'Sentence', 'Dependency']
        self.tw_eng.setColumnCount(3)
        self.tw_eng.setHorizontalHeaderLabels(hor_labels)
        self.tw_chn.setColumnCount(3)
        self.tw_chn.setHorizontalHeaderLabels(hor_labels)
        # Sync the scroll bar of the two table
        sb_en = self.tw_eng.verticalScrollBar()
        sb_cn = self.tw_chn.verticalScrollBar()
        sb_en.valueChanged.connect(sb_cn.setValue)
        sb_cn.valueChanged.connect(sb_en.setValue)
        
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

    def __set_tw_item(self, tw, sen, counter):
        itemId = QTableWidgetItem(sen.get('id'))
        itemId.setFlags(itemId.flags() & (~Qt.ItemIsEditable))
        tw.setItem(counter-1, 0, itemId)
        itemText = QTableWidgetItem(
                find.get_sen_text(sen.find('ROOT')))
        itemText.setFlags(itemText.flags() & (~Qt.ItemIsEditable))
        tw.setItem(counter-1, 1, itemText)
        itemDepend = QTableWidgetItem(
                self.__get_depen(sen.find('Dependency')))
        itemDepend.setFlags(
                itemDepend.flags() & (~Qt.ItemIsEditable))
        tw.setItem(counter-1, 2, itemDepend)
        itemLabel = QTableWidgetItem(str(counter))
        tw.setVerticalHeaderItem(counter-1, itemLabel)

    def __do_search(self, query):
        self.action_stop.setEnabled(True)
        self.change_status.emit('Search...')
        self.update_progress.emit(0)
        if self.rbtn_eng.isChecked():
            master_tw, slave_tw = self.tw_eng, self.tw_chn
            master_sens, slave_sens = self.eng_sens, self.chn_sens
        else:
            master_tw, slave_tw = self.tw_chn, self.tw_eng
            master_sens, slave_sens = self.chn_sens, self.eng_sens
        i = 0
        counter = 0;
        length = len(master_sens)
        sel_sen = []
        for sen in master_sens:
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
        master_tw.setRowCount(counter)
        slave_tw.setRowCount(counter)
        self.change_status.emit('Ready, found '+str(counter)+' sentences')
        counter = 0
        for sen in sel_sen:
            counter = counter + 1
            # master
            self.__set_tw_item(master_tw, sen, counter)
            # slave
            idx = int(sen.get('id'))-1
            if idx < len(slave_sens):
                self.__set_tw_item(slave_tw,
                        slave_sens[idx], counter)

        self.action_stop.setEnabled(False)

    def __search(self):
        _thread.start_new_thread(self.__do_search,
                (self.lineEdit.text(),))

    def __do_stop(self):
        self.stopped = True
        self.action_stop.setEnabled(False)
        return None

    def __do_open(self):
        self.eng_filename = QFileDialog.getOpenFileName(self,
                'Open English XML File', QDir.currentPath(),
                'XML files (*.xml);; XML files(*.xml)')
        if self.eng_filename != '':
            self.chn_filename = QFileDialog.getOpenFileName(self,
                    'Open Chinese XML File', QDir.currentPath(),
                    'XML files (*.xml);; XML files(*.xml)')
            if self.chn_filename != '': self.__load_files()

    def __parseFile(self):
        self.change_status.emit('Loading files...')
        self.update_progress.emit(10)
        self.eng_sens = lxml.etree.parse(
                self.eng_filename).findall('Sentence')
        self.update_progress.emit(50)
        self.chn_sens = lxml.etree.parse(
                self.chn_filename).findall('Sentence')
        self.update_progress.emit(100)
        self.change_status.emit('Ready')
        self.file_ready.emit()

    def __load_files(self):
        _thread.start_new_thread(self.__parseFile, ())

    def __on_file_ready(self):
        self.action_search.setEnabled(True)

if __name__=='__main__':
    app = QApplication(sys.argv)
    mainwindow = ReGui()
    sys.exit(app.exec_())
