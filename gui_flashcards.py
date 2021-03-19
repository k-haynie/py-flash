from handleCollections import handleCollections
from tableDataManager import tableModeling
from settings_flashcards import Ui_Dialog
from at_flashcards import Ui_MainWindow
from deckHandler import deckHandler
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import * 
import shutil, sys, csv, os


class executeGUI():
	def __init__(self):
		app = QApplication(sys.argv)
		self.mainW = QMainWindow()
		self.ui = Ui_MainWindow()
		self.functions = deckHandler()
		self.dropdown = handleCollections()
		self.ui.setupUi(self.mainW)
		self.setupSlots(app)
		self.retrievePrefs(app)
		self.mainW.show()
		sys.exit(app.exec_())
		
	def setupSlots(self, app):
		self.selectionDisplay(os.listdir("Decks"))
		self.createInit([])
		self.ui.tabWidget.setCurrentIndex(0)
		self.ui.tabWidget.setTabVisible(1, False)
		self.ui.pushButton.clicked.connect(lambda: self.practiceInProgress(False))
		self.ui.pushButton_3.clicked.connect(lambda: self.practiceInProgress(True))
		self.ui.pushButton.setDisabled(True)
		self.ui.pushButton_3.setDisabled(True)
		self.ui.practiceCancelBtn.clicked.connect(self.cancelPractice)
		self.ui.lineEdit.returnPressed.connect(self.handleInput)
		self.ui.importButton.clicked.connect(self.importing)
		self.ui.settingsButton.clicked.connect(lambda: self.settings(app))
		self.dropdown.loadOptions(self.ui) # initializes a list in the drop-down menu
		self.ui.comboBox.setMaxVisibleItems(5)
		self.ui.comboBox.currentIndexChanged.connect(self.toggleColls)
		
	def selectionDisplay(self, f): # dynamically initializes deck choies
		self.f = f
		self.row = 0
		self.rowIndex = 0
		try:
			if os.listdir("Decks") == []:
				self.ui.label.setText("Try adding some decks first!") # in case there are no decks added
			else:
				for i in self.f:
					self.ui.newCheckBox = QCheckBox()
					if self.rowIndex == 5:
						self.row += 1
						self.rowIndex = 0
					self.ui.newCheckBox.setObjectName(str(i))
					self.ui.newCheckBox.setText(str(i))
					self.ui.newCheckBox.setMinimumSize(90, 18)
					self.ui.newCheckBox.setMaximumSize(90, 18)
					self.ui.newCheckBox.stateChanged.connect(lambda state, name=i: self.checked(state, name))
					self.ui.gridLayout.addWidget(self.ui.newCheckBox, self.row, self.rowIndex)
					self.rowIndex += 1
				self.ui.scrollAreaWidgetContents.setLayout(self.ui.gridLayout)
		except FileNotFoundError: # in case there is no preexisiting Decks subdirectory
			os.makedirs("Decks")
			self.selectionDisplay(os.listdir("Decks"))

	def checked(self, state, name): # detects origin and passes the name to the operative module
		if state == Qt.Checked:
			self.functions.decksToPractice.append(str(name))
		elif state == Qt.Unchecked:
			if name in self.functions.decksToPractice:
				self.functions.decksToPractice.remove(str(name))
		if self.functions.decksToPractice == []:
			self.ui.pushButton.setDisabled(True)
			self.ui.pushButton_3.setDisabled(True)
		else:
			self.ui.pushButton.setDisabled(False)
			self.ui.pushButton_3.setDisabled(False)
			
	def practiceInProgress(self, reverseTrue): # starts off a deck cycle, passes on to both handlePractice and handleInput
		try:
			self.functions.practice(reverseTrue) 
			self.ui.tabWidget.setTabVisible(1, True)
			self.ui.tabWidget.setCurrentIndex(1)
			self.ui.tabWidget.setTabVisible(0, False)
			self.ui.tabWidget.setTabVisible(2, False)
			for i in range(0, self.ui.gridLayout.count()):
				checkBox = self.ui.gridLayout.itemAt(i).widget()
				try:
					checkBox.setCheckState(False)
				except:
					pass
			self.functions.inPractice = True
			self.handlePractice(self.functions.i)	
		except IndexError:	
			self.error("There is an issue with this deck. Try editing it in the \"Create\" tab.")
		except UnicodeDecodeError:
			self.error("There is an issue with this deck. Try editing it in the \"Create\" tab.")

	def handlePractice(self, i): # fetches the answer from the functional module, prints to the textBrowser
		try:
			self.functions.currentQuestion = self.functions.questions[i]
			self.functions.currentAnswer = self.functions.answers[i]
			self.ui.textBrowser.append(self.functions.currentQuestion)
			self.ui.textBrowser.ensureCursorVisible()
		except IndexError:
			self.ui.textBrowser.append("You finished with " + str(self.functions.numright) + " (" + str(round(self.functions.numright/len(self.functions.questions), 2)*100) + "%) cards correct. Congrats!")
			self.ui.textBrowser.append("Hit enter to quit.")
			self.functions.inPractice = False

	def handleInput(self): # checks input, responds accordingly
		if self.functions.inPractice: 
			inputO = self.ui.lineEdit.text().strip().lower()
			if inputO == self.functions.currentAnswer:
				self.ui.textBrowser.append(inputO)
				self.ui.textBrowser.append("You are correct!")
				self.ui.textBrowser.append("")
				self.ui.textBrowser.append("=====================================")
				self.ui.textBrowser.append("")
				self.functions.numright += 1
			elif inputO != self.functions.currentAnswer:
				self.ui.textBrowser.append(inputO)
				self.ui.textBrowser.append(str("Incorrect! The answer is actually " + self.functions.currentAnswer))
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

	def importing(self): # handles importing a csv file to the app's decks file - MIGHT BE AN ISSUE w/DELETING DECKS
		try:
			self.filedir = QFileDialog(self.ui.tab_3)
			self.filedir.setOption(self.filedir.DontUseNativeDialog, True)
			self.filedir.setFileMode(QFileDialog.ExistingFile)
			self.filedir.setNameFilter("CSV files (*.csv)")
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
				for i in reversed(range(self.ui.gridLayout.count())): 
					self.ui.gridLayout.itemAt(i).widget().setParent(None)
				self.selectionDisplay(os.listdir("Decks"))
				self.ui.tabWidget.setCurrentIndex(0)
				self.ui.comboBox.setCurrentIndex(0)
		except IndexError: # thrown when the window is prematurely closed
			pass 
		
	def error(self, message): # easy to customize, will reuse throughout
		self.win = QMessageBox(self.ui.tab_3)
		self.win.setText(message) 
		self.win.setIcon(QMessageBox.Warning)
		self.win.setWindowTitle("Warning")
		self.win.exec()
		
	def createInit(self, tableData): # initializes the create tab
		# initialization
		self.tableData = tableData	
		self.table = self.ui.tableView
		self.model = tableModeling(self.tableData)
		self.table.setModel(self.model)
		
		# signals & slots
		self.ui.addButton.clicked.connect(lambda: self.addRow(self.tableData, self.model))
		self.ui.removeButton.clicked.connect(lambda: self.removeRow(self.tableData, self.model))
		self.ui.createButton.clicked.connect(lambda: self.creation(self.tableData, self.model))
		self.ui.editButton.clicked.connect(lambda: self.loadToEdit(tableData, self.model))
		self.ui.pushButton_2.clicked.connect(lambda: self.cancelCreation(tableData, self.model))
		
		# cosmetics
		width = 213 # to account for the scrollbar width; I couldn't find an easy way to dynamically enable it
		self.table.horizontalHeader().setMaximumSectionSize(width)
		self.table.horizontalHeader().setMinimumSectionSize(width)
		self.table.verticalHeader().setFixedWidth(21)
		
	def creation(self, tableData, model): # handles the click of createButton
		inputName = self.ui.inputName.text().strip()
		deckname = "Decks/" + inputName + ".csv"		
		
		if self.ui.createButton.text() == "Save":
			self.fileWrite(deckname, tableData)
			self.ui.createButton.setText("Create")
			for i in range(len(tableData)):
				tableData.pop()
			self.ui.inputName.clear()
			model.layoutChanged.emit()
		else:
			if tableData == []:
				self.error("You can't create an empty deck!")
			elif inputName == "":
				self.error("You need to name your deck!")
			elif inputName + ".csv" in os.listdir("Decks"):
				self.error("This deck already exists!")
			else:
				self.fileWrite(deckname, tableData)
				for i in range(len(tableData)):
					tableData.pop()
				self.ui.inputName.clear()
				model.layoutChanged.emit()
				for i in reversed(range(self.ui.gridLayout.count())): 
					self.ui.gridLayout.itemAt(i).widget().setParent(None)
				self.selectionDisplay(os.listdir("Decks"))
				self.ui.tabWidget.setCurrentIndex(0)
		self.ui.inputName.setReadOnly(False)
			
	def fileWrite(self, deckname, tabledata): # actually writes the files edited/produced in the interface
		try:
			with open(deckname, "w+", newline="", encoding="utf-8") as f:
				f.truncate()
				filewriter = csv.writer(f)
				for i in tabledata:
					filewriter.writerow(i)
			f.close()		
		except PermissionError:
			os.chmod(deckname, stat.S_IWRITE)
			self.fileWrite(deckname, tabledata)
		
	def removeRow(self, tableData, model): # removes a row in the Create interface
		self.ref = self.ui.tableView.selectionModel().currentIndex().row()
		try:
			tableData.pop(self.ref)
		except:
			pass
		self.scrollbarTest(tableData)
		self.ui.tableView.selectRow(len(tableData)-1)
		self.ui.scrollArea_2.ensureWidgetVisible(self.ui.tableView.selectRow(self.ref-1))
		model.layoutChanged.emit()
		
	def addRow(self, tableData, model): # adds a row in the Create interface
		self.ref = self.ui.tableView.selectionModel().currentIndex().row()+1
		self.after = []
		if self.ref == len(tableData):
			tableData.append(["", ""])
		else:
			for i in range(self.ref, len(tableData)):
				x = tableData.pop()
				self.after.append(x)
			tableData.append(["",""])
			
			for i in range(len(self.after)):
				x = self.after.pop()
				tableData.append(x)
				
		self.scrollbarTest(tableData)
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
			if newLine == []:
				for i in reformat:
					tableData.append(i)
			else:
				for i in newLine:
					tableData.append(i)
					
			self.scrollbarTest(tableData)
			model.layoutChanged.emit()
			self.ui.inputName.setText(realName)
			self.ui.inputName.setReadOnly(True)				
		except FileNotFoundError: # thrown when the window is prematurely closed
			pass
		except UnicodeDecodeError:
			self.error("This file is formatted incorrectly.\nTry opening it in Notepad and checking its format.")
		except IndexError:
			pass
		
	def settings(self, app): # handles the settings widget
		self.inherit = QDialog()
		self.window = Ui_Dialog()
		self.window.setupUi(self.inherit)
		if self.ui.centralwidget.palette().color(QPalette.Base).name() == "#ffffff":
			self.window.radioButton_2.setChecked(True)
		elif self.ui.centralwidget.palette().color(QPalette.Base).name() == "#353535":
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
		self.palette = QPalette()
		self.palette.setColor(QPalette.Text, QColor(255, 255, 255))
		self.palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
		self.palette.setColor(QPalette.Background, QColor(0, 0, 0))
		self.palette.setColor(QPalette.Base, QColor(53, 53, 53))
		self.palette.setColor(QPalette.AlternateBase, QColor(80, 80, 80))
		self.palette.setColor(QPalette.Button, QColor(53, 53, 53))
		self.palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
		app.setPalette(self.palette)
		
	def lightmode(self, app): # sets palette with light values
		app.setStyle("Fusion")
		self.palette = QPalette()
		self.palette.setColor(QPalette.Text, QColor(0, 0, 0))
		self.palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
		self.palette.setColor(QPalette.Background, QColor(211, 211, 211))
		self.palette.setColor(QPalette.Base, QColor(255, 255, 255))
		self.palette.setColor(QPalette.AlternateBase, QColor(180, 180, 180))
		self.palette.setColor(QPalette.Button, QColor(211, 211, 211))
		self.palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
		app.setPalette(self.palette)
		
	def tinytext(self): # sets font size 8
		font = QFont()
		font.setPointSize(8)
		self.ui.centralwidget.setFont(font)
		
	def normaltext(self): # sets font size 10
		font = QFont()
		font.setPointSize(10)
		self.ui.centralwidget.setFont(font)
	
	def scrollbarTest(self, tableData): # best test I could think of to handle column resizing in the tableView
		if len(tableData) > 8:
			self.ui.tableView.horizontalHeader().setMaximumSectionSize(207)
			self.ui.tableView.horizontalHeader().setMinimumSectionSize(207)
		else:
			self.ui.tableView.horizontalHeader().setMaximumSectionSize(214)
			self.ui.tableView.horizontalHeader().setMinimumSectionSize(214)
			
	def cancelPractice(self): # cancels a practicing session, resets deckHandler instance
		self.ui.tabWidget.setTabVisible(0, True)	
		self.ui.tabWidget.setTabVisible(2, True)		
		self.ui.tabWidget.setCurrentIndex(0)
		self.ui.textBrowser.clear()
		self.ui.tabWidget.setTabVisible(1, False)
		self.functions = deckHandler()
		
	def cancelCreation(self, tableData, model): # clears the Q/A model
		self.ui.inputName.clear()
		self.ui.inputName.setReadOnly(False)
		self.ui.createButton.setText("Create")
		tableData.clear()
		model.layoutChanged.emit()
		
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
			
	def toggleColls(self): # directs user interaction to handleCollections module
		self.functions.decksToPractice = [] # erases previously checked options
		if self.ui.comboBox.currentText() == "All Collections" and self.dropdown.flagForInput:
			for i in reversed(range(self.ui.gridLayout.count())): 
				self.ui.gridLayout.itemAt(i).widget().setParent(None)
			self.selectionDisplay(os.listdir("Decks"))
		elif self.ui.comboBox.currentText() == "Create Collection" or self.ui.comboBox.currentIndex() == -1: # Creating a new collection
			self.dropdown.indexChanged(self.ui, self.selectionDisplay)						
		else:
			for i in reversed(range(self.ui.gridLayout.count())): 
				self.ui.gridLayout.itemAt(i).widget().setParent(None)
			self.dropdown.loadCollection(self.ui, self.selectionDisplay)
			
	
executeGUI()
