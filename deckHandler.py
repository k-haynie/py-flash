import os
import csv
import random

class deckHandler():
	def __init__(self):
		# establishes vars to be referenced later
		self.decksToPractice = []
		self.questions = []
		self.answers = []
		self.currentAnswer = ""
		self.currentQuestion = ""
		self.i = 0
		self.numright = 0
		self.inPractice = False # response-directing flag
		
	def practice(self, reverseTrue): 
		deckDirs = []
		
		for i in self.decksToPractice:
			deckDirs.append("Decks/" + str(i)) # creates a list of directories to be practiced
		
		for i in deckDirs: # compiles a list of questions and a list of answers
			if not reverseTrue: 
				try:
					with open(i, encoding='utf-8') as f:
						reader = csv.reader(f, delimiter=",")
						for row in reader:
							self.questions.append(row[0])
							self.answers.append(row[1].lower().strip())
					f.close()
				except IndexError:
					with open(i, encoding='utf-8') as f:
						reader = csv.reader(f, delimiter="	")
						for row in reader:
							self.questions.append(row[0])
							self.answers.append(row[1].lower().strip())
					f.close()
					self.questions.pop(0)
			# tsv files have a ANSWER\t at index[0]... weird
			else:
				try:
					with open(i, encoding='utf-8') as f:
						reader = csv.reader(f, delimiter=",")
						for row in reader:
							self.answers.append(row[0].lower().strip())
							self.questions.append(row[1])
					f.close()
				except IndexError:
					with open(i, encoding='utf-8') as f:
						reader = csv.reader(f, delimiter="	")
						for row in reader:
							self.answers.append(row[0].lower().strip())
							self.questions.append(row[1])
					f.close()
					self.questions.pop(0)
				
		# shuffles both question and answer lists keeping corresponding values at identical indexes
		seed = random.random()
		random.seed(seed)
		random.shuffle(self.questions) 
		random.seed(seed)
		random.shuffle(self.answers)
