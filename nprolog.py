import string


'''
This class organizes the facts.
'''

variables = {}

class Fact():
	def __init__(self, string):
		s = string.replace(" ", "").split('(')
		self.functor, self.args = s[0], s[1][:-1].split(',')
		self.arity = len(self.args)
		self.unknowns = len([arg for arg in self.args if arg.isupper()])

	def __str__(self):
		return self.functor + '(' +', '.join(self.args) +')'


a = Fact("dad(alice,bill)")

b = Fact("mother(mary,john)")

f = Fact("yo(george, obama)")

c = Fact("yo(jane,james)")

d = Fact("yo(jane, X)")

e = Fact("yo(Y, obama)")

facts = [a, f, b, c]


def unify(fact):
	functor = fact.functor
	args = fact.args
	unknowns = fact.unknowns

	print functor, args

	if unknowns:
		print "UNKNOWN"

		for f in facts:
			if functor == f.functor:
				print "MATCH " + functor
				#Get all known indices
				indices = [i for i, x in enumerate(args) if not x.isupper()]
				print "LENGTH: " + str(len(indices))
				for i in indices:
					if args[i]==f.args[i]:
						unknown = [i for i, x in enumerate(args) if x.isupper()]
						print args[unknown[0]] + " = " + f.args[unknown[0]]
						variables[args[unknown[0]]] = f.args[unknown[0]]

	else:
		if fact not in facts:
			return False

	print variables
	return True


