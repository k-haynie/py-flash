from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import os
					
def createOption(i, ui, grid, responseHandler): # creates a deck image for each deck
	if os.path.exists(f"Decks/{i}"):
		ui.newCheckBox = QPushButton()
		ui.newCheckBox.setCheckable(True)
		fileSize = os.stat(f"Decks/{i}").st_size
		if fileSize > 0:
			ui.newCheckBox.setStyleSheet("""
				QPushButton {
				border-image: url("assets/decks.png");
				color: rgb(0,0,0);}
				QPushButton:checked {
				border-image: url("assets/decks_selected.png");}
				""")
		else:
			ui.newCheckBox.setStyleSheet("""
				QPushButton {
				border-image: url("assets/decks_empty.png");
				color: rgb(255,255,255);}
				""")
			ui.newCheckBox.setEnabled(False)
		originalName = (str(i)[::-1].replace("vsc.", "", 1))[::-1] # for a deck named .csv.csv 
		spacedName = originalName.split(" ")
		realName = produceName(spacedName, ui)

		ui.newCheckBox.setText(realName)
		ui.newCheckBox.setMinimumSize(100, 133)
		ui.newCheckBox.setMaximumSize(100, 133)
		ui.newCheckBox.toggled.connect(lambda state, name=str(i): responseHandler(state, name))
		grid.addWidget(ui.newCheckBox)

def produceName(listOfWords, ui): # splices names into lines according to display width
	data = listOfWords
	fontRef = ui.tabWidget.font()
	fm = QFontMetrics(fontRef)
	words  = []
	while len(data) > 0:
		if fm.horizontalAdvance(data[0]) < 60:
			words.append(data[0])
			data.pop(0)
		else:
			x = [i for i in data[0]]
			assembledWord = ""
			while len(x) > 0:
				if fm.horizontalAdvance(assembledWord + "-"+ x[0]) > 60:
					words.append(assembledWord + "-")
					assembledWord = ""
					data.pop(0)
					data.insert(0, "".join([i for i in x]))
					x.clear()
				else:
					assembledWord += x[0]
					x.pop(0)
	name = []
	assembledLine = ""
	while len(words) > 0:
		if fm.horizontalAdvance(assembledLine + " " + words[0]) > 63 and len(assembledLine) > 0:
			name.append(assembledLine + "\n")
			assembledLine = ""
		else:
			assembledLine += words[0]
			words.pop(0)
			if len(assembledLine) > 0 and len(words) > 0:
				assembledLine += " "
			if len(words) == 0:
				name.append(assembledLine)
	if len(name) > 5:
		return "".join(i for i in name[0:5]) + "..."
	else:
		return "".join(i for i in name)
					 
