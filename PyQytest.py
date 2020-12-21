#from PyQt5.QtWidgets import QApplication, QLabel

#app = QApplication([])
#label = QLabel('Hello World!')
#label.show()
#app.setStyle('Fusion')

#app.exec_()
#https://build-system.fman.io/pyqt5-tutorial

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout


app = QApplication([])
app.setStyle('Fusion')
window = QWidget()
layout = QVBoxLayout()
layout.addWidget(QPushButton('Top'))
layout.addWidget(QPushButton('Bottom'))
window.setLayout(layout)
window.show()
app.exec_()
