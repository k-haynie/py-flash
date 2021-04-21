from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtCore import *

class tableModeling(QtCore.QAbstractTableModel):
	def __init__(self, tableData, parent=None):
		QtCore.QAbstractTableModel.__init__(self, parent)
		self.tableData = tableData
		self.verticalHeader = True # managing a permanent header
		
	def data(self, index, role):
		if role == Qt.ItemDataRole.DisplayRole: # manages the info getting returned
			return self.tableData[index.row()][index.column()]
		if role == Qt.ItemDataRole.EditRole:
			return self.tableData[index.row()][index.column()]
			
	def rowCount(self, index):
		return len(self.tableData)
		
	def columnCount(self, index):
		return 2
		
	def headerData(self, section, orientation, role):
		if role == Qt.ItemDataRole.DisplayRole:
			if orientation == Qt.Orientations.Horizontal:
				return ["Questions", "Answers"][section]
			if orientation == Qt.Orientations.Vertical:
				if len(self.tableData) == 1 and not self.verticalHeader:
					return "#"
				else:
					return (str(section+1))
				
	def setData(self, index, value, role):
		if role == Qt.ItemDataRole.EditRole:
			self.tableData[index.row()][index.column()] = value
			return True
	
	def flags(self, index):
		if not self.verticalHeader:
			return QAbstractItemModel.flags(self, index) & ~Qt.ItemFlags.ItemIsEnabled
		else:
			return Qt.ItemFlags.ItemIsEnabled | Qt.ItemFlags.ItemIsSelectable | Qt.ItemFlags.ItemIsEditable
		
