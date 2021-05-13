from PyQt6.QtWidgets import *
from PyQt6.QtCore import QObject, QThread, Qt
from PyQt6.QtGui import *
import sys

class loadDialog(QWidget):
	def loadWidget(self, loading, thread):
		self.loading = loading
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
		
		self.loading.setWindowTitle("Flashcard Whiz")
		self.gif.start()
		self.loading.show()
		
		self.inst = loadGui()
		self.inst.moveToThread(thread)
		thread.started.connect(lambda: self.inst.generateGUI(self.loading))
		thread.start()
		

class loadGui(QObject):
	def __init__(self, parent=None):
		QObject.__init__(self, parent)
		
	def generateGUI(self, loading):
		from gui_flashcards import executeGUI
		executeGUI()
		loading.hide()
		
	
if __name__ == "__main__":
	app = QApplication(sys.argv)
	app.setStyle("Fusion")
	loading = QDialog()
	thread = QThread()
	loadDialog().loadWidget(loading, thread)
	sys.exit(app.exec())
