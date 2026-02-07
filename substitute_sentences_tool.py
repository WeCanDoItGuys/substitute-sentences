"""Created on Tue Feb  3 14:29:13 2026"""
"""Substitute Sentences GUI (outputs substitution cyphers using valid English words for user's input phrase)
   Copyright (C) 2026 WeCanDoItGuys <https://www.gnu.org/licenses/>."""

import find_substitute_sentences as ss
from functools import partial
from PyQt5 import QtWidgets, uic, QtGui, QtCore #pip install pyqt5
import sys, os

SS_UI = "gui/SS.ui"  #Substitute Sentences ui file, view in QT designer

class ssGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(ssGUI, self).__init__()
        uic.loadUi(SS_UI,self) #loads the ui file containing the positions/names/behaviors/etc of the Qt widgets used in this GUI.
        self.setTextboxValidators() # prevents user from typing illegal input into a given text entry box
        self.addFunctionsToButtons()
        self.phraseInput.returnPressed.connect(self.submitPhrase)
        self.setFontSize(18)
        self.outputFolder=None
        self.defaultOutputFolder=os.path.dirname(os.path.realpath(__file__)) + '/out'
        
    def setFontSize(self, fontSize):
        self.origWindowGeom = [0,0,self.width(),self.height()]
        labelFont = QtGui.QFont()
        labelFont.setPixelSize(int(fontSize*min(float(self.width())/self.origWindowGeom[2],float(self.height())/self.origWindowGeom[3])))
        self.setFont(labelFont) #I can't figure out how to adjust the label's pointSize directly.

    def setTextboxValidators(self):
        letters_spaces = QtCore.QRegExp("[a-zA-Z\\s]+")
        allowedPhrases = QtGui.QRegExpValidator(letters_spaces)
        inputBoxes = [self.phraseInput,]
        for inputBox in inputBoxes:
            inputBox.setValidator(allowedPhrases)

    def addFunctionsToButtons(self):
        self.submitPhraseButton.clicked.connect(self.submitPhrase)
        self.outputFolderButton.clicked.connect(self.browse)

    def updateDropdown(self,i):
        outfname=self.outfname_from_phrase(self.input_phrase)
        if not os.path.exists(outfname): 
            return
        dropdowns = self.scrollArea.widget().findChildren(QtWidgets.QComboBox)
        dropdown = dropdowns[i]
        self.chosen[i] = dropdown.currentText() #for sequential filtering
        with open(outfname) as f:
            phrases = frozenset({p for p in f if all(p.split()[k]==self.chosen[k] for k in self.chosen)})
        dropdown_data = self.get_dropdown_data(phrases)
        self.update_dropdowns(dropdown_data, i) 

    def syncDropdownsWithOtherDropdowns(self):
        dropdowns=self.scrollArea.widget().findChildren(QtWidgets.QComboBox)
        for i in range(len(dropdowns)):
            setattr(self,f'updateDropdown_{i}',partial(self.updateDropdown,i=i))
            dropdowns[i].activated.connect(getattr(self,f'updateDropdown_{i}'))
        
    def outfname_from_phrase(self,phrase):
        if self.outputFolder is None:
            self.outputFolder=self.defaultOutputFolder
            if not os.path.isdir(self.outputFolder):
                os.mkdir(self.outputFolder)
        return self.outputFolder+'/'+phrase.replace(' ','_')+'.txt'
    
###################################################     BUTTONS      ###################################################################################################################
    def browse(self):
        suggested=self.outputFolder if os.path.isdir(self.outputFolder) else None
        folder = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a folder:',suggested, QtWidgets.QFileDialog.ShowDirsOnly)
        if os.path.isdir(folder):
            self.outputFolder=folder

    def submitPhrase(self):
        self.initVariables()
        
        outfname=self.outfname_from_phrase(self.input_phrase)
        if os.path.exists(outfname): #pull from file if already found
            with open(outfname) as f:
                phrases=[line.strip('\n') for line in f]
        else:
            phrases=ss.find_substitutes(self.input_phrase)
            if self.exportCheckBox.isChecked():
                self.export(phrases)
        
        dropdown_data = self.get_dropdown_data(phrases)
        self.display_dropdowns(dropdown_data)

    def get_dropdown_data(self, phrases):
        return {i: sorted({p.split()[i] for p in phrases}) for i in range(len(self.input_phrase.split()))}

    def initVariables(self):
        self.input_phrase=self.phraseInput.text()
    
    def export(self, phrases):
        outfname=self.outfname_from_phrase(self.input_phrase)
        with open(outfname,'w') as f:
            f.write('\n'.join(phrases))
    
    def update_dropdowns(self,dropdown_data,exclude):
        for d in dropdown_data:
            if d!=exclude:
                getattr(self,f"phraseDropdown{d}").clear()
                getattr(self,f"phraseDropdown{d}").addItems(dropdown_data[d])
                getattr(self,f"phraseDropdown{d}").setMaxVisibleItems(len(dropdown_data[d]))
                getattr(self,f"phraseDropdown{d}").showPopup()
    
    def display_dropdowns(self,dropdown_data):
        content_widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(content_widget)
        layout.setAlignment(QtCore.Qt.AlignTop)

        for d in dropdown_data:
            setattr(self,f"phraseDropdown{d}",QtWidgets.QComboBox())
            getattr(self,f"phraseDropdown{d}").addItems(dropdown_data[d])
            layout.addWidget(getattr(self,f"phraseDropdown{d}"))
        self.scrollArea.setWidget(content_widget)
        self.scrollArea.setWidgetResizable(True)
        self.chosen={}
        self.syncDropdownsWithOtherDropdowns()
################################################################################################################################################################################################################

def main():
    app = QtWidgets.QApplication([])
    substituteSentences = ssGUI()
    substituteSentences.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()