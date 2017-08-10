class IncrementalBar:
	def __init__(self, max = 100):
		self.max = max;
		self.index = 0;
	def start(self): pass
	def update(self):
		print("On action " + str(self.index) + "/" + str(self.max))
	@staticmethod
	def finish():
		print("Done")