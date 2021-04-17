from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import *

class tableModeling(QtCore.QAbstractTableModel):
	def __init__(self, tableData, parent=None):
		QtCore.QAbstractTableModel.__init__(self, parent)
		self.tableData = tableData
		self.verticalHeader = True # managing a permanent header
		
	def data(self, index, role):
		if role == Qt.DisplayRole: # manages the info getting returned
			return self.tableData[index.row()][index.column()]
		if role == Qt.EditRole:
			return self.tableData[index.row()][index.column()]
			
	def rowCount(self, index):
		return len(self.tableData)
		
	def columnCount(self, index):
		return 2
		
	def headerData(self, section, orientation, role):
		if role == Qt.DisplayRole:
			if orientation == Qt.Horizontal:
				return ["Questions", "Answers"][section]
			if orientation == Qt.Vertical:
				if len(self.tableData) == 1 and not self.verticalHeader:
					return "#"
				else:
					return (str(section+1))
				
	def setData(self, index, value, role):
		if role == Qt.EditRole:
			self.tableData[index.row()][index.column()] = value
			return True
	
	def flags(self, index):
		if not self.verticalHeader:
			return QAbstractItemModel.flags(self, index) & ~Qt.ItemIsEnabled
		else:
			return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
		
