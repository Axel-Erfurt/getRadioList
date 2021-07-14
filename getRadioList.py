#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
made in October 2019 by Axel Schneider
https://github.com/Axel-Erfurt/
radio-browser
https://de1.api.radio-browser.info/
"""
##############
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPlainTextEdit, QLineEdit, QComboBox, QScrollBar, 
                              QPushButton, QFileDialog, QAction, QMenu, QMessageBox, QSlider)
from PyQt5.QtGui import QIcon, QTextCursor, QTextOption
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import requests
import xml.etree.ElementTree as ET

genres ="""Acoustic
Bluegrass 
Country
New Country
Classic Country
Country Rock
Western
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
        ### volume slider
        self.volSlider = QSlider()
        self.volSlider.setFixedWidth(100)
        self.volSlider.setOrientation(Qt.Horizontal)
        self.volSlider.valueChanged.connect(self.setVolume)
        self.volSlider.setMinimum(0)
        self.volSlider.setMaximum(100)
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
        self.statusBar().addPermanentWidget(self.volSlider)
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
        
        self.getForWebAction = QAction(QIcon.fromTheme("browser"), "copy for WebPlayer", self, triggered=self.getForWeb)
        self.volSlider.setValue(60)
        self.statusBar().showMessage("Welcome", 0)
        
    def setVolume(self):
        self.player.setVolume(self.volSlider.value())

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
        
    def getForWeb(self):
        t = self.field.textCursor().selectedText()
        name = t.partition(",")[0]
        url = t.partition(",")[2]
        result = f"<li><a class='chlist' href='{url}'>{name}</a></li>"
        clip = QApplication.clipboard()
        clip.setText(result)
        
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
            cmenu.addAction(self.getForWebAction)
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
        my_value = self.findfield.text()
        self.statusBar().showMessage("searching ...")
        base_url = "https://de1.api.radio-browser.info/xml/stations/byname/"
        url = f"{base_url}{my_value}"
        xml = requests.get(url).content.decode()
        if xml:
            root = ET.fromstring(xml)

            for child in root:
                ch_name = child.attrib["name"]
                ch_url = child.attrib["url"]
                self.field.appendPlainText(f"{ch_name},{ch_url}")    
                self.copyToClipboard()
                
                tc = self.field.textCursor()
                tc.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor)
                tc.select(QTextCursor.LineUnderCursor)
                tc.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                self.field.setTextCursor(tc)
                
        else:
            self.statusBar().showMessage("nothing found", 0)
            
        self.field.verticalScrollBar().triggerAction(QScrollBar.SliderToMinimum)
        self.field.horizontalScrollBar().triggerAction(QScrollBar.SliderToMinimum)

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
                    
    def copyToClipboard(self):
        clip = QApplication.clipboard()
        if not self.field.toPlainText() == "":
            clip.setText(self.field.toPlainText())

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
    
