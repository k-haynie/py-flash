from gui_flashcards import executeGUI
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import * 
import sys, time

class loadDialog(QWidget):
	initialized = pyqtSignal()

	
	def loadWidget(self, loading, GuiThread):
		self.loading = loading
		self.GuiThread = GuiThread
		self.loading.setMinimumSize(200, 100)
		self.loading.setMaximumSize(200, 100)
		
		self.loadingGif = QLabel()
		self.gif = QMovie("assets/loading.gif")
		self.loadingGif.setMovie(self.gif)
		self.loadingText = QLabel("Loading...")
		
		self.masterLayout = QVBoxLayout()
		self.masterLayout.addWidget(self.loadingGif, 0, Qt.Alignment.AlignHCenter)
		self.masterLayout.addWidget(self.loadingText, 1, Qt.Alignment.AlignHCenter)
		
		self.loading.setLayout(self.masterLayout)
		self.loading.setStyleSheet("background-color: rgb(255, 255, 255); color: rgb(0, 0, 0)")
		
		self.initialized.connect(executeGUI)
		
		# self.Gui = worker()
		# self.GuiThread.started.connect(self.Gui.work)
		# self.Gui.moveToThread(self.GuiThread)
		# self.initialized.connect(self.GuiThread.start)
		
		self.loading.setWindowTitle("Flashcard Whiz")
		self.gif.start()
		self.loading.show()
		self.initialized.emit()
	
class worker(QObject):
	def __init__(self, parent=None):
		QObject.__init__(self, parent=parent)
	def work(self):
		executeGUI()
	
if __name__ == "__main__":
	app = QApplication(sys.argv)
	app.setStyle("Fusion")
	loading = QDialog()	
	thread = QThread
	loadDialog().loadWidget(loading, thread)
	loading.hide()
	sys.exit(app.exec())
