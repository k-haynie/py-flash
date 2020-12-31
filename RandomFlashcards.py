import csv
import random
#import practice_interface
def shuffleExec(parent, filename):
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
			parent.printText("What does " + question + " mean?")
			#print("What does", question, "mean?")
			guess = parent.lineEdit.returnPressed.connect(parent.acceptText)

			if guess == answers[index]:
				print("You are right!")
				index += 1
				numright += 1
			else:
				print("You are wrong. The answer is " + str(answers[index]) + "; better luck next time!")
				index += 1
		print("You got " + str(round(numright/len(questions), 2)*100) + "% (" + str(numright) + ") of the cards right.")

#shuffleExec("Decks/Animals.csv")