#!/usr/bin/python
# -*- coding: utf-8 -*-

import string
import re
import sys

variables = {}


class ParseError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


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
            if self.subgoals[i][-1] != ')':
                self.subgoals[i] += ')'

        self.subgoals = [Fact(subgoal) for subgoal in self.subgoals]

        self.subgoals_count = len(self.subgoals)

        self.dict[self.goal] = self.subgoals

    def __str__(self):
        return self.goal.functor + '(' + ', '.join(self.goal.args) \
            + ') :- ' + ''.join([subgoal.functor + '('
                                + ', '.join(subgoal.args) + '),'
                                for subgoal in self.subgoals])[:-1]


def unify(fact):
    """
    Tries to unify a fact with all the facts in the database.
    Returns False if not possible.
    """

    functor = fact.functor
    args = fact.args
    unknowns = fact.unknowns
    response = False
    global question
    question = False

    if unknowns:

        for f in facts:
            if functor == f.functor:

                var = equal(args, f.args)
                if var:
                    variables.update(var)
                    response = True
    else:

        for f in facts:
            if f.functor == fact.functor and f.args == fact.args:
                question = True
                return True

    return response


def search(fact):
    """
    If it can't unify a fact directly, derive it
    from the rulebase.
    """

    if unify(fact):
        return True
    else:
        for rule in rulebase:
            if fact.functor == rule.goal.functor:
                for subgoal in rule.subgoals:

                    if not subgoal.arity == fact.arity:
                        return False

                    fact.args = [fact.args[i] for i in
                                 [subgoal.args.index(rule.goal.args[i])
                                 for i in range(len(rule.goal.args))]]

                    temp = Fact(subgoal.functor + '('
                                + ','.join(fact.args) + ')')

                    if unify(temp):
                        return True


def equal(arr1, arr2):
    """
    Checks if all lowercase elements in the two lists are equal.
    If they are, return a dictionary that maps the uppercase variables
    in arr1 to the corresponding variable in arr2.
    """

    if len(arr1) != len(arr2):
        return False

    match = {}

    for i in range(len(arr1)):
        if arr1[i].islower() and arr1[i] != arr2[i]:
            return False
        if arr1[i].isupper():
            match[arr1[i]] = arr2[i]
            print arr1[i] + ' = ' + arr2[i]

    return match


def parse(file=sys.argv[1]):
    f = filter(lambda line: line.strip(), open(file))

    extension = file.split('.')[-1]

    if extension != 'npro':
        raise ParseError('Cannot parse .' + extension + '-files.')

    for (linenumber, line) in enumerate(f):
        line = line.replace(' ', '').strip()

        if not line[0].islower():
            continue

        if ':-' in line:
            rulebase.append(Rule(line))
        else:
            facts.append(Fact(line))


if __name__ == '__main__':
    rulebase = []
    facts = []
    parse()

    print 'Rules:'
    for rule in rulebase:
        print rule
    print '\nFacts:'
    for fact in facts:
        print fact

    print '\n'
    while True:

        prompt = Fact(raw_input('? '))

        if search(prompt):
            print "yes"
            continue

        if question:
            continue

        print "no"
