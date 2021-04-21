from PyQt6 import QtGui
from PyQt6.QtWidgets import *
import os
import json

class dropDownModel():
	def __init__(self):
		self.model = QtGui.QStandardItemModel(0, 1)
		self.creationInProgress = False
		
	def loadOptions(self, ui): # creates a collections file to simulate subdirectories and sorting
		if not os.path.isfile("collections.txt"):
			with open("collections.txt", "w+", encoding="utf-8") as collections:
				x = {"All Collections": 0}
				json.dump(x, collections)
			collections.close()
			self.loadOptions(ui)
		else:
			self.model.clear()
			with open("collections.txt", "r", encoding="utf-8") as collections:
				data = json.load(collections)
			collections.close()
			for i in data.keys():
				self.model.appendRow(QtGui.QStandardItem(i))
			ui.comboBox.setModel(self.model)			
			self.model.layoutChanged.emit()
