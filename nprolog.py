#!/usr/bin/python
# -*- coding: utf-8 -*-

import string
import re
import sys

#variables = {}


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
        self.env = {}

    def __str__(self):
        return self.functor + '(' + ', '.join(self.args) + ')'

    def __eq__(self, other):
        return (self.arity == other.arity and self.functor == other.functor)

    def __hash__(self):
        return id(self)


class Rule:

    def __init__(self, string):
        s = string.replace(' ', '').split(':-')
        self.goal = Fact(s[0])
        self.subgoals = s[1].split('),')
        self.dict = {}
        self.env = {}
        self.index = 0
        self.parent = False

        for i in range(len(self.subgoals)):
            if self.subgoals[i][-1] != ')':
                self.subgoals[i] += ')'

        self.subgoals = [Fact(subgoal) for subgoal in self.subgoals]
        
        for sub in self.subgoals:
            sub.parent = self

        self.subgoals_count = len(self.subgoals)

        self.dict[self.goal] = self.subgoals


    def __str__(self):
        return self.goal.functor + '(' + ', '.join(self.goal.args) \
            + ') :- ' + ''.join([subgoal.functor + '('
                                + ', '.join(subgoal.args) + '),'
                                for subgoal in self.subgoals])[:-1]

    def __eq__(self, other):
        if isinstance(other, Fact):
            print "fact in eq: ", other
            print "rule in eq: ", self
            return self.goal.functor == other.functor and self.goal.args == other.arity 
        return (self.goal.functor == other.goal.functor and self.goal.args == other.goal.args)


def unify(s_fact, s_env, d_fact, d_env):
    """
    Tries to unify a fact with all the facts in the database.
    Returns False if not possible.
    """


    if s_fact.args != d_fact.args or s_fact.functor != d_fact.functor: return 0

    for i in range(len(s_fact.args)):
        #if not s_fact.args[i] is a variable, it is a constant
        if s_fact.args[i].isupper():
            sval = s_env.get(s_fact.args[i])
        else:
            sval = s_fact.args[i]
        if(d_fact.args[i].isupper()): #variable in dest
            #if the variable is not set, set it from the sourceval
            if (not d_env.get(d_fact.args[i])):
                d_env[d_fact.args[i]] = sval
            else: #the variable is set, have to check if it is the same as sval
                if (d_env.get(d_fact.args[i]) != sval):
                    return 0
        elif(d_fact.args[i] != s_fact.args[i]):
            return 0
    return 1


    # functor = fact.functor
    # args = fact.args
    # unknowns = fact.unknowns
    # response = False

    #     if d_fact.functor == s_fact.functor:

    #         var = equal(d_fact.args, s_fact.args)

    #         if var:
    #             d_env.update(var)

    #             for key, value in var.iteritems():
    #                 print(key + " = " + value)

    #             response = True
    # else:
    #     if s_fact.functor == d_fact.functor and s_fact.args == d_fact.args:
    #         #update environment
    #         for arg in s_fact.args:

    #         return True

    # return response


# def search(fact):
#     """
#     If it can't unify a fact directly, derive it
#     from the rulebase.
#     """

#     if unify(fact):
#         return True
#     else:
#         for rule in rulebase:
#             if fact.functor == rule.goal.functor:
#                 for subgoal in rule.subgoals:
                    
#                     indices = []

#                     # SOME TEMPORARY DIRTY HACKS HERE TO MAKE THIS KIND OF STUFF WORK:
#                     # child(X):-mother(Y,X)

#                     for i in range(len(rule.goal.args)):
#                         try:
#                             indices.append(subgoal.args.index(rule.goal.args[i]))
#                         except:
#                             continue

#                     if indices:
#                         if indices[0]>len(fact.args)-1:
#                             fact.args.insert(0, "Y")

#                     if "Y" not in fact.args:
#                         fact.args = gen_list(fact.args, indices)

#                     print subgoal.args
#                     print fact.args

#                     if len(fact.args)!=len(subgoal.args):
#                         for element in fact.args:
#                             if element not in subgoal.args:
#                                 fact.args.remove(element)

#                     temp = Fact(subgoal.functor + '('
#                                 + ','.join(fact.args) + ')')

#                     print variables

#                     if not unify(temp):
#                         return False
#                 return True



def search(query, env={}):
    curr_rules = []
    for rule in rulebase:
        if rule.goal.functor == query.functor:
            curr_rules.append(rule)
    if not len(curr_rules):
        return False
    stack = [curr_rules.pop()]
    while stack:
        print "in while"
        rule = stack.pop()
        if(rule.index < rule.subgoals_count): #we still have more subgoals to compute
            print "more subgoals"
            r = rule.subgoals[rule.index]

            for set_rule in rulebase_facts:
                print "rule: ", set_rule
                print "r: ", r
                if set_rule == r:
                    print "set_rule == r"
                    if unify(set_rule, set_rule.env, r, r.env):
                        print "unified!!"
                        stack.append(r)
                    else:
                        print "not unified :("
                else:
                    print "set_rule != r"
        else: #subgoals finished, check if there are parents who want to join
            print "finished subgoals"
            if(rule.parent):
                print "finding parent"
                if(unify(rule, rule.env, rule.parent.subgoals[rule.parent.index], rule.parent.env)):
                    stack.append(rule.parent)
                    continue
            else:
                print "no parent"
                print rule.env
                return True





    




def gen_list(array, indices):
    new_list = []

    for i in indices:
        new_list.append(array[i])

    return new_list

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

    return match


def parse(file=sys.argv[1]):
    f = filter(lambda line: line.strip(), open(file))

    extension = file.split('.')[-1]

    if extension != 'npro':
        raise ParseError('Cannot parse .' + extension + '-files.')

    for (linenumber, line) in enumerate(f):
        line = line.replace(' ', '').strip()

        if line[-1]=='.': line=line[0:-1]

        if not line[0].islower():
            continue

        if ':-' in line:
            rulebase.append(Rule(line))
            rulebase_facts.append(Rule(line))
        else:
            rulebase_facts.append(Fact(line))
            facts.append(Fact(line))


if __name__ == '__main__':
    rulebase = []
    facts = []
    rulebase_facts = rulebase + facts
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

        print "no"
