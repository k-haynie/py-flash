import csv
import random

def shuffleExec(filename):
	questions = []
	answers = []
	index = 0
	numright = 0



	with open(filename, encoding='utf-8') as tsv:
		reader = csv.reader(tsv, delimiter="\t")
	
		for row in reader:
			questions.append(row[0][::-1])
			answers.append(row[1].lower())
		seed = random.random()
		random.seed(seed)
		random.shuffle(questions)
		random.seed(seed)
		random.shuffle(answers)
	
		for question in questions:
			print("What does", question, "mean?")
			guess = str(input()).lower()
		
			if guess == answers[index]:
				print("You are right!")
				index += 1
				numright += 1
			else:
				print("You are wrong. The answer is " + str(answers[index]) + "; better luck next time!")
				index +=1
		print("You got " + str(round(numright/len(questions), 2)*100) + "% (" + str(numright) + ") of the cards right.")
