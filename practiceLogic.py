from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import * 


def practiceFlags(name, state, functions):
	if name == "reverse":
		if state == 0:
			functions.reverseTrue = False
		elif state == 2:
			functions.reverseTrue = True
	elif name == "timed":
		if state == 0:
			functions.timed = False
		elif state == 2:
			functions.timed = True
	
def practiceInProgress(ui, functions, error, uncheckAll, deckHandler, obj): # starts off a deck cycle, passes on to both handlePractice and handleInput
	try:
		try:
			ui.newImageCont.deleteLater()
			ui.discardPile.widget(1).deleteLater()
			ui.discardPile.removeWidget(ui.discardPile.widget(1))
		except:
			pass
		ui.selectAll.setText("Select All")
		ui.tabWidget.setTabEnabled(1, True)
		ui.tabWidget.setTabVisible(1, True)
		functions.practice(ui, handleTimeout, error)		
		ui.tabWidget.setCurrentIndex(1)
		ui.tabWidget.setTabEnabled(0, False)
		ui.tabWidget.setTabVisible(0, False)
		ui.tabWidget.setTabEnabled(2, False)
		ui.tabWidget.setTabVisible(2, False)
		ui.numRight.setText("Right: 0")
		ui.numWrong.setText("Wrong: 0")
		ui.timerDisplay.display("--:--")
		uncheckAll()
		functions.inPractice = True
		handlePractice(functions.i, functions, ui)
		ui.revPractice.setChecked(False)
		ui.timedPractice.setChecked(False)
	except (IndexError, UnicodeDecodeError):	
		error(f"There is an issue with {obj.pluralSelected()[0]}. Try editing {obj.pluralSelected()[1]} in the \"Create\" tab.")
		obj.functions = deckHandler()
		obj.uncheckAll()
	except Exception:
		error("Something went wrong!")
		obj.functions = deckHandler()
		obj.uncheckAll()

def handlePractice(i, functions, ui): # fetches the answer from the functional module, prints to the textBrowser
	try:
		functions.currentQuestion = functions.questions[i]
		functions.currentAnswer = functions.answers[i]
		
		createPage("""QPushButton {border-image: url("assets/card_front.png")} QTextEdit {color: white; border: 0; background-color: rgba(0, 0, 0, 0)}""", functions.currentQuestion, 1, ui)
		createPage("""QPushButton {border-image: url("assets/card_right.png")} QTextEdit {color: white; border: 0; background-color: rgba(0, 0, 0, 0)}""", functions.currentAnswer, 2, ui)
		createPage("""QPushButton {border-image: url("assets/card_wrong.png")} QTextEdit {color: white; border: 0; background-color: rgba(0, 0, 0, 0)}""", functions.currentAnswer, 3, ui)
		ui.stackedWidget.setCurrentIndex(1)
	except IndexError:
		functions.inPractice = False
		percentageRight = round(functions.numright/len(functions.questions) * 100, 2)
		if percentageRight < 70:
			ui.message = "You should practice these cards more."
		elif percentageRight < 80:
			ui.message = "Fair job."
		elif percentageRight < 90:
			ui.message = "Kudos!"
		elif percentageRight < 100:
			ui.message = "Terrific Job!"
		else:
			ui.message = "Perfect!"
		finished = f"You finished with {str(functions.numright)} ({percentageRight}%) cards correct. {ui.message} Hit enter to quit."
		createPage("border: 0", finished, 1, ui, False, functions)
		ui.stackedWidget.setCurrentIndex(1)
		functions.timer.stop()

def createPage(styleSheet, text, index, ui, dist=True, functions=0):
	try:
		ui.stackedWidget.removeWidget(ui.stackedWidget.widget(index))
		ui.stackedWidget.widget(index).deleteLater()
	except:
		pass
	btn = QPushButton()
	
	btn.text = QTextEdit(btn)
	btn.text.setMouseTracking(False)
	
	fontMet = QFontMetrics(ui.tabWidget.font())
	height = fontMet.height()
	if dist:
		numLines = (fontMet.horizontalAdvance(text)//135) + 1
	else:
		numLines = ((fontMet.horizontalAdvance(text) + fontMet.horizontalAdvance(str(functions.numright)) + fontMet.horizontalAdvance(ui.message))//135)
	
	btn.text.setMaximumHeight((height * numLines) + height)
	btn.text.viewport().setAutoFillBackground(False)
	btn.text.setText(text)
	btn.text.setAlignment(Qt.Alignment.AlignCenter)
	btn.text.setTextInteractionFlags(Qt.TextInteractionFlags.NoTextInteraction)
	
	btn.setLayout(QVBoxLayout(btn))
	btn.layout().setAlignment(btn.layout(), Qt.Alignment.AlignCenter)
	btn.layout().addStretch()
	btn.layout().addWidget(btn.text)
	btn.layout().addStretch()
	
	btn.setStyleSheet(styleSheet)
	ui.stackedWidget.insertWidget(index, btn)
	
def handleInput(inputO, ui, functions, mainW, deckHandler, obj): # checks input, responds accordingly
	if functions.inAnimation:
		obj.fullFlip.stop()
		turnOffAnimation(functions, mainW)
		resetSlide(ui)
		newCard(ui, functions)
	elif functions.inPractice: 
		functions.inAnimation = True
		createImages(QPixmap(QWidget.grab(ui.stackedWidget.widget(1))), 1, ui, obj)
		createImages(QPixmap(QWidget.grab(ui.stackedWidget.widget(2))), 2, ui, obj)
		createImages(QPixmap(QWidget.grab(ui.stackedWidget.widget(3))), 3, ui, obj)	
		ui.stackedWidget.setCurrentIndex(1)
		
		if inputO.lower() == functions.currentAnswer.lower():
			functions.numright += 1
			ui.numRight.setText(f"Right: {functions.numright}")
			mainW.setMinimumSize(mainW.size())
			mainW.setMaximumSize(mainW.size())
			createImages(ui.stackedWidget.widget(2).pixmap(), 0, ui, obj, True)
			flippingAnimation(2, ui, functions, mainW, obj)
			
		elif inputO.lower() != functions.currentAnswer.lower():
			ui.numWrong.setText(f"Wrong: {functions.i - functions.numright + 1}")
			mainW.setMinimumSize(mainW.size())
			mainW.setMaximumSize(mainW.size())
			createImages(ui.stackedWidget.widget(3).pixmap(), 0, ui, obj, True)
			flippingAnimation(3, ui, functions, mainW, obj)
			
		functions.i += 1			
	else:
		ui.tabWidget.setTabEnabled(0, True)
		ui.tabWidget.setTabVisible(0, True)	
		ui.tabWidget.setTabEnabled(2, True)
		ui.tabWidget.setTabVisible(2, True)		
		ui.tabWidget.setCurrentIndex(0)
		ui.lineEdit.clear()
		ui.tabWidget.setTabEnabled(1, False)
		ui.tabWidget.setTabVisible(1, False)
		obj.functions = deckHandler()
		
def handleTimeout(functions, ui):
	if not functions.inAnimation:
		functions.inPractice = False
		message = f"You timed out with {functions.i}/{len(functions.questions)} answered, and {functions.numright} correct. Hit enter to quit."
		createPage("border: 0", message, 1, ui, 2)
		ui.stackedWidget.setCurrentIndex(1)
	
def createImages(pixmap, index, ui, obj, proceed=False): # creates a pixmap image for both the front and back of the cards
	obj.face = pixmap
	
	obj.rounded = QPixmap(obj.face.size())
	obj.rounded.fill(QColor("transparent"))
	obj.painter = QPainter(obj.rounded)
	obj.painter.setRenderHint(QPainter.RenderHints.Antialiasing)
	obj.painter.setBrush(QBrush(obj.face))
	obj.painter.setPen(Qt.PenStyle.NoPen)
	obj.painter.drawRoundedRect(obj.face.rect(), 35, 35)
	obj.painter.end()
	
	if proceed == False:
		ui.stackedWidget.widget(index).deleteLater()
		ui.stackedWidget.removeWidget(ui.stackedWidget.widget(index))
		ui.stackedWidget.insertWidget(index, QLabel())
		ui.stackedWidget.widget(index).setPixmap(obj.rounded)
		ui.stackedWidget.widget(index).setStyleSheet("QLabel {border-radius: 35px}")
		ui.stackedWidget.widget(index).setScaledContents(True)
	else:
		ui.newImageCont = QLabel(ui.tab_2)
		ui.newImageCont.setPixmap(obj.rounded)
		ui.newImageCont.setStyleSheet("QLabel {border-radius: 35px}")
		ui.newImageCont.setScaledContents(True)
		ui.newImageCont.setMinimumHeight(267)
		ui.newImageCont.setMinimumWidth(200)
		
def flippingAnimation(index, ui, functions, mainW, obj):
	# For some reason, I could not get the setEasingCurve function to work normally on Qt6
	# so I used the following roundabout way - perhaps that's a bug, but the lack of documentation and 
	# comprehensive examples is sorely felt
	ui.lineEdit.clear()
	
	inCubic = QEasingCurve()
	inCubic.setType(QEasingCurve.Type.InCubic)
	outCubic = QEasingCurve()
	outCubic.setType(QEasingCurve.Type.OutCubic)
	inOutCubic = QEasingCurve()
	inOutCubic.setType(QEasingCurve.Type.InOutCubic)
	
	obj.shrink = QPropertyAnimation(ui.stackedWidget, b"size")
	obj.shrink.setEndValue(QSize(0, 267))
	obj.shrink.setEasingCurve(inCubic)
	obj.shrink.setDuration(400)
	
	obj.moveMid = QPropertyAnimation(ui.stackedWidget, b"pos")
	obj.moveMid.setEndValue(QPoint(ui.stackedWidget.geometry().x()+100, ui.stackedWidget.geometry().y()))
	obj.moveMid.setEasingCurve(inCubic)
	obj.moveMid.setDuration(400)
	obj.moveMid.finished.connect(lambda: ui.stackedWidget.setCurrentIndex(index))
	
	obj.flipBack = QParallelAnimationGroup()
	obj.flipBack.addAnimation(obj.shrink)
	obj.flipBack.addAnimation(obj.moveMid)

	obj.expand = QPropertyAnimation(ui.stackedWidget, b"size")
	obj.expand.setEasingCurve(outCubic)
	obj.expand.setStartValue(QSize(0, 267))
	obj.expand.setEndValue(QSize(200, 267))
	obj.expand.setDuration(400)
	
	obj.moveBack = QPropertyAnimation(ui.stackedWidget, b"pos")
	obj.moveBack.setEasingCurve(outCubic)
	obj.moveBack.setStartValue(QPoint(ui.stackedWidget.geometry().x()+100, ui.stackedWidget.geometry().y()))
	obj.moveBack.setEndValue(QPoint(ui.stackedWidget.geometry().x(), ui.stackedWidget.geometry().y()))
	obj.moveBack.setDuration(400)
	
	obj.flipForward = QParallelAnimationGroup()
	obj.flipForward.addAnimation(obj.expand)
	obj.flipForward.addAnimation(obj.moveBack)
	obj.flipForward.finished.connect(ui.newImageCont.show)
	obj.flipForward.finished.connect(lambda: newCard(ui, functions))
	
	obj.slide = QPropertyAnimation(ui.newImageCont, b"pos")
	obj.slide.setStartValue(QPoint(ui.stackedWidget.geometry().x(), ui.stackedWidget.geometry().y()))
	obj.slide.setEndValue(QPoint(ui.discardPile.geometry().x(), ui.discardPile.geometry().y()))
	obj.slide.setEasingCurve(inOutCubic)
	obj.slide.setDuration(500)
	obj.slide.finished.connect(lambda: resetSlide(ui))
	

	obj.fullFlip = QSequentialAnimationGroup()
	obj.fullFlip.addAnimation(obj.flipBack)
	obj.fullFlip.addAnimation(obj.flipForward)
	obj.fullFlip.addAnimation(obj.slide)
	obj.fullFlip.finished.connect(lambda: turnOffAnimation(functions, mainW))
	
	obj.fullFlip.start()

def turnOffAnimation(functions, mainW):
	functions.inAnimation = False
	mainW.setMaximumSize(16777215, 16777215)
	mainW.setMinimumSize(600, 500)

def resetSlide(ui):
	try:
		ui.discardPile.widget(1).deleteLater()
		ui.discardPile.removeWidget(ui.discard.widget(1))
	except:
		pass
	ui.discardPile.insertWidget(1, ui.newImageCont)
	ui.discardPile.setCurrentIndex(1)
	
def newCard(ui, functions):
	ui.stackedWidget.setCurrentIndex(0)
	handlePractice(functions.i, functions, ui)
	

