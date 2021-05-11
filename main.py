from gui_flashcards import executeGUI
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import * 
import sys, time

class loadDialog(QWidget):
	initialized = pyqtSignal()
	gifLoaded = pyqtSignal()

	def loadWidget(self, loading):
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
		self.initialized.connect(executeGUI)
		self.initialized.emit()
	
if __name__ == "__main__":
	app = QApplication(sys.argv)
	app.setStyle("Fusion")
	loading = QDialog()
	loadDialog().loadWidget(loading)
	loading.hide()
	sys.exit(app.exec())
