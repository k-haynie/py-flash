from tkinter import *
from tkinter import filedialog
import os
import shutil


base = Tk() 

base.geometry('300x300')

def file_opener():
	#Gets directory (filedir)
	filedir = filedialog.askopenfilename(initialdir="/")
	print(filedir)

	#creates a savelocation directory
	savelocation = 'Decks'
	print(savelocation) 


	#establishes a Decks file for the csv file being imported
	try:
		os.makedirs(savelocation)    
		print("Directory ", savelocation,  " Created ")
	except FileExistsError:
		print("Directory ", savelocation,  " already exists")

	finality = os.path.abspath(savelocation)
	print(finality)
	shutil.copy(filedir, finality)
	print("success")


button = Button(base, text ='Select a .txt/.csv file', command = lambda:file_opener())
button.pack()
mainloop()

#figure out a way to break out of the import window. Maybe switch to a tkinter alternative?


#Entrer l'version PyQt; requires QtGUI, os, shutil

def file_import(self):
	# Gets directory (filedir)
	filedir = QFileDialog.getOpenFileName(self, 'Open File', '/')
	print(filedir)

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
	shutil.copy(filedir[0], finality)
	print("success")
	self.close()