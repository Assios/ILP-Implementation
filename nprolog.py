
'''
This class organizes the facts.
'''
class Fact():
	def __init__(self, string):
		s = string.split('(')
		self.functor, self.args = s[0],s[1][:-1].split(',')
		self.relation = {}
		self.relation[self.functor] = self.args
		self.arity = len(self.args)

	def __str__(self):
		return self.functor + ': ' +', '.join(self.args)

