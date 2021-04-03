from dropDownManager import dropDownModel as dropdown
from tableDataManager import tableModeling
from settings_flashcards import Ui_Dialog
from new_flashcards_again import Ui_MainWindow
from deckHandler import deckHandler
from flow_layout import FlowLayout
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import * 
import loadDecks
import tableviewLogic
import shutil, sys, csv, os, json


class executeGUI():
	def __init__(self):
		app = QApplication(sys.argv)
		self.mainW = QMainWindow()
		self.ui = Ui_MainWindow()
		self.functions = deckHandler()
		self.dropdown = dropdown()
		self.grid = FlowLayout()
		self.ui.setupUi(self.mainW)		
		self.setupSlots(app)
		self.retrievePrefs(app)
		self.mainW.show()
		sys.exit(app.exec_())
		
	def setupSlots(self, app):
		self.selectionDisplay()
		self.createInit([])
		self.ui.tabWidget.setCurrentIndex(0)
		self.ui.tabWidget.setTabVisible(1, False)
		self.ui.pushButton.clicked.connect(self.practiceInProgress)
		self.ui.pushButton.setDisabled(True)
		app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
		self.ui.lineEdit.returnPressed.connect(self.handleInput)
		
		self.ui.toolButton_2.clicked.connect(lambda: self.settings(app))
		self.ui.importButton.clicked.connect(lambda: tableviewLogic.importing(self.ui.tab_3, self.ui, self.deleteSelection, self.selectionDisplay))
		self.ui.pushButton_3.clicked.connect(self.creationStarted)
		self.ui.revPractice.stateChanged.connect(lambda state: self.practiceFlags("reverse", state))
		self.ui.timedPractice.stateChanged.connect(lambda state: self.practiceFlags("timed", state))
		
		self.dropdown.loadOptions(self.ui) # initializes a list in the drop-down menu
		self.ui.comboBox.setMaxVisibleItems(5)
		self.ui.comboBox.currentIndexChanged.connect(lambda: self.loadSelection(self.ui.comboBox.currentText()))
		
		self.ui.gridLayout_3.addLayout(self.grid, 0, 0)
		
		self.ui.buttonDel.clicked.connect(lambda: self.confirmDialog(self.deleteCollection, "delete this collection"))
		self.ui.buttonAdd.clicked.connect(self.addToCollection)
		self.ui.buttonRem.clicked.connect(self.removeFromCollection)
		self.ui.buttonDel.setIcon(QApplication.instance().style().standardIcon(QStyle.SP_TrashIcon))
		self.ui.buttonAdd.setIcon(QApplication.instance().style().standardIcon(QStyle.SP_DirOpenIcon))
		self.ui.buttonRem.setIcon(QApplication.instance().style().standardIcon(QStyle.SP_DirClosedIcon))
		self.ui.deckDelBtn.hide()
		
	def selectionDisplay(self): # dynamically initializes deck choies 
		self.ui.groupBox.hide()
		self.f = []
		try:
			if os.listdir("Decks") == []:
				self.ui.label.setText("Try adding some decks first!") # in case there are no decks added
			else:
				for i in os.listdir("Decks"):
					self.f.append(str(i))
				for i in self.f:
					loadDecks.createOption(i, self.ui, self.grid, self.checked)
		except FileNotFoundError: # in case there is no preexisiting Decks subdirectory
			os.makedirs("Decks")
			self.selectionDisplay()

	def checked(self, state, name): # detects origin and passes the name to the operative module
		if state == True:
			self.functions.decksToPractice.append(str(name))
		elif state == False:
			if name in self.functions.decksToPractice:
				self.functions.decksToPractice.remove(str(name))
		if self.functions.decksToPractice == []:
			self.ui.pushButton.setDisabled(True)
		else:
			self.ui.pushButton.setDisabled(False)
			
	def uncheckAll(self):
		for i in range(0, self.grid.count()):
			item = self.grid.itemAt(i).widget()
			try:
				item.setChecked(False)
			except AttributeError:
				pass
	
	
	# HANDLES PRACTICE
	
	def practiceFlags(self, name, state):
		if name == "reverse":
			if state == 0:
				self.functions.reverseTrue = False
			elif state == 2:
				self.functions.reverseTrue = True
		elif name == "timed":
			if state == 0:
				self.functions.timed = False
			elif state == 2:
				self.functions.timed = True
		
	def practiceInProgress(self): # starts off a deck cycle, passes on to both handlePractice and handleInput
		self.functions.practice(self.ui, self.handleTimeout) 
		if len(self.functions.questions) == 0:
			self.error("This is an empty deck!")
		else:
			try:
				self.ui.tabWidget.setTabVisible(1, True)
				self.ui.tabWidget.setCurrentIndex(1)
				self.ui.tabWidget.setTabVisible(0, False)
				self.ui.tabWidget.setTabVisible(2, False)
				self.ui.numRight.setText("Right: ")
				self.ui.numWrong.setText("Wrong: ")
				self.ui.timerDisplay.display("--:--")
				self.uncheckAll()
				self.functions.inPractice = True
				self.handlePractice(self.functions.i)
				self.ui.revPractice.setChecked(False)
				self.ui.timedPractice.setChecked(False)
			except IndexError:	
				self.error("There is an issue with this deck. Try editing it in the \"Create\" tab.")
				self.functions = deckHandler()
			except UnicodeDecodeError:
				self.error("There is an issue with this deck. Try editing it in the \"Create\" tab.")
				self.functions = deckHandler()

	def handlePractice(self, i): # fetches the answer from the functional module, prints to the textBrowser
		try:
			self.functions.currentQuestion = self.functions.questions[i]
			self.functions.currentAnswer = self.functions.answers[i]
			self.ui.textBrowser.append(self.functions.currentQuestion)
			self.ui.textBrowser.verticalScrollBar().setValue(self.ui.textBrowser.verticalScrollBar().maximum())
		except IndexError:
			self.percentageRight = round(self.functions.numright/len(self.functions.questions) * 100, 2)
			if self.percentageRight < 70:
				self.message = "You should practice this deck more."
			elif self.percentageRight < 80:
				self.message = "Fair job."
			elif self.percentageRight < 90:
				self.message = "Kudos!"
			elif self.percentageRight < 100:
				self.message = "Terrific Job!"
			else:
				self.message = "Perfect!"
			self.ui.textBrowser.append(f"You finished with {str(self.functions.numright)} ({self.percentageRight}%) cards correct. {self.message}")
			self.ui.textBrowser.append("Hit enter to quit.")
			self.functions.timer.stop()
			self.functions.inPractice = False

	def handleInput(self): # checks input, responds accordingly
		if self.functions.inPractice: 
			inputO = self.ui.lineEdit.text().strip()
			if inputO.lower() == self.functions.currentAnswer:
				self.ui.textBrowser.append(inputO)
				self.ui.textBrowser.append("You are correct!")
				self.ui.textBrowser.append("")
				self.ui.textBrowser.append("=====================================")
				self.ui.textBrowser.append("")
				self.functions.numright += 1
				self.ui.numRight.setText(f"Right: {self.functions.numright}")
			elif inputO.lower() != self.functions.currentAnswer:
				self.ui.textBrowser.append(inputO)
				self.ui.textBrowser.append(f"Incorrect! The answer is actually '{str(self.functions.currentAnswer)}'")
				self.ui.textBrowser.append("")
				self.ui.textBrowser.append("=====================================")
				self.ui.textBrowser.append("")
				self.ui.numWrong.setText(f"Wrong: {self.functions.i - self.functions.numright + 1}")
			self.functions.i += 1
			self.ui.lineEdit.clear()
			self.handlePractice(self.functions.i)
		else:
			self.ui.tabWidget.setTabVisible(0, True)	
			self.ui.tabWidget.setTabVisible(2, True)		
			self.ui.tabWidget.setCurrentIndex(0)
			self.ui.textBrowser.clear()
			self.ui.tabWidget.setTabVisible(1, False)
			self.functions = deckHandler()
			
	def handleTimeout(self):
		self.ui.textBrowser.append("=====================================")
		self.ui.textBrowser.append(f"You timed out with {self.functions.i}/{len(self.functions.questions)} answered, and {self.functions.numright} correct.")
		self.ui.textBrowser.append("Hit enter to quit.")
		self.functions.inPractice = False

	
	# HANDLES TABLEVIEW on TAB 3
	
		
	def error(self, message): # easy to customize, will reuse throughout
		self.win = QMessageBox(self.ui.tab_3)
		self.win.setText(message) 
		self.win.setIcon(QMessageBox.Warning)
		self.win.setWindowTitle("Warning")
		self.win.exec_()
		
	def createInit(self, tableData): # initializes the create tab
		# initialization
		self.tableData = tableData	
		self.table = self.ui.tableView
		self.model = tableModeling(self.tableData)
		self.table.setModel(self.model)
		self.cornerButton = self.table.findChild(QAbstractButton)
		self.table.setCornerButtonEnabled(False)
		self.table.horizontalHeader().sectionPressed.disconnect()
		self.table.verticalHeader().sectionPressed.disconnect()
		tableviewLogic.addRow(self.tableData, self.model, self.ui)
		
		# signals & slots
		self.ui.addButton.clicked.connect(lambda: tableviewLogic.addRow(self.tableData, self.model, self.ui))
		self.ui.removeButton.clicked.connect(lambda: tableviewLogic.removeRow(self.tableData, self.model, self.ui))
		self.ui.createButton.clicked.connect(lambda: tableviewLogic.creation(self.tableData, self.model, self.ui, self.error, self.deleteSelection, self.selectionDisplay))
		self.ui.editButton.clicked.connect(lambda: tableviewLogic.loadToEdit(tableData, self.model, self.ui, self.dropdown, self.error))
		self.ui.pushButton_2.clicked.connect(lambda: self.cancelCreation(tableData, self.model))
		self.ui.inputName.setMaxLength(50)
		
		# self.cancelBtnShown(self.tableData)
		self.ui.practiceCancelBtn.clicked.connect(lambda: self.confirmDialog(self.cancelPractice, "cancel your practice"))
		self.ui.deckDelBtn.clicked.connect(lambda: self.confirmDialog(tableviewLogic.deleteDeck, "delete this deck", tableData, self.model))
		self.table.model().dataChanged.connect(lambda: print("Changed!"))
		
		# cosmetics
		self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
			
	def cancelBtnShown(self, tableData):
		if tableData == [["",""]]:
			self.ui.pushButton_2.setDisabled(True)
		else:
			self.ui.pushButton_2.setDisabled(False)
		
	
	# COSMETICS
	
	
	def settings(self, app): # handles the settings widget
		self.inherit = QDialog(self.mainW)
		self.window = Ui_Dialog()
		self.window.setupUi(self.inherit)
		if self.mainW.palette().color(QPalette.Background).name() == "#d3d3d3":
			self.window.radioButton_2.setChecked(True)
		elif self.mainW.palette().color(QPalette.Background).name() == "#191919":
			self.window.radioButton.setChecked(True)
		if self.ui.centralwidget.font().pointSize() == 10:
			self.window.radioButton_4.setChecked(True)
		elif self.ui.centralwidget.font().pointSize() == 8:
			self.window.radioButton_3.setChecked(True)
		self.window.radioButton.clicked.connect(lambda: self.darkmode(app))
		self.window.radioButton.clicked.connect(lambda: self.savePrefs(0, "darkmode"))
		self.window.radioButton_2.clicked.connect(lambda: self.lightmode(app))
		self.window.radioButton_2.clicked.connect(lambda: self.savePrefs(0, "lightmode"))
		self.window.radioButton_3.clicked.connect(self.tinytext)
		self.window.radioButton_3.clicked.connect(lambda: self.savePrefs(1, "tinytext"))
		self.window.radioButton_4.clicked.connect(self.normaltext)
		self.window.radioButton_4.clicked.connect(lambda: self.savePrefs(1, "normaltext"))
		self.inherit.show()
		
	def darkmode(self, app): # sets palette with dark values
		app.setStyle("Fusion")
		darkSettings = ("""{
		color: rgb(255, 255, 255);
		background-color: rgb(25, 25, 25);
		alternate-background-color: rgb(80, 80, 80);}
		QRadioButton::indicator {
		border: 1px solid rgb(255, 255, 255);
		border-radius: 7px}
		QRadioButton::indicator::checked {
		background-color: rgb(255, 255, 255)}
		QTabWidget * {
		background-color: rgb(53, 53, 53)}
		QTabWidget QScrollArea * {
		background-color: rgb(25, 25, 25)}
		QTabWidget QScrollArea QTableView {
		background-color: rgb(53, 53, 53);
		gridline-color: rgb(0, 0, 0)}
		QTabWidget QScrollArea QHeader {
		background-color: rgb(53, 53, 53)}
		QTabWidget QScrollArea QScrollBar {
		background-color: rgb(53, 53, 53)}
		QLineEdit {
		background-color: rgb(80, 80, 80)}
		""")
		app.setStyleSheet(f"* {darkSettings}")
		
	def lightmode(self, app): # sets palette with light values
		app.setStyle("Fusion")
		lightSettings = ("""{
		color: rgb(0, 0, 0);
		background-color: rgb(211, 211, 211);
		alternate-background-color: rgb(180, 180, 180);}
		QTabWidget * {
		background-color: rgb(255, 255, 255)}
		QTabWidget QScrollArea * {
		background-color: rgb(211, 211, 211)}
		QTabWidget QScrollArea QTableView {
		background-color: rgb(255, 255, 255);
		gridline-color: rgb(0, 0, 0)}
		QTabWidget QScrollArea QHeader {
		background-color: rgb(255, 255, 255)}
		QTabWidget QScrollArea QScrollBar {
		background-color: rgb(255, 255, 255)}
		QLineEdit {
		background-color: rgb(180, 180, 180)}
		""")
		app.setStyleSheet(f"* {lightSettings}")
		
	def tinytext(self): # sets font size 8
		self.mainW.setStyleSheet("* {font-size: 8pt}")
		
	def normaltext(self): # sets font size 11
		self.mainW.setStyleSheet("* {font-size: 10pt}")
			
	
	# CANCELING
	
	
	def cancelPractice(self): # cancels a practicing session, resets deckHandler instance
		self.ui.tabWidget.setTabVisible(0, True)	
		self.ui.tabWidget.setTabVisible(2, True)		
		self.ui.tabWidget.setCurrentIndex(0)
		self.ui.textBrowser.clear()
		self.functions.timer.stop()
		self.ui.tabWidget.setTabVisible(1, False)
		self.functions = deckHandler()
		
	def cancelCreation(self, tableData, model): # clears the Q/A model
		confirmWindow = QMessageBox(self.mainW)
		confirmWindow.setText("Are you sure you want to cancel?")
		confirmWindow.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
		confirmWindow.setIcon(QMessageBox.Warning)
		confirmWindow.setWindowTitle("Confirm")
		confirmWindow.setDefaultButton(QMessageBox.No)
		proceed = confirmWindow.exec_()
		if proceed == QMessageBox.Yes:
			self.ui.inputName.clear()
			self.ui.inputName.setReadOnly(False)
			self.ui.deckDelBtn.hide()
			self.ui.createButton.setText("Create")
			tableData.clear()
			self.ui.tableView.setShowGrid(False)
			model.verticalHeader = False
			tableData.append(["", ""])
			model.layoutChanged.emit()
		
	def confirmDialog(self, method, action, tableData=0, model=0):
		confirmWindow = QMessageBox(self.mainW)
		confirmWindow.setText(f"Are you sure you want to {action}?")
		confirmWindow.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
		confirmWindow.setIcon(QMessageBox.Warning)
		confirmWindow.setWindowTitle("Confirm")
		confirmWindow.setDefaultButton(QMessageBox.No)
		proceed = confirmWindow.exec_()
		if tableData != 0 and proceed == QMessageBox.Yes:
			tableviewLogic.deleteDeck(tableData, model, self.ui)
		elif proceed == QMessageBox.Yes:
			method()
		
	
	# USER PREFERENCES
	
	
	def retrievePrefs(self, app): # loads previous settings upon window load
		if os.path.isfile("preferences.csv"):
			values = []
			with open("preferences.csv", "r", newline="", encoding="utf-8") as preferences:
				values.append([row for row in csv.reader(preferences, delimiter=",")][0])
			preferences.close()
			if values[0][0] == "lightmode":
				self.lightmode(app)
			elif values[0][0] == "darkmode":
				self.darkmode(app)
			if values[0][1] == "tinytext":
				self.tinytext()
			elif values[0][1] == "normaltext":
				self.normaltext()
		else:
			with open("preferences.csv", "w+", newline="", encoding="utf-8") as preferences:
				x = csv.writer(preferences)
				x.writerow(["lightmode", "tinytext"])
			preferences.close()
			self.lightmode(app)
			self.tinytext()
		
	def savePrefs(self, mode, text): # adds the new values to the preferences reference file
		values = []
		with open("preferences.csv", "r", newline="", encoding="utf-8") as preferences:
			values.append([row for row in csv.reader(preferences, delimiter=",")][0])
		preferences.close()
		if mode == 0:
			if text == "darkmode":
				values[0][0] = "darkmode"
			elif text == "lightmode":
				values[0][0] = "lightmode"
		elif mode == 1:
			if text == "tinytext":
				values[0][1] = "tinytext"
			elif text == "normaltext":
				values[0][1] = "normaltext"
		with open("preferences.csv", "w+", newline="", encoding="utf-8") as preferences:
			preferences.truncate()
			x = csv.writer(preferences)
			x.writerow(values[0])
		preferences.close()
			
	
	# HANDLES COLLECTIONS FEATURE
	# - note: I first tried to extensively modularize this code, but that 
	#         resulted in spaghetti code (with messy parameter passing) so I kept most of it in this module. 
	
	
	def deleteSelection(self): # deletes all the checkboxes in the selection window
		for i in reversed(range(self.grid.count())):
			self.grid.itemAt(i).widget().close()
			self.grid.takeAt(i)

	def loadSelection(self, colName): # repopulates checkboxes
		self.uncheckAll()
		self.deleteSelection()
		self.ui.groupBox.hide()
		if self.dropdown.creationInProgress == True:
			pass
		elif self.ui.comboBox.currentIndex() == -1:
			pass
		elif colName == "All Collections":
			self.selectionDisplay()
		else:
			with open("collections.txt", "r", encoding="utf-8") as collections:
				data = json.load(collections)
			collections.close()
			
			for i in data[colName]:
				loadDecks.createOption(i, self.ui, self.grid, self.checked)
			self.ui.groupBox.show()
			
	def deleteCollection(self): # deletes a collection (model and view) 
		self.uncheckAll()
		self.deleteSelection()
		with open("collections.txt", "r+", encoding="utf-8") as collections:
			data = json.load(collections)
			data.pop(self.ui.comboBox.currentText())
			collections.seek(0)
			collections.truncate()
			json.dump(data, collections)
		collections.close()
		self.dropdown.model.clear()
		self.dropdown.loadOptions(self.ui)
		self.ui.comboBox.setCurrentIndex(0)
		
	def addToCollection(self): # adds to a collection (model and view)
		index = self.ui.comboBox.currentText()
		try:
			self.filedir = QFileDialog(self.ui.tab_3)
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
				if realName not in data[self.ui.comboBox.currentText()]:
					data[self.ui.comboBox.currentText()].append(realName)
					collections.seek(0)
					collections.truncate()
					json.dump(data, collections)
			collections.close()
			self.loadSelection(self.ui.comboBox.currentText())
		except IndexError:
			pass	
		
	def dirCheck(self, dlg): # makes the dialog window non-traversable
		dlg.setDirectory("Decks/")		
		
	def removeFromCollection(self): # removes from a collecion (model and view)
		index = self.ui.comboBox.currentText()
		try:
			with open("collections.txt", "r", encoding="utf-8") as collections:
				data = json.load(collections)
			collections.close()
			self.filedir = QFileDialog(self.ui.tab_3)
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
				if realName in data[index]:
					data[index].remove(realName)
					collections.seek(0)
					collections.truncate()
					json.dump(data, collections)
			collections.close()
			
			self.loadSelection(index) 
		except IndexError:
			pass
		
	def creationStarted(self): # starts off the collection process, sends to creationFinished
		self.dropdown.creationInProgress = True
		self.ui.comboBox.setModel(QStandardItemModel(0, 1))
		a = QLineEdit()
		self.ui.comboBox.setLineEdit(a)
		a.setReadOnly(False)
		a.setFocus()
		a.returnPressed.connect(lambda: self.creationFinished(a))
		self.ui.comboBox.setCurrentIndex(0)
		
	def creationFinished(self, a): # handles adding the new collection to the json file
		realName = a.text()
		newName = a.text().strip().lower()
		if newName == "" or newName == "all collections" or newName == "create collections":
			a.setReadOnly(True)
			self.ui.comboBox.setModel(self.dropdown.model)
			self.dropdown.creationInProgress = False
			self.loadSelection("All Collections")
		else:
			with open("collections.txt", "r+", encoding="utf-8") as collections:
				data = json.load(collections)
				if a.text() not in data.keys():
					data[a.text()] = []
				collections.seek(0)
				collections.truncate()
				json.dump(data, collections)
			collections.close()
			
			self.dropdown.creationInProgress = False			
			a.setReadOnly(True)
			self.ui.comboBox.disconnect()
			self.ui.comboBox.setModel(self.dropdown.model)
			self.dropdown.loadOptions(self.ui)
			self.ui.comboBox.currentIndexChanged.connect(lambda: self.loadSelection(self.ui.comboBox.currentText()))
			x = list(data.keys()).index(realName)
			self.ui.comboBox.setCurrentIndex(x)
