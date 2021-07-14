#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
made in October 2019 by Axel Schneider
https://github.com/Axel-Erfurt/
radio-browser
https://de1.api.radio-browser.info/
"""
##############
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, QComboBox, 
                             QPushButton, QFileDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QUrl, QFileInfo
from PyQt5.QtWebEngineWidgets import QWebEngineView
import requests
import xml.etree.ElementTree as ET
from os import linesep

genres ="""Acoustic
Bluegrass 
Folk
Folk Rock
Grunge
Hard Rock
Blues
Oldies
Pop
Rock
Country
New Country
Classic Country
Country Rock
Western
Classic Rock
Classic
Beat
Metal
Dance
Disco
Funk
Hip-Hop
Jazz
New Age
Other
Rhythm and Blues
Rap
Reggae
Techno
Industrial
Alternative
Ska
Death Metal
Pranks
Soundtrack
Euro-Techno
Ambient
Trip-Hop
Vocal
Jazz & Funk
Fusion
Trance
Classical
Instrumental
Acid
House
Game
Sound clip
Gospel
Noise
Alternative Rock
Bass
Soul
Punk
Space
Meditative
Instrumental Pop
Instrumental Rock
Ethnic
Gothic
Darkwave
Techno-Industrial
Electronic
Pop-Folk
Eurodance
Dream
Southern Rock
Comedy
Cult
Gangsta
Top 40
Christian Rap
Pop/Funk
Jungle music
Native US
Cabaret
New Wave
Psychedelic
Rave
Showtunes
Trailer
Lo-Fi
Tribal
Acid Punk
Acid Jazz
Polka
Retro
Musical
Rock ’n’ Roll
Krautrock
"""

html_top = """<!DOCTYPE html>
<html>

  <head>
    <title>Radio Player</title>
    <script type="text/javascript" src="list.min.js"></script>
    <script type="text/javascript" src="jquery-1.10.1.js"></script>
    <link rel="stylesheet" href="player.css" media="all">
    <script src="player.js" async></script>
  </head>
  <div class="header">
    <a href="#top"><button class="buttontop" type="button">&#11121;</button></a>
  </div>

  <body>
    <div id='player'>
      <audio autoplay controls='' id='audio' preload='none' tabindex='0'>
        <source id="primarysrc" src=''></audio>
    </div>
    <div id="test">
      <input class="customSearch search" type="search" placeholder="find ..." />
      <ul id='playlist' class='list'>
"""

html_end = """      </ul>
    </div>
  </body>
</html>
"""

html_content = ""

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.webfile = f"{QFileInfo.path(QFileInfo(app.arguments()[0]))}/myradio.html"
        print(self.webfile)
        self.setGeometry(0, 0, 700, 800)
        self.setMaximumWidth(700)
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
        self.field = ""
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
        self.tb.addWidget(self.findfield)
        self.tb.addWidget(self.saveButton)
        self.tb.addWidget(self.savePlaylistButton)
        self.tb.addSeparator()
        self.tb.addWidget(self.combo)

        self.statusBar().showMessage("Welcome", 0)
        self.view = QWebEngineView()
        if QFileInfo(self.webfile).exists:
            self.view.load(QUrl.fromLocalFile(self.webfile))
        self.setCentralWidget(self.view)     
        
    def comboSearch(self):
        if self.combo.currentIndex() > 0:
            self.findfield.setText(self.combo.currentText())
            self.findStations()


    def findStations(self):
        html_content = html_top
        self.field = ""
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
                self.field += (f"{ch_name},{ch_url}")
                self.field += '\n'
#        mysearch = self.findfield.text()
#        self.statusBar().showMessage("searching ...")
#        rb = RadioBrowser()
#        myparams = {'name': 'search', 'nameExact': 'false', 'bitrateMin': 64}
#        
#        for key in myparams.keys():
#                if key == "name":
#                    myparams[key] = mysearch
#        
#        r = rb.station_search(params=myparams)
#        
#        n = ""
#        m = ""
#        for i in range(len(r)):
#            for key,value in r[i].items():
#                if str(key) == "name":
#                    n = value.replace(",", " ")
#                if str(key) == "url_resolved":
#                    m = value
#            if not n == "" and not m == "":
#                self.field += ("%s,%s" % (n, m.replace('\n', '')))
#                self.field += '\n'
#
        text = linesep.join([s for s in self.field.splitlines() if s]).splitlines()
                
        if not len(text) == 0:
            self.statusBar().showMessage("found "+ str(len(text)) + " '" + self.findfield.text() + "' Stations")
            for line in text:
                ch = line.split(",")
                if len(ch) > 1:
                    name = ch[0]
                    url = ch[1]
                    html_content += f"\t\t<li><a class='chlist' href='{url}'>{name}</a></li>"
            html_content += html_end
            with open(self.webfile, 'w') as f:
                f.write(html_content)
                f.close()
            
            self.view.load(QUrl.fromLocalFile(self.webfile))

            
        else:
            self.statusBar().showMessage("nothing found", 0)

    def saveStations(self):
        if not self.field == "":
            path, _ = QFileDialog.getSaveFileName(None, "RadioStations", self.findfield.text() + ".txt", "Text Files (*.txt)")
            if path:
                s = self.field
                with open(path, 'w') as f:
                    f.write(s)
                    f.close()
                    self.statusBar().showMessage("saved!", 0)

    def savePlaylist(self):
        if not self.field == "":
            path, _ = QFileDialog.getSaveFileName(None, "RadioStations", self.findfield.text() + ".m3u", "Playlist Files (*.m3u)")
            if path:
                result = ""
                s = self.field
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
QStatusBar
{
font-size: 8pt;
color: #ccc;
background: #202F1F;
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
QToolBar:separator
{
background: transparent;
border: 0px;
}
QMainWindow
{
background: #202F1F;
}
QLineEdit
{
background: #202F1F;
color: #ccc;
}
QPushButton
{
background: #202F1F;
color: #ccc;
}
QComboBox
{ 
background-color: #202F1F; 
 color: #ccc;
}
QListView
{ 
 background-color: darkgreen;
 color: #ccc;
}
QListView:hover
{ 
 background-color: orange;
 color: #ccc;
}
    """       

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    mainWin.findfield.setFocus()
    sys.exit(app.exec_())
    
