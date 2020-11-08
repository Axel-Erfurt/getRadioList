#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
made in October 2019 by Axel Schneider
https://github.com/Axel-Erfurt/
Credits: André P. Santos (andreztz) for pyradios
https://github.com/andreztz/pyradios
Copyright (c) 2018 André P. Santos
radio-browser
https://www.radio-browser.info/#!/
"""
##############
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPlainTextEdit, QLineEdit, QComboBox, 
                                                            QPushButton, QFileDialog, QAction, QMenu, QMessageBox)
from PyQt5.QtGui import QIcon, QTextCursor, QTextOption
from PyQt5.QtCore import Qt, QUrl
from radios import RadioBrowser
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from urllib import request
import requests

genres ="""Acoustic
Bluegrass 
Country
New Country
Classic Country
Country Rock
Cowboy / Western
Folk
Folk Rock
Grunge
Hard Rock
Blues
Oldies
Pop
Rock
Classic Rock
Classic
Beat
Metal
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(0, 0, 700, 400)
        self.setContentsMargins(6, 6, 6, 6)
        self.setStyleSheet(myStyleSheet(self))
        self.setWindowTitle("Radio Stations - searching with pyradios")
        self.genreList = genres.splitlines()
        self.findfield = QLineEdit()
        self.findfield.setFixedWidth(250)
        self.findfield.addAction(QIcon.fromTheme("edit-find"), 0)
        self.findfield.setPlaceholderText("type search term and press RETURN ")
        self.findfield.returnPressed.connect(self.findStations)
        self.findfield.setClearButtonEnabled(True)
        self.field = QPlainTextEdit()
        self.field.setContextMenuPolicy(Qt.CustomContextMenu)
        self.field.customContextMenuRequested.connect(self.contextMenuRequested)
        self.field.cursorPositionChanged.connect(self.selectLine)
        self.field.setWordWrapMode(QTextOption.NoWrap)
        ### genre box
        self.combo = QComboBox()
        self.combo.currentIndexChanged.connect(self.comboSearch)
        self.combo.addItem("choose Genre")
        for m in self.genreList:
            self.combo.addItem(m)
        self.combo.addItem("Country")
        self.combo.setFixedWidth(150)
        ### toolbar ###
        self.tb = self.addToolBar("tools")
        self.tb.setContextMenuPolicy(Qt.PreventContextMenu)
        self.tb.setMovable(False)
#        self.tb.setContentMargins(0, #0, 0, 6)
        #self.setStyleSheet("QPlainTextEdit {background: #e9e9e9; font-size: 8pt; border: 1px outset #babdb6;} \
        #                                                           QStatusBar { background: transparent; color: #888a85; border: 0px; font-size: 8pt;}QToolBar \
        #                                                            {background: transparent; border: 0px;} QPushButton{background: #d3d7cf; \
        #                                                                    font-size: 8pt;} QLineEdit{background: #eeeeec; font-size: 8pt;}")
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
        self.tb.addSeparator()
        self.tb.addWidget(self.combo)
        ### player ###
        self.player = QMediaPlayer()
        self.player.metaDataChanged.connect(self.metaDataChanged)
        self.startButton = QPushButton("Play")
        self.startButton.setIcon(QIcon.fromTheme("media-playback-start"))
        self.startButton.clicked.connect(self.getURLtoPlay)
        self.stopButton = QPushButton("Stop")
        self.stopButton.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.stopButton.clicked.connect(self.stopPlayer)
        self.statusBar().addPermanentWidget(self.startButton)
        self.statusBar().addPermanentWidget(self.stopButton)
        ## actions
        self.getNameAction = QAction(QIcon.fromTheme("edit-copy"), "copy Station Name", self, triggered=self.getName)
        self.getUrlAction = QAction(QIcon.fromTheme("edit-copy"), "copy Station URL", self, triggered=self.getURL)
        self.getNameAndUrlAction = QAction(QIcon.fromTheme("edit-copy"), "copy Station Name,URL", self, triggered=self.getNameAndUrl)
        self.getURLtoPlayAction = QAction(QIcon.fromTheme("media-playback-start"), "play Station", self, shortcut="F6", triggered=self.getURLtoPlay)
        self.addAction(self.getURLtoPlayAction)
        self.stopPlayerAction = QAction(QIcon.fromTheme("media-playback-stop"), "stop playing", self, shortcut="F7", triggered=self.stopPlayer)
        self.addAction(self.stopPlayerAction)
        self.helpAction = QAction(QIcon.fromTheme("help-info"), "Help", self, shortcut="F1", triggered=self.showHelp)
        self.addAction(self.helpAction)
        self.statusBar().showMessage("Welcome", 0)

    def comboSearch(self):
        if self.combo.currentIndex() > 0:
            self.findfield.setText(self.combo.currentText())
            self.findStations()

    def getName(self):
        t = self.field.textCursor().selectedText().partition(",")[0]
        clip = QApplication.clipboard()
        clip.setText(t)

    def getURL(self):
        t = self.field.textCursor().selectedText().partition(",")[2]
        clip = QApplication.clipboard()
        clip.setText(t)

    def getNameAndUrl(self):
        t = self.field.textCursor().selectedText()
        clip = QApplication.clipboard()
        clip.setText(t)
        
    def selectLine(self):
        tc = self.field.textCursor()
        tc.select(QTextCursor.LineUnderCursor)
        tc.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor) ##, 
        tc.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        self.field.setTextCursor(tc)

    def showHelp(self):
        QMessageBox.information(self, "Information", "F6 -> play Station (from line where cursor is)\nF7 -> stop playing")

    def stopPlayer(self):
        self.player.stop()
        self.statusBar().showMessage("Player stopped", 0)

    ### QPlainTextEdit contextMenu
    def contextMenuRequested(self, point):
        cmenu = QMenu()
        if not self.field.toPlainText() == "":
            cmenu.addAction(self.getNameAction)
            cmenu.addAction(self.getUrlAction)
            cmenu.addAction(self.getNameAndUrlAction)
            cmenu.addSeparator()
            cmenu.addAction(self.getURLtoPlayAction)
            cmenu.addAction(self.stopPlayerAction)
            cmenu.addSeparator()
            cmenu.addAction(self.helpAction)
        cmenu.exec_(self.field.mapToGlobal(point))  

    def getURLtoPlay(self):
        url = ""
        tc = self.field.textCursor()
        rtext = tc.selectedText().partition(",")[2]
        stext = tc.selectedText().partition(",")[0]
        url = rtext
        print("stream url=", url)
        self.player.setMedia(QMediaContent(QUrl(url)))
        self.player.play()
        self.statusBar().showMessage("%s %s" % ("playing", stext), 0)

    def metaDataChanged(self):
        if self.player.isMetaDataAvailable():
            trackInfo = (self.player.metaData("Title"))
            trackInfo2 = (self.player.metaData("Comment"))
            if not trackInfo == None:
                self.statusBar().showMessage(trackInfo, 0)
                if not trackInfo2 == None:
                   self.statusBar().showMessage("%s %s" % (trackInfo, trackInfo2))

    def findStations(self):
        self.field.setPlainText("")
        mysearch = self.findfield.text()
        self.statusBar().showMessage("searching ...")
        rb = RadioBrowser()
        myparams = {'name': 'search', 'nameExact': 'false', 'bitrateMin': 64}
        
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
                if str(key) == "url_resolved":
                    m = value
            if not n == "" and not m == "":
                self.field.appendPlainText("%s,%s" % (n, m.replace('\n', '')))
                
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

def myStyleSheet(self):
    return """
QPlainTextEdit
{
background: #eeeeec;
color: #202020;
}
QStatusBar
{
font-size: 8pt;
color: #555753;
}
QMenuBar
{
background: transparent;
border: 0px;
}
QToolBar
{
background: transparent;
border: 0px;
}
QMainWindow
{
     background: qlineargradient(y1: 0, y2: 1,
                                 stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                 stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
}
QLineEdit
{
     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                 stop: 0 #E1E1E1, stop: 0.4 #e5e5e5,
                                 stop: 0.5 #e9e9e9, stop: 1.0 #d2d2d2);
}
QPushButton
{
background: #D8D8D8;
}
    """       

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    mainWin.findfield.setFocus()
    sys.exit(app.exec_())
    
