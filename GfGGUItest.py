# importing libraries
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import os
import shutil

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # setting title
        self.setWindowTitle("Python ")

        # setting geometry
        self.setGeometry(100, 100, 600, 400)

        # calling method
        self.UiComponents()

        # showing all the widgets
        self.show()

        # method for widgets

    def UiComponents(self):
        # creating a push button
        button = QPushButton("CLICK", self)

        # setting geometry of button
        button.setGeometry(200, 150, 100, 30)

        # adding action to a button
        button.clicked.connect(self.clickme)

        # action method

    def clickme(self):
        # Gets directory (filedir)
        filedir = QFileDialog.getOpenFileName(self, 'Open File', '/', "CSV files (*.csv)")
        opendir = filedir[0]
        print(opendir)

        # creates a savelocation directory
        savelocation = 'Decks'
        print(savelocation)

        # establishes a Decks file for the csv file being imported
        try:
            os.makedirs(savelocation)
            print("Directory ", savelocation, " Created ")
        except FileExistsError:
            print("Directory ", savelocation, " already exists")

        finality = os.path.abspath(savelocation)
        print(finality)
        shutil.copy(opendir, finality)
        print("success")
        self.close()

    # create pyqt5 app


App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

# start the app
sys.exit(App.exec())
