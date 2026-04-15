import io

from .structure import *

class Linter:
	def __init__(self, text):
		self.text = text
		self.pointer = 0
		self.structure = Structure()
	def run(self):
		self.preprocess()
		return self.text
	def preprocess(self):
		processed = ""
		in_string = False
		in_comment = False
		for line in self.text.split("\n"):
			line = line.strip()
			for i in range(len(line)):
				if line[i] == "\"" and not in_comment:
					in_string = not in_string
				if line[i] == "#" and not in_string:
					in_comment = True
				if in_comment and i+1 == len(line) and line[i] == "\\":
					break
				if not in_comment:
					processed += line[i]
			else:
				continue
			in_comment = False
		processed = processed.replace("\n", " ")
		processed = processed.replace("\t", " ")
		while processed.find("  ") != -1:
			processed = processed.replace("  ", " ")
		self.text = processed
				



def load(file: io.TextIOWrapper):
	data = file.read()
	linter = Linter(data)
	struct = linter.run()
	return struct