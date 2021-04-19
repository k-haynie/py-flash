from dropDownManager import dropDownModel as dropdown
from tableDataManager import tableModeling
from settings_flashcards import Ui_Dialog
from new_flashcards_again import Ui_MainWindow
from deckHandler import deckHandler
from flow_layout import FlowLayout
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import * 
from fileDialog import Ui_Options
import loadDecks
import tableviewLogic
import practiceLogic as practice
import shutil, sys, csv, os, json


class executeGUI():
	def __init__(self):
		app = QApplication(sys.argv)
		app.setStyle("Fusion")
		app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
		
		self.mainW = QMainWindow()
		self.ui = Ui_MainWindow()		
		self.ui.setupUi(self.mainW)	
		
		self.functions = deckHandler()
		self.dropdown = dropdown()
		self.grid = FlowLayout()
		
		self.setupSlots()
		self.retrievePrefs()	
		self.mainW.show()
		sys.exit(app.exec_())
		
	def setupSlots(self): # handles slots and beginning processes
		self.selectionDisplay()
		self.createInit([])
		self.ui.tabWidget.setCurrentIndex(0)
		self.ui.tabWidget.setTabEnabled(1, False)
		self.ui.tabWidget.setTabVisible(1, False)
		self.ui.pushButton.clicked.connect(lambda: practice.practiceInProgress(self.ui, self.functions, self.error, self.uncheckAll, deckHandler, self))
		self.ui.pushButton.setDisabled(True)
		
		self.ui.discardPile.stackUnder(self.ui.stackedWidget)
		self.ui.stackedWidget.setMinimumSize(0, 0)
		self.ui.lineEdit.returnPressed.connect(lambda: practice.handleInput(self.ui.lineEdit.text().strip(), self.ui, self.functions, self.mainW, deckHandler, self))
		
		self.ui.toolButton_2.clicked.connect(self.settings)
		self.ui.importButton.clicked.connect(lambda: tableviewLogic.importing(self.ui.tab_3, self.ui, self.deleteSelection, self.selectionDisplay))
		self.ui.pushButton_3.clicked.connect(self.creationStarted)
		self.ui.revPractice.stateChanged.connect(lambda state: practice.practiceFlags("reverse", state, self.functions))
		self.ui.timedPractice.stateChanged.connect(lambda state: practice.practiceFlags("timed", state, self.functions))
		
		self.dropdown.loadOptions(self.ui) # initializes a list in the drop-down menu
		self.ui.comboBox.setMaxVisibleItems(5)
		self.ui.comboBox.currentIndexChanged.connect(lambda: self.loadSelection(self.ui.comboBox.currentText()))
		self.ui.comboBox.setSizeAdjustPolicy(2)
		
		self.ui.gridLayout_3.addLayout(self.grid, 0, 0)
	
		self.ui.buttonDel.clicked.connect(lambda: self.confirmDialog(self.deleteCollection, "delete this collection"))
		self.ui.buttonAdd.clicked.connect(self.addDialog)
		self.ui.buttonRem.clicked.connect(self.remDialog)
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
	
	
	# def practiceFlags(self, name, state):
		# if name == "reverse":
			# if state == 0:
				# self.functions.reverseTrue = False
			# elif state == 2:
				# self.functions.reverseTrue = True
		# elif name == "timed":
			# if state == 0:
				# self.functions.timed = False
			# elif state == 2:
				# self.functions.timed = True
		
	# def practiceInProgress(self): # starts off a deck cycle, passes on to both handlePractice and handleInput
		# self.functions.practice(self.ui, self.handleTimeout) 
		# if len(self.functions.questions) == 0:
			# self.error("This is an empty deck!")
		# else:
			# try:
				# try:
					# self.ui.discardPile.widget(1).deleteLater()
					# self.ui.discardPile.removeWidget(self.ui.discardPile.widget(1))
				# except:
					# pass
				# self.ui.tabWidget.setTabEnabled(1, True)
				# self.ui.tabWidget.setTabVisible(1, True)
				# self.ui.tabWidget.setCurrentIndex(1)
				# self.ui.tabWidget.setTabEnabled(0, False)
				# self.ui.tabWidget.setTabVisible(0, False)
				# self.ui.tabWidget.setTabEnabled(2, False)
				# self.ui.tabWidget.setTabVisible(2, False)
				# self.ui.numRight.setText("Right: ")
				# self.ui.numWrong.setText("Wrong: ")
				# self.ui.timerDisplay.display("--:--")
				# self.uncheckAll()
				# self.functions.inPractice = True
				# self.handlePractice(self.functions.i)
				# self.ui.revPractice.setChecked(False)
				# self.ui.timedPractice.setChecked(False)
			# except IndexError:	
				# self.error("There is an issue with this deck. Try editing it in the \"Create\" tab.")
				# self.functions = deckHandler()
			# except UnicodeDecodeError:
				# self.error("There is an issue with this deck. Try editing it in the \"Create\" tab.")
				# self.functions = deckHandler()

	# def handlePractice(self, i): # fetches the answer from the functional module, prints to the textBrowser
		# try:
			# if self.functions.inPractice:
				# self.functions.currentQuestion = self.functions.questions[i]
				# self.functions.currentAnswer = self.functions.answers[i]
				
				# self.createPage("""QPushButton {border-image: url("assets/card_front.png")} QTextEdit {color: white; border: 0; background-color: rgba(0, 0, 0, 0)}""", self.functions.currentQuestion, 1)
				# self.createPage("""QPushButton {border-image: url("assets/card_right.png")} QTextEdit {color: white; border: 0; background-color: rgba(0, 0, 0, 0)}""", self.functions.currentAnswer, 2)
				# self.createPage("""QPushButton {border-image: url("assets/card_wrong.png")} QTextEdit {color: white; border: 0; background-color: rgba(0, 0, 0, 0)}""", self.functions.currentAnswer, 3)
				# self.ui.stackedWidget.setCurrentIndex(1)
		# except IndexError:
			# self.functions.inPractice = False
			# self.percentageRight = round(self.functions.numright/len(self.functions.questions) * 100, 2)
			# if self.percentageRight < 70:
				# self.message = "You should practice these cards more."
			# elif self.percentageRight < 80:
				# self.message = "Fair job."
			# elif self.percentageRight < 90:
				# self.message = "Kudos!"
			# elif self.percentageRight < 100:
				# self.message = "Terrific Job!"
			# else:
				# self.message = "Perfect!"
			# finished = f"You finished with {str(self.functions.numright)} ({self.percentageRight}%) cards correct. {self.message} Hit enter to quit."
			# self.createPage("border: 0", finished, 1)
			# self.ui.stackedWidget.setCurrentIndex(1)
			# self.functions.timer.stop()
			
	# def createPage(self, styleSheet, text, index):
		# try:
			# self.ui.stackedWidget.removeWidget(self.ui.stackedWidget.widget(index))
			# self.ui.stackedWidget.widget(index).deleteLater()
		# except:
			# pass
		# self.btn = QPushButton()
		
		# self.btn.text = QTextEdit(self.btn)
		# self.btn.text.setMouseTracking(False)
		
		# fontMet = QFontMetrics(self.ui.tabWidget.font())
		# height = fontMet.height()
		# numLines = (fontMet.horizontalAdvance(text)//150) + 1
		
		# self.btn.text.setMaximumHeight(height * numLines + height)
		# self.btn.text.viewport().setAutoFillBackground(False)
		# self.btn.text.setText(text)
		# self.btn.text.setAlignment(Qt.AlignCenter)
		# self.btn.text.setTextInteractionFlags(Qt.NoTextInteraction)
		
		# self.btn.setLayout(QVBoxLayout(self.btn))
		# self.btn.layout().setAlignment(Qt.AlignCenter)
		# self.btn.layout().addStretch()
		# self.btn.layout().addWidget(self.btn.text)
		# self.btn.layout().addStretch()
		
		# self.btn.setStyleSheet(styleSheet)
		# self.ui.stackedWidget.insertWidget(index, self.btn)
		
	# def handleInput(self, inputO): # checks input, responds accordingly
		# if self.functions.inAnimation:
			# pass
		# elif self.functions.inPractice: 
			# self.functions.inAnimation = True
			# self.createImages(QPixmap(QWidget.grab(self.ui.stackedWidget.widget(1))), 1)
			# self.createImages(QPixmap(QWidget.grab(self.ui.stackedWidget.widget(2))), 2)
			# self.createImages(QPixmap(QWidget.grab(self.ui.stackedWidget.widget(3))), 3)	
			# self.ui.stackedWidget.setCurrentIndex(1)
			
			
			# if inputO.lower() == self.functions.currentAnswer.lower():
				# self.functions.numright += 1
				# self.ui.numRight.setText(f"Right: {self.functions.numright}")
				# self.mainW.setMinimumSize(self.mainW.size())
				# self.mainW.setMaximumSize(self.mainW.size())
				# self.createImages(self.ui.stackedWidget.widget(2).pixmap(), 0, True)
				# self.flippingAnimation(2)
				
			# elif inputO.lower() != self.functions.currentAnswer.lower():
				# self.ui.numWrong.setText(f"Wrong: {self.functions.i - self.functions.numright + 1}")
				# self.mainW.setMinimumSize(self.mainW.size())
				# self.mainW.setMaximumSize(self.mainW.size())
				# self.createImages(self.ui.stackedWidget.widget(3).pixmap(), 0, True)
				# self.flippingAnimation(3)
				
			# self.ui.lineEdit.clear()
			# self.functions.i += 1			
		# else:
			# self.ui.tabWidget.setTabEnabled(0, True)
			# self.ui.tabWidget.setTabVisible(0, True)	
			# self.ui.tabWidget.setTabEnabled(2, True)
			# self.ui.tabWidget.setTabVisible(2, True)		
			# self.ui.tabWidget.setCurrentIndex(0)
			# self.ui.lineEdit.clear()
			# self.ui.tabWidget.setTabEnabled(1, False)
			# self.ui.tabWidget.setTabVisible(1, False)
			# self.functions = deckHandler()
			
	# def handleTimeout(self):
		# if not self.functions.inAnimation:
			# self.functions.inPractice = False
			# message = f"You timed out with {self.functions.i}/{len(self.functions.questions)} answered, and {self.functions.numright} correct. Hit enter to quit."
			# self.createPage("border: 0", message, 1)
			# self.ui.stackedWidget.setCurrentIndex(1)
		
	# def createImages(self, pixmap, index, proceed=False): # creates a pixmap image for both the front and back of the cards
		# self.face = pixmap
		
		# self.rounded = QPixmap(self.face.size())
		# self.rounded.fill(QColor("transparent"))
		# painter = QPainter(self.rounded)
		# painter.setRenderHint(QPainter.Antialiasing)
		# painter.setBrush(QBrush(self.face))
		# painter.setPen(Qt.NoPen)
		# painter.drawRoundedRect(self.face.rect(), 35, 35)
		
		# if proceed == False:
			# self.ui.stackedWidget.widget(index).deleteLater()
			# self.ui.stackedWidget.removeWidget(self.ui.stackedWidget.widget(index))
			# self.ui.stackedWidget.insertWidget(index, QLabel())
			# self.ui.stackedWidget.widget(index).setPixmap(self.rounded)
			# self.ui.stackedWidget.widget(index).setScaledContents(True)
		# else:
			# self.newImageCont = QLabel(self.ui.tab_2)
			# self.newImageCont.setAutoFillBackground(False)
			# self.newImageCont.setMinimumHeight(267)
			# self.newImageCont.setMinimumWidth(200)
			# self.newImageCont.setStyleSheet("QLabel {border-radius: 35px}")
			# self.newImageCont.setPixmap(self.rounded)
			# self.newImageCont.setScaledContents(True)
			
	# def flippingAnimation(self, index):
		# self.shrink = QPropertyAnimation(self.ui.stackedWidget, b"size")
		# self.shrink.setEndValue(QSize(0, 267))
		# self.shrink.setEasingCurve(QEasingCurve.InCubic)
		# self.shrink.setDuration(400)
		
		# self.moveMid = QPropertyAnimation(self.ui.stackedWidget, b"pos")
		# self.moveMid.setEndValue(QPoint(self.ui.stackedWidget.geometry().x()+100, self.ui.stackedWidget.geometry().y()))
		# self.moveMid.setEasingCurve(QEasingCurve.InCubic)
		# self.moveMid.setDuration(400)
		# self.moveMid.finished.connect(lambda: self.ui.stackedWidget.setCurrentIndex(index))
		
		# self.flipBack = QParallelAnimationGroup()
		# self.flipBack.addAnimation(self.shrink)
		# self.flipBack.addAnimation(self.moveMid)
	
		# self.expand = QPropertyAnimation(self.ui.stackedWidget, b"size")
		# self.expand.setEasingCurve(QEasingCurve.OutCubic)
		# self.expand.setStartValue(QSize(0, 267))
		# self.expand.setEndValue(QSize(200, 267))
		# self.expand.setDuration(400)
		
		# self.moveBack = QPropertyAnimation(self.ui.stackedWidget, b"pos")
		# self.moveBack.setEasingCurve(QEasingCurve.OutCubic)
		# self.moveBack.setStartValue(QPoint(self.ui.stackedWidget.geometry().x()+100, self.ui.stackedWidget.geometry().y()))
		# self.moveBack.setEndValue(QPoint(self.ui.stackedWidget.geometry().x(), self.ui.stackedWidget.geometry().y()))
		# self.moveBack.setDuration(400)
		
		# self.flipForward = QParallelAnimationGroup()
		# self.flipForward.addAnimation(self.expand)
		# self.flipForward.addAnimation(self.moveBack)
		# self.flipForward.finished.connect(self.newImageCont.show)
		# self.flipForward.finished.connect(self.newCard)
		
		# self.slide = QPropertyAnimation(self.newImageCont, b"pos")
		# self.slide.setStartValue(QPoint(self.ui.stackedWidget.geometry().x(), self.ui.stackedWidget.geometry().y()))
		# self.slide.setEndValue(QPoint(self.ui.discardPile.geometry().x(), self.ui.discardPile.geometry().y()))
		# self.slide.setEasingCurve(QEasingCurve.InOutCubic)
		# self.slide.setDuration(500)
		# self.slide.finished.connect(self.resetSlide)
		

		# self.fullFlip = QSequentialAnimationGroup()
		# self.fullFlip.addAnimation(self.flipBack)
		# self.fullFlip.addAnimation(self.flipForward)
		# self.fullFlip.addAnimation(self.slide)
		# self.fullFlip.finished.connect(self.turnOffAnimation)
		
		# self.fullFlip.start()
	
	# def turnOffAnimation(self):
		# self.functions.inAnimation = False
		# self.mainW.setMaximumSize(16777215, 16777215)
		# self.mainW.setMinimumSize(600, 500)
	
	# def resetSlide(self):
		# try:
			# self.ui.discardPile.widget(1).deleteLater()
			# self.ui.discardPile.removeWidget(self.ui.discard.widget(1))
		# except:
			# pass
		# self.ui.discardPile.insertWidget(1, self.newImageCont)
		# self.ui.discardPile.setCurrentIndex(1)
		
	# def newCard(self):
		# self.ui.stackedWidget.setCurrentIndex(0)
		# self.ui.lineEdit.clear()
		# self.handlePractice(self.functions.i)
	
	
	# HANDLES TABLEVIEW on TAB 3
	
		
	def error(self, message): # easy to customize, will reuse throughout
		self.win = QMessageBox(self.mainW)
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
		
		self.ui.pushButton_2.setDisabled(True)
		self.ui.practiceCancelBtn.clicked.connect(lambda: self.confirmDialog(self.cancelPractice, "cancel your practice"))
		self.ui.deckDelBtn.clicked.connect(lambda: self.confirmDialog(tableviewLogic.deleteDeck, "delete this deck", tableData, self.model))
		self.model.layoutChanged.connect(lambda: self.cancelBtnShown(self.model))
		
		# cosmetics
		self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.table.horizontalHeader().setSectionsClickable(False)
		self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.table.verticalHeader().setSectionsClickable(False)
			
	def cancelBtnShown(self, model):
		if model.verticalHeader: 
			self.ui.pushButton_2.setDisabled(False)
		else:
			self.ui.pushButton_2.setDisabled(True)
		

	# COSMETICS
	
	
	def settings(self): # handles the settings widget
		self.inherit = QDialog(self.mainW)
		self.window = Ui_Dialog()
		self.window.setupUi(self.inherit)
		if str(qApp.styleSheet()).find("color: rgb(255, 255, 255)") == 148:
			self.window.radioButton_2.setChecked(True)
		elif str(qApp.styleSheet()).find("color: rgb(255, 255, 255)") == 8:
			self.window.radioButton.setChecked(True)
		if self.ui.tabWidget.font().pointSize() == 10:
			self.window.radioButton_4.setChecked(True)
		elif self.ui.tabWidget.font().pointSize() == 8:
			self.window.radioButton_3.setChecked(True)
		self.window.radioButton.clicked.connect(self.darkmode)
		self.window.radioButton.clicked.connect(lambda: self.savePrefs(0, "darkmode"))
		self.window.radioButton_2.clicked.connect(self.lightmode)
		self.window.radioButton_2.clicked.connect(lambda: self.savePrefs(0, "lightmode"))
		self.window.radioButton_3.clicked.connect(self.tinytext)
		self.window.radioButton_3.clicked.connect(lambda: self.savePrefs(1, "tinytext"))
		self.window.radioButton_4.clicked.connect(self.normaltext)
		self.window.radioButton_4.clicked.connect(lambda: self.savePrefs(1, "normaltext"))
		self.inherit.setModal(True)
		self.inherit.show()
		
	def darkmode(self): # sets palette with dark values
		darkSettings = ("""* {
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
		qApp.setStyleSheet(f"* {darkSettings}")
		
	def lightmode(self): # sets palette with light values
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
		qApp.setStyleSheet(f"* {lightSettings}")
		
	def tinytext(self): # sets font size 8
		self.ui.tabWidget.setStyleSheet("* {font-size: 8pt}")
		
	def normaltext(self): # sets font size 10
		self.ui.tabWidget.setStyleSheet("* {font-size: 10pt}")
			
	
	# CANCELING
	
	
	def cancelPractice(self): # cancels a practicing session, resets deckHandler instance
		self.ui.tabWidget.setTabEnabled(0, True)
		self.ui.tabWidget.setTabVisible(0, True)
		self.ui.tabWidget.setTabEnabled(2, True)	
		self.ui.tabWidget.setTabVisible(2, True)		
		self.ui.tabWidget.setCurrentIndex(0)
		self.ui.lineEdit.clear()
		self.functions.timer.stop()
		self.ui.tabWidget.setTabEnabled(1, False)
		self.ui.tabWidget.setTabVisible(1, False)
		self.functions = deckHandler()
		
	def cancelCreation(self, tableData, model): # clears the Q/A model
		confirmWindow = QMessageBox(self.ui.tab_3)
		confirmWindow.setText("Are you sure you want to cancel?")
		confirmWindow.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
		confirmWindow.setIcon(QMessageBox.Warning)
		confirmWindow.setWindowTitle("Confirm")
		confirmWindow.setModal(True)
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
		confirmWindow.setModal(True)
		confirmWindow.setDefaultButton(QMessageBox.No)
		proceed = confirmWindow.exec_()
		if tableData != 0 and proceed == QMessageBox.Yes:
			tableviewLogic.deleteDeck(tableData, model, self.ui)
		elif proceed == QMessageBox.Yes:
			method()
		
	
	# USER PREFERENCES
	
	
	def retrievePrefs(self): # loads previous settings upon window load
		if os.path.isfile("preferences.csv"):
			values = []
			with open("preferences.csv", "r", newline="", encoding="utf-8") as preferences:
				values.append([row for row in csv.reader(preferences, delimiter=",")][0])
			preferences.close()
			if values[0][0] == "lightmode":
				self.lightmode()
			elif values[0][0] == "darkmode":
				self.darkmode()
			if values[0][1] == "tinytext":
				self.tinytext()
			elif values[0][1] == "normaltext":
				self.normaltext()
		else:
			with open("preferences.csv", "w+", newline="", encoding="utf-8") as preferences:
				x = csv.writer(preferences)
				x.writerow(["lightmode", "tinytext"])
			preferences.close()
			self.lightmode()
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
		
	def addDialog(self):
		index = self.ui.comboBox.currentText()
		
		with open("collections.txt", "r", encoding="utf-8") as collections:
			data = json.load(collections)
			base = data[index]
		collections.close()
		
		excludedNames = set(os.listdir("Decks")) - set(base)
		self.createDialog(sorted(excludedNames, key=str.casefold), self.addToCollection)		
		
	def remDialog(self):
		index = self.ui.comboBox.currentText()
		
		with open("collections.txt", "r", encoding="utf-8") as collections:
			data = json.load(collections)
			base = data[index]
		collections.close()
		
		names = set(base)
		self.createDialog(sorted(names, key=str.casefold), self.removeFromCollection)
		
	def addToCollection(self, name): # adds to a collection (model and view)
		realName = name
		with open("collections.txt", "r+", encoding="utf-8") as collections:
			data = json.load(collections)
			if realName not in data[self.ui.comboBox.currentText()]:
				data[self.ui.comboBox.currentText()].append(realName)
				collections.seek(0)
				collections.truncate()
				json.dump(data, collections)
		collections.close()
		self.loadSelection(self.ui.comboBox.currentText())
		
	def dirCheck(self, dlg): # makes the dialog window non-traversable
		dlg.setDirectory("Decks/")		
		
	def createDialog(self, options, method):
		self.fd = QDialog(self.mainW)
		self.fd.setModal(True)
		self.fdinst = Ui_Options()
		self.fdinst.setupUi(self.fd)
		optionModel = QStandardItemModel()
		optionModel.setColumnCount(1)
		for i in options:
			optionModel.appendRow(QStandardItem(QIcon("assets/decks.png"), i))
		self.fdinst.listView.setModel(optionModel)
		self.fd.show()
		self.fd.accepted.connect(lambda: method(self.fdinst.listView.currentIndex().data()))
		
	def removeFromCollection(self, name): # removes from a collecion (model and view)
		index = self.ui.comboBox.currentText()
		realName = name
		with open("collections.txt", "r+", encoding="utf-8") as collections:
			data = json.load(collections)
			if realName in data[index]:
				data[index].remove(realName)
				collections.seek(0)
				collections.truncate()
				json.dump(data, collections)
		collections.close()
		
		self.loadSelection(index) 
		
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
