import os
import json
from PyQt5 import QtGui
from PyQt5.QtWidgets import *


class handleCollections():
	def __init__(self):
		self.model = QtGui.QStandardItemModel(0, 1)
		self.flagForInput = True
		
	def loadOptions(self, ui): # creates a collections file to simulate subdirectories and sorting
		if not os.path.isfile("collections.txt"):
			with open("collections.txt", "w+", encoding="utf-8") as collections:
				x = {"All Collections": 0, "Create Collection": 0}
				json.dump(x, collections)
			collections.close()
			self.loadOptions(ui)
		else:
			with open("collections.txt", "r", encoding="utf-8") as collections:
				data = json.load(collections)
			collections.close()
			ui.comboBox.setModel(self.model)
			for i in data.keys():
				self.model.appendRow(QtGui.QStandardItem(i))
			self.model.layoutChanged.emit()
				
	def indexChanged(self, ui, selectionDisplay): # for Create Collection
		rowNum = self.model.rowCount()
		ui.comboBox.setModel(QtGui.QStandardItemModel(0, 1))
		a = QLineEdit()
		a.returnPressed.connect(lambda: self.addCollection(a, ui, selectionDisplay))		
		ui.comboBox.setLineEdit(a)
		a.setReadOnly(False)		
		ui.comboBox.setCurrentIndex(0)

	def addCollection(self, a, ui, selectionDisplay): # handle adding a collection w/comboBox and lineEdit
		a.disconnect()
		if a.text().strip() == "" or a.text().strip().lower() == "all collections" or a.text().strip().lower() == "create collection":
			a.setReadOnly(True)
			ui.comboBox.setModel(self.model)
		else:
			with open("collections.txt", "r+", encoding="utf-8") as f:
				data = json.load(f)
				if a.text() not in data.keys():
					data[a.text()] = []
				f.seek(0)
				f.truncate()
				json.dump(data, f)
			f.close()	
			a.setReadOnly(True)
			x = list(data.keys()).index(a.text())
			self.flagForInput = False
			self.model.clear()
			self.loadOptions(ui)
			self.flagForInput = True
			ui.comboBox.setCurrentIndex(x)
			for i in reversed(range(ui.gridLayout.count())): 
				ui.gridLayout.itemAt(i).widget().setParent(None)
			self.loadCollection(ui, selectionDisplay)
			
	def loadCollection(self, ui, selectionDisplay): # redraws checkbox grid
		with open("collections.txt", "r", encoding="utf-8") as collections:
			data = json.load(collections)
		collections.close()
		
		icon = (QApplication.instance().style().standardIcon(QStyle.SP_TrashIcon))
		buttonDel = QPushButton(icon, " Delete")
		buttonDel.clicked.connect(lambda: self.deleteCollection(ui))
		buttonDel.resize(90, 18)
		addIcon = (QApplication.instance().style().standardIcon(QStyle.SP_DirOpenIcon))
		removeIcon = (QApplication.instance().style().standardIcon(QStyle.SP_DirClosedIcon))
		buttonAdd = QPushButton(addIcon, " Add")
		buttonAdd.clicked.connect(lambda: self.addToCollection(ui))
		buttonAdd.resize(90, 18)
		buttonRemove = QPushButton(removeIcon, " Remove")
		buttonRemove.clicked.connect(lambda: self.removeFromCollection(ui))
		buttonRemove.resize(90, 18)
		
		try:
			children = [i for i in data[ui.comboBox.currentText()]]
			selectionDisplay(children)
			ui.gridLayout.addWidget(buttonDel, ui.gridLayout.count()//5, ui.gridLayout.count()%5, 1, 1)
			ui.gridLayout.addWidget(buttonAdd, ui.gridLayout.count()//5, ui.gridLayout.count()%5, 1, 1)
			ui.gridLayout.addWidget(buttonRemove, ui.gridLayout.count()//5, ui.gridLayout.count()%5, 1, 1)
		except:
			pass
		
	def deleteCollection(self, ui): # updates model & view for collections
		for i in range(0, ui.gridLayout.count()):
			checkBox = ui.gridLayout.itemAt(i).widget()
			try:
				checkBox.setCheckState(False)
			except:
				pass
		
		with open("collections.txt", "r+", encoding="utf-8") as collections:
			data = json.load(collections)
			data.pop(ui.comboBox.currentText())
			collections.seek(0)
			collections.truncate()
			json.dump(data, collections)
		collections.close()
		self.model.clear()
		self.loadOptions(ui)
		ui.comboBox.setCurrentIndex(0)
			
	def addToCollection(self, ui): # opens a dialog box to import decks
		index = ui.comboBox.currentText()
		try:
			self.filedir = QFileDialog(ui.tab_3)
			self.filedir.setOption(self.filedir.DontUseNativeDialog, True)
			self.filedir.setFileMode(QFileDialog.ExistingFile)
			self.filedir.setNameFilter("CSV files (*.csv)")
			self.filedir.setDirectory("Decks/")
			self.filedir.directoryEntered.connect(lambda: self.dirCheck(self.filedir))
			impFile = ""
			if self.filedir.exec_():
				impFile = self.filedir.selectedFiles()
			realName = os.path.split(impFile[0])[1]
			with open("collections.txt", "r+", encoding="utf-8") as collections:
				data = json.load(collections)
				if realName not in data[ui.comboBox.currentText()]:
					data[ui.comboBox.currentText()].append(realName)
					collections.seek(0)
					collections.truncate()
					json.dump(data, collections)
			collections.close()
			ui.comboBox.setCurrentIndex(0)
			ui.comboBox.setCurrentIndex(list(data.keys()).index(index))
		except IndexError:
			pass
		
	def removeFromCollection(self, ui): # reverse engineers addToCollection
		index = ui.comboBox.currentText()
		try:
			with open("collections.txt", "r", encoding="utf-8") as collections:
				info = json.load(collections)
			collections.close()
			optionsOpen = "".join([str(i + " ") for i in info[ui.comboBox.currentText()]])
			if optionsOpen == "":
				optionsOpen = "None.txt"
			self.filedir = QFileDialog(ui.tab_3)
			self.filedir.setOption(self.filedir.DontUseNativeDialog, True)
			self.filedir.setFileMode(QFileDialog.ExistingFile)
			self.filedir.setNameFilter(str("CSV files (" + optionsOpen + ")"))
			self.filedir.setDirectory("Decks/")
			self.filedir.directoryEntered.connect(lambda: self.dirCheck(self.filedir))
			impFile = ""
			
			if self.filedir.exec_():
				impFile = self.filedir.selectedFiles()
			realName = os.path.split(impFile[0])[1]
			
			with open("collections.txt", "r+", encoding="utf-8") as collections:
				data = json.load(collections)
				if realName in data[ui.comboBox.currentText()]:
					data[ui.comboBox.currentText()].remove(realName)
					collections.seek(0)
					collections.truncate()
					json.dump(data, collections)
			collections.close()
			
			if data[ui.comboBox.currentText()] == []:
				self.deleteCollection(ui)
			else:
				for i in range(0, ui.gridLayout.count()):
					checkBox = ui.gridLayout.itemAt(i).widget()
					try:
						checkBox.setCheckState(False)
					except:
						pass
				ui.comboBox.setCurrentIndex(0)
				ui.comboBox.setCurrentIndex(list(data.keys()).index(index))
				
		except IndexError:
			pass
		
	def dirCheck(self, dlg): # makes the dialog window non-traversable
		dlg.setDirectory("Decks/")	
