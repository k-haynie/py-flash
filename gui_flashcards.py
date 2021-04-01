from dropDownManager import dropDownModel as dropdown
from tableDataManager import tableModeling
from settings_flashcards import Ui_Dialog
from new_flashcards import Ui_MainWindow
from deckHandler import deckHandler
from flow_layout import FlowLayout
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import * 
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
		self.ui.pushButton.clicked.connect(lambda: self.practiceInProgress(False))
		self.ui.pushButton_3.clicked.connect(lambda: self.practiceInProgress(True))
		self.ui.pushButton.setDisabled(True)
		self.ui.pushButton_3.setDisabled(True)
		app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
		
		self.ui.lineEdit.returnPressed.connect(self.handleInput)
		self.ui.importButton.clicked.connect(self.importing)
		self.ui.settingsButton.clicked.connect(lambda: self.settings(app))
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
		self.ui.buttonDel.hide()
		self.ui.buttonAdd.hide()
		self.ui.buttonRem.hide()
		self.f = []
		try:
			if os.listdir("Decks") == []:
				self.ui.label.setText("Try adding some decks first!") # in case there are no decks added
			else:
				for i in os.listdir("Decks"):
					self.f.append(str(i))
				for i in self.f:
					self.ui.newCheckBox = QPushButton()
					self.ui.newCheckBox.setCheckable(True)
					self.ui.newCheckBox.setStyleSheet("""
						QPushButton {
						border-image: url("assets/decks.png");
						color: rgb(0,0,0);}
						QPushButton:checked {
						border-image: url("assets/decks_selected.png");}
						""")
					originalName = (str(i)[::-1].replace("vsc.", "", 1))[::-1] # for a deck named .csv.csv 
					spacedName = originalName.split(" ")
					
					if self.btnWordWrap(spacedName):
						words = []
						for i in spacedName:
							if len(i) > 10:
								splices = [str(i[x:x+10]) + "-" if len(i) - 10 >= x else i[x:x+10] for x in range(0, len(i), 10)]
								for i in splices:
									words.append(i)
							else:
								words.append(i)
						if len(words) > 5:
							standIn = "".join(str(i) + "\n" for i in words[0:5])
							realName = standIn + "..."
						else:
							realName = "".join(str(i) + "\n" for i in words)
					else:
						realName = "".join(str(i) + "\n" for i in spacedName)
					self.ui.newCheckBox.setText(realName)
					self.ui.newCheckBox.setMinimumSize(100, 133)
					self.ui.newCheckBox.setMaximumSize(100, 133)
					self.ui.newCheckBox.toggled.connect(lambda state, name=str(i): self.checked(state, name))
					self.grid.addWidget(self.ui.newCheckBox)
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
			self.ui.pushButton_3.setDisabled(True)
		else:
			self.ui.pushButton.setDisabled(False)
			self.ui.pushButton_3.setDisabled(False)
			
	def uncheckAll(self):
		for i in range(0, self.grid.count()):
			item = self.grid.itemAt(i).widget()
			try:
				item.setChecked(False)
			except AttributeError:
				pass
				
	def btnWordWrap(self, listOfWords):
		for i in listOfWords:
			if len(i) > 10:
				return True
		return False
	
	
	# HANDLES PRACTICE
	
	
	def practiceInProgress(self, reverseTrue): # starts off a deck cycle, passes on to both handlePractice and handleInput
		try:
			self.functions.practice(reverseTrue) 
			self.ui.tabWidget.setTabVisible(1, True)
			self.ui.tabWidget.setCurrentIndex(1)
			self.ui.tabWidget.setTabVisible(0, False)
			self.ui.tabWidget.setTabVisible(2, False)
			self.uncheckAll()
			self.functions.inPractice = True
			self.handlePractice(self.functions.i)	
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
			elif inputO.lower() != self.functions.currentAnswer:
				self.ui.textBrowser.append(inputO)
				self.ui.textBrowser.append(f"Incorrect! The answer is actually '{str(self.functions.currentAnswer)}'")
				self.ui.textBrowser.append("")
				self.ui.textBrowser.append("=====================================")
				self.ui.textBrowser.append("")
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

	
	# HANDLES TABLEVIEW on TAB 3
	
	
	def importing(self): # handles importing a csv file to the app's decks file - MIGHT BE AN ISSUE w/DELETING DECKS
		try:
			self.filedir = QFileDialog(self.ui.tab_3)
			self.filedir.setOption(self.filedir.DontUseNativeDialog, True)
			self.filedir.setFileMode(QFileDialog.ExistingFile)
			self.filedir.setNameFilter("CSV files (*.csv)")
			self.filedir.setDirectory("C:")
			impFile = ""
			if self.filedir.exec_():
				impFile = self.filedir.selectedFiles()
			fromDir = impFile[0] 
			name = os.path.split(fromDir)[1]			
			toDir = os.path.abspath("Decks/")
			if name in os.listdir(toDir):
				self.error("This file already exists!")
			else:
				shutil.copy(fromDir, toDir)			
				self.deleteSelection()
				self.selectionDisplay()
				self.ui.tabWidget.setCurrentIndex(0)
				self.ui.comboBox.setCurrentIndex(0)
		except IndexError: # thrown when the window is prematurely closed
			pass 
		
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
		self.addRow(self.tableData, self.model)
		# signals & slots
		self.ui.addButton.clicked.connect(lambda: self.addRow(self.tableData, self.model))
		self.ui.removeButton.clicked.connect(lambda: self.removeRow(self.tableData, self.model))
		self.ui.createButton.clicked.connect(lambda: self.creation(self.tableData, self.model))
		self.ui.editButton.clicked.connect(lambda: self.loadToEdit(tableData, self.model))
		self.ui.pushButton_2.clicked.connect(lambda: self.cancelCreation(tableData, self.model))
		# self.cancelBtnShown(self.tableData)
		self.ui.practiceCancelBtn.clicked.connect(lambda: self.confirmDialog(self.cancelPractice, "cancel your practice"))
		self.ui.deckDelBtn.clicked.connect(lambda: self.confirmDialog(self.deleteDeck, "delete this deck", tableData, self.model))
		# self.table.model().dataChanged.connect(lambda: print("Changed!"))
		
		# cosmetics
		self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		
	def creation(self, tableData, model): # handles the click of createButton
		inputName = self.ui.inputName.text().strip()
		deckname = "Decks/" + inputName + ".csv"
		if not self.checkForEmpty(tableData):
			pass
		else:		
			
			if self.ui.createButton.text() == "Save":
				self.fileWrite(deckname, tableData)
				self.ui.createButton.setText("Create")
				tableData.clear()
				self.ui.inputName.clear()
				tableData.append(["", ""])
				self.ui.tableView.setShowGrid(False)
				model.verticalHeader = False
				model.layoutChanged.emit()
			else:
				if inputName == "":
					self.error("You need to name your deck!")
				elif inputName + ".csv" in os.listdir("Decks"):
					self.error("This deck already exists!")
				else:
					self.fileWrite(deckname, tableData)
					tableData.clear()
					tableData.append(["",""])
					self.ui.tableView.setShowGrid(False)
					model.verticaHeader = False
					self.ui.inputName.clear()
					model.layoutChanged.emit()
					self.deleteSelection()
					self.selectionDisplay()
					self.ui.tabWidget.setCurrentIndex(0)
					self.ui.comboBox.setCurrentIndex(0)
			self.ui.inputName.setReadOnly(False)
			self.ui.deckDelBtn.hide()
			
	def fileWrite(self, deckname, tabledata): # actually writes the files edited/produced in the interface
		try:
			with open(deckname, "w+", newline="", encoding="utf-8") as f:
				f.truncate()
				filewriter = csv.writer(f)
				
				for i in tabledata:
					testForEmpty = []
					for j in i:
						if j.strip() != "":
							testForEmpty.append(j)
					if testForEmpty != []:
						filewriter.writerow(i)
			f.close()		
		except PermissionError:
			os.chmod(deckname, stat.S_IWRITE)
			self.fileWrite(deckname, tabledata)
		
	def removeRow(self, tableData, model): # removes a row in the Create interface
		if len(tableData) == 1:
			tableData.pop()
			tableData.append(["",""])
			self.ui.tableView.setShowGrid(False)
			model.verticalHeader = False
			model.layoutChanged.emit()
		else:
			self.ref = self.ui.tableView.selectionModel().currentIndex().row()
			try:
				tableData.pop(self.ref)
			except:
				pass
			self.ui.tableView.selectRow(len(tableData)-1)
			self.ui.scrollArea_2.ensureWidgetVisible(self.ui.tableView.selectRow(self.ref-1))
			model.layoutChanged.emit()
		
	def addRow(self, tableData, model): # adds a row in the Create interface
		self.ref = self.ui.tableView.selectionModel().currentIndex().row()+1
		self.after = []
		if len(tableData) == 0:
			tableData.append(["",""])
			model.verticalHeader = False
			self.ui.tableView.setShowGrid(False)
		elif len(tableData) == 1 and not self.model.verticalHeader:
			self.model.verticalHeader = True
			self.ui.tableView.setShowGrid(True)
		elif self.ref == len(tableData):
			tableData.append(["", ""])
		else:
			for i in range(self.ref, len(tableData)):
				x = tableData.pop()
				self.after.append(x)
			tableData.append(["",""])
			
			for i in range(len(self.after)):
				x = self.after.pop()
				tableData.append(x)
				self.ui.tableView.selectRow(self.ref)
		self.ui.scrollArea_2.ensureWidgetVisible(self.ui.tableView.selectRow(self.ref-1))
		model.layoutChanged.emit()
		
	def loadToEdit(self, tableData, model): # creates and returns lists of the data from a selected file
		try:
			self.filedir = QFileDialog(self.ui.tab_3)
			self.filedir.setOption(self.filedir.DontUseNativeDialog, True)
			self.filedir.setFileMode(QFileDialog.ExistingFile)
			self.filedir.setNameFilter("CSV files (*.csv)")
			self.filedir.setDirectory("Decks/")
			self.filedir.directoryEntered.connect(lambda: self.dropdown.dirCheck(self.filedir))
			impFile = ""
			if self.filedir.exec_():
				impFile = self.filedir.selectedFiles()
			realName = os.path.split(impFile[0])[1].split(".csv")[0]
			subName = "Decks/" + realName + ".csv"

			self.ui.createButton.setText("Save")
			model.verticalHeader = True
			self.ui.tableView.setShowGrid(True)
			tableData.clear()
			reformat = []
			newLine = []
			
			with open(subName, "r", newline="", encoding="utf-8") as f:
				fileReader = csv.reader(f, delimiter=",")
				for line in fileReader:
					reformat.append(line)
			f.close()
			for i in reformat: # copying, filtering, and formatting the read-in data
				for j in i:
					if j != "":
						if "," in j: # splits csv data into an app-readable format
							newLine.append(j.split(","))
						elif "\t" in j: # splits tsv data into an app-readable format
							newLine.append(j.split("\t"))
			if newLine == [] and reformat == []:
				tableData.append(["",""])
				model.verticalHeader = False
				self.ui.tableView.setShowGrid(False)
			elif len(newLine) != len(reformat):
				for i in reformat:
					tableData.append(i)
			else:
				for i in newLine:
					tableData.append(i)
					
			model.layoutChanged.emit()
			self.ui.inputName.setText(realName)
			self.ui.inputName.setReadOnly(True)	
			self.ui.deckDelBtn.show()			
		except FileNotFoundError: # thrown when the window is prematurely closed
			pass
		except UnicodeDecodeError:
			self.error("This file is formatted incorrectly.\nTry opening it in Notepad and checking its format.")
		except IndexError:
			pass
			
	def deleteDeck(self, tableData, model):
		name = self.ui.inputName.text().strip()
		os.remove(f"Decks/{name}.csv")
		self.ui.inputName.clear()
		self.ui.inputName.setReadOnly(False)
		self.ui.deckDelBtn.hide()
		self.ui.createButton.setText("Create")
		tableData.clear()
		
		tableData.append(["",""])
		self.ui.tableView.setShowGrid(False)
		model.verticalHeader = False
		model.layoutChanged.emit()
		
		with open("collections.txt", "r+", encoding="utf-8") as collections:
			data = json.load(collections)
			for i in data:
				try:
					if f"{name}.csv" in data[i]:
						data[i].remove(f"{name}.csv")
				except:
					pass
			collections.seek(0)
			collections.truncate()
			json.dump(data, collections)
		collections.close()
		self.ui.comboBox.setCurrentIndex(-1)
		self.ui.comboBox.setCurrentIndex(0)
		
	def checkForEmpty(self, tableData):
		rows = []
		for count,i in enumerate(tableData):
			if i[0].strip() == "" and i[1].strip() == "":
				pass
			elif i[0].strip() == "" or i[1].strip() == "":
				rows.append(count)
		if rows == []:
			return True
		else:
			if len(rows) == 1:
				row = ["Row", "has an empty value."]
			else:
				row = ["Rows", "have empty values."]
			nums = ''.join((str(i+1) + ", ") if rows.index(i) != (len(rows)-1) else str(i+1) for i in [i for i in rows])
			self.error(f"{row[0]} {nums} {row[1]}")
			return False
	
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
			self.deleteDeck(tableData, model)
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
		self.ui.buttonDel.hide()
		self.ui.buttonAdd.hide()
		self.ui.buttonRem.hide()
		if self.dropdown.creationInProgress == True:
			pass
		elif self.ui.comboBox.currentIndex() == -1:
			pass
		elif colName == "All Collections":
			self.selectionDisplay()
		elif colName == "Create Collection":
			self.creationStarted()
		else:
			with open("collections.txt", "r", encoding="utf-8") as collections:
				data = json.load(collections)
			collections.close()
			
			for i in data[colName]:
				self.ui.newCheckBox = QPushButton()
				self.ui.newCheckBox.setCheckable(True)
				self.ui.newCheckBox.setStyleSheet("""
					QPushButton {
					border-image: url("assets/decks.png");
					color: rgb(0,0,0);}
					QPushButton:checked {
					border-image: url("assets/decks_selected.png");}
					""")
				originalName = (str(i)[::-1].replace("vsc.", "", 1))[::-1]
				self.ui.newCheckBox.setText(originalName)
				self.ui.newCheckBox.setMinimumSize(75, 100)
				self.ui.newCheckBox.setMaximumSize(75, 100)
				self.ui.newCheckBox.toggled.connect(lambda state, name=str(i): self.checked(state, name))
				self.grid.addWidget(self.ui.newCheckBox)
		
			self.ui.buttonDel.show()
			self.ui.buttonAdd.show()
			self.ui.buttonRem.show()
			
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
