#!/usr/bin/python3
# -*- coding: utf-8 -*-
##############
"""
made in October 2019 by Axel Schneider
https://github.com/Axel-Erfurt/
Credits: André P. Santos (andreztz) for pyradios
https://github.com/andreztz/pyradios
radio-browser
http://www.radio-browser.info/webservice
"""
##############
from PyQt5.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QLineEdit, QPushButton, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from radios import RadioBrowser

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(0, 0, 700, 400)
        self.setContentsMargins(6, 6, 6, 6)
        self.setWindowTitle("Radio Stations - searching with pyradios")
        self.findfield = QLineEdit()
        self.findfield.setFixedWidth(250)
        self.findfield.addAction(QIcon.fromTheme("edit-find"), 0)
        self.findfield.setPlaceholderText("type search term and press RETURN ")
        self.findfield.returnPressed.connect(self.findStations)
        self.field = QPlainTextEdit()
        self.tb = self.addToolBar("tools")
        self.tb.setContextMenuPolicy(Qt.PreventContextMenu)
        self.tb.setMovable(False)
#        self.tb.setContentMargins(0, #0, 0, 6)
        self.setStyleSheet("QPlainTextEdit {background: #e9e9e9; font-size: 8pt; border: 1px outset #babdb6;} \
                                                                   QStatusBar { background: transparent; color: #888a85; border: 0px; font-size: 8pt;}QToolBar \
                                                                    {background: transparent; border: 0px;} QPushButton{background: #d3d7cf; \
                                                                            font-size: 8pt;} QLineEdit{background: #eeeeec; font-size: 8pt;}")
        self.saveButton = QPushButton("Save as txt")
        self.saveButton.setIcon(QIcon.fromTheme("document-save"))
        self.saveButton.clicked.connect(self.saveStations)
        self.savePlaylistButton = QPushButton("Save as m3u")
        self.savePlaylistButton.setIcon(QIcon.fromTheme("document-save"))
        self.savePlaylistButton.clicked.connect(self.savePlaylist)
        self.setCentralWidget(self.field)
        self.tb.addWidget(self.findfield)
        self.tb.addWidget(self.saveButton)
        self.tb.addWidget(self.savePlaylistButton)
        self.statusBar().showMessage("Welcome", 0)

    def findStations(self):
        self.field.setPlainText("")
        mysearch = self.findfield.text()
        self.statusBar().showMessage("searching ...")
        rb = RadioBrowser()
        myparams = {'name': 'search', 'nameExact': 'false'}
        
        for key in myparams.keys():
                if key == "name":
                    myparams[key] = mysearch
        
        r = rb.station_search(params=myparams)
        
        n = ""
        m = ""
        for i in range(len(r)):
            for key,value in r[i].items():
                if str(key) == "name":
                    n = value.replace(",", " ")
        #            print (n)
                if str(key) == "url":
                    m = value
                    self.field.appendPlainText("%s,%s" % (n, m))
        if not self.field.toPlainText() == "":
            self.statusBar().showMessage("found "+ str(self.field.toPlainText().count('\n')+1) + " '" + self.findfield.text() + "' Stations")
        else:
            self.statusBar().showMessage("nothing found", 0)

    def saveStations(self):
        if not self.field.toPlainText() == "":
            path, _ = QFileDialog.getSaveFileName(None, "RadioStations", self.findfield.text() + ".txt", "Text Files (*.txt)")
            if path:
                s = self.field.toPlainText()
                with open(path, 'w') as f:
                    f.write(s)
                    f.close()
                    self.statusBar().showMessage("saved!", 0)

    def savePlaylist(self):
        if not self.field.toPlainText() == "":
            path, _ = QFileDialog.getSaveFileName(None, "RadioStations", self.findfield.text() + ".m3u", "Playlist Files (*.m3u)")
            if path:
                result = ""
                s = self.field.toPlainText()
                st = []
                for line in s.splitlines():
                    st.append(line)
                result += "#EXTM3U"
                result += '\n'
                for x in range(len(st)):
                    result += "#EXTINF:" + str(x) + "," +  st[x].partition(",")[0]
                    result += '\n'
                    result += st[x].partition(",")[2]
                    result += '\n'
                with open(path, 'w') as f:
                    f.write(result)
                    f.close()
                    self.statusBar().showMessage("saved!", 0)

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    mainWin.findfield.setFocus()
    sys.exit(app.exec_())