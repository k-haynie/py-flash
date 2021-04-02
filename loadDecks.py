from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
					
def createOption(i, ui, grid, responseHandler):
	ui.newCheckBox = QPushButton()
	ui.newCheckBox.setCheckable(True)
	ui.newCheckBox.setStyleSheet("""
		QPushButton {
		border-image: url("assets/decks.png");
		color: rgb(0,0,0);}
		QPushButton:checked {
		border-image: url("assets/decks_selected.png");}
		""")
	originalName = (str(i)[::-1].replace("vsc.", "", 1))[::-1] # for a deck named .csv.csv 
	spacedName = originalName.split(" ")
	realName = produceName(spacedName, ui)

	ui.newCheckBox.setText(realName)
	ui.newCheckBox.setMinimumSize(100, 133)
	ui.newCheckBox.setMaximumSize(100, 133)
	ui.newCheckBox.toggled.connect(lambda state, name=str(i): responseHandler(state, name))
	grid.addWidget(ui.newCheckBox)

	
def produceName(listOfWords, ui):
	data = listOfWords
	fontRef = ui.centralwidget.font()
	fm = QFontMetrics(fontRef)
	words  = []
	tempWords = []
	while len(data) > 0:
		if fm.horizontalAdvance(data[0]) < 60:
			if len(data) > 2 and fm.horizontalAdvance(data[0] + data[1]) < 60:
				words.append(data[0] + data[1] + "\n")
				data.pop(0)
				data.pop(1)
			else:
				words.append(data[0] + "\n")
				data.pop(0)
		else:
			x = [i for i in data[0]]
			assembledWord = ""
			while len(x) > 0:
				if fm.horizontalAdvance(assembledWord + "-" + "\n" + x[0]) > 60:
					words.append(assembledWord + "-" + "\n")
					assembledWord = ""
					data.pop(0)
					data.insert(0, "".join([i for i in x]))
					x.clear()
				else:
					assembledWord += x[0]
					x.pop(0)
	if len(words) > 5:
		return "".join(i for i in words[0:5]) + "..."
	else:
		return "".join(i for i in words)
					 
