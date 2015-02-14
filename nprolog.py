#!/usr/bin/python
# -*- coding: utf-8 -*-

import string

variables = {}


class Fact:

    def __init__(self, string):
        s = string.replace(' ', '').split('(')
        (self.functor, self.args) = (s[0], (s[1])[:-1].split(','))
        self.arity = len(self.args)
        self.unknowns = len([arg for arg in self.args if arg.isupper()])

    def __str__(self):
        return self.functor + '(' + ', '.join(self.args) + ')'


class Rule:

	def __init__(self, string):
		s = string.replace(' ', '').split(':-')
		self.goal = Fact(s[0])
		self.subgoals = s[1].split('),')
		self.dict = {}

		for i in range(len(self.subgoals)):
			if self.subgoals[i][-1]!=')':
				self.subgoals[i]+=')'

		self.subgoals = [Fact(subgoal) for subgoal in self.subgoals]

		self.dict[self.goal] = self.subgoals

	def __str__(self):
		return self.goal.functor + '(' + ', '.join(self.goal.args) + ') :- ' + \
		''.join([subgoal.functor + '(' + ', '.join(subgoal.args) + \
		'),' for subgoal in self.subgoals])[:-1]

############################################
#####      TESTING TERMS        ############

rule1 = Rule('mortal(X):-human(X)')

cat = Fact('katt(tom)')

a = Fact('dad(alice,bill)')

b = Fact('mother(mary,john)')

f = Fact('yo(yomaaan, obama)')

c = Fact('yo(jane,james, johnny)')

e = Fact('yo(jane,peter, johnny)')

d = Fact('yo(jane, X, Y)')

fail = Fact('yo(Y, X, bill)')

fail2 = Fact('dad(billyyy,johhny)')

sokrates = Fact('human(sokrates)')

facts = [a, f, b, c, cat, sokrates]

rules = [rule1]

sokr = Fact("mortal(sokrates)")


#############################################


def unify(fact):
    functor = fact.functor
    args = fact.args
    unknowns = fact.unknowns
    response = False

    if unknowns:

        for f in facts:
            if functor == f.functor:

                var = equal(args, f.args)
                if var:
                    variables.update(var)
                    response = True
    else:
        if fact in facts:
            return True

    return response


def search(fact):
	if unify(fact):
		return True
	else:
		for rule in rules:
			if fact.functor==rule.goal.functor:
				for subgoal in rule.subgoals:
					print subgoal
					print subgoal.functor+'('+fact.args[0]+')'
					temp = Fact(subgoal.functor+'('+fact.args[0]+')')
					print temp
					print sokrates
					if unify(temp):
						return True


'''
Checks if two arrays are equal if we ignore uppercase characters.
If they are, all uppercase-lowercase pairs are returned.

'''

def equal(arr1, arr2):

    if len(arr1) != len(arr2):
        return False

    match = {}

    for i in range(len(arr1)):
        if arr1[i].islower() and arr1[i] != arr2[i]:
            return False
        if arr1[i].isupper():
            match[arr1[i]] = arr2[i]

    return match


def print_vars():
	print variables
