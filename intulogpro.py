#!/usr/bin/python
# -*- coding: utf-8 -*-

import string
import re
import sys
import copy

rulebase = []


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
        self.index = 0
        self.goal = self
        self.subgoals_count = 0

    def __str__(self):
        return self.functor + '(' + ', '.join(self.args) + ')'

    def __eq__(self, other):
        return self.arity == other.arity and self.functor \
            == other.functor

    def __hash__(self):
        return id(self)


class Hypo:

    def __init__(self, string):

        self.string = string

        fields = [f.replace(':-', '').strip() for f in string.split('=>'
                  )]

        self.hypo = fields[1]

        self.head = fields[0]

        self.hypo = self.hypo.split('),')

        self.pregoal = (self.hypo[0])[1:] + ')'.strip()

        self.rule = Rule(self.hypo[1].replace('))', ')').strip())

    def __str__(self):
        return 'Head: ' + self.head + ' Pregoal: ' + self.pregoal \
            + ' Rule: ' + str(self.rule)


class Rule:

    def __init__(
        self,
        string,
        parent=None,
        env={},
        ):

        s = string.replace(' ', '').split(':-')
        self.goal = Fact(s[0])
        self.subgoals = []
        if len(s) > 1:
            self.subgoals = s[1].split('),')
        self.dict = {}
        self.env = {}
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
            print 'fact in eq: ', other
            print 'rule in eq: ', self
            return self.goal.functor == other.functor \
                and self.goal.args == other.arity
        if not isinstance(other, Hypo):
            return self.goal.functor == other.goal.functor \
                and self.goal.args == other.goal.args


class Toprule:

    def __init__(
        self,
        rule,
        parent=None,
        env={},
        ):

        self.rule = rule
        self.parent = parent
        self.env = copy.deepcopy(env)
        self.index = 0


def unify(
    s_fact,
    s_env,
    d_fact,
    d_env,
    ):
    """
    Tries to unify two facts with their corresponding environment.
    Returns False if not possible.
    """

    if len(s_fact.args) != len(d_fact.args) or s_fact.functor \
        != d_fact.functor:
        return True

    for i in range(len(s_fact.args)):

        # if not s_fact.args[i] is a variable, it is a constant

        if s_fact.args[i].isupper():
            sval = s_env.get(s_fact.args[i])
        else:
            sval = s_fact.args[i]
        if sval:
            if d_fact.args[i].isupper():  # variable in dest

                # if the variable is not set, set it from the sourceval

                if not d_env.get(d_fact.args[i]):
                    d_env[d_fact.args[i]] = sval
                else:

                      # the variable is set, have to check if it is the same as sval

                    if d_env.get(d_fact.args[i]) != sval:
                        return True
            elif d_fact.args[i] != sval:
                return False

    return True


def search(fact, rulebase, added_rule=None):

    toprule = Toprule(Rule('a(b):-c(d)'))
    toprule.rule.subgoals = [fact]
    stack = [toprule]
    while stack:
        current_rule = stack.pop()
        if current_rule.index >= len(current_rule.rule.subgoals):
            if current_rule.parent == None:
                if current_rule.env:
                    for (key, value) in current_rule.env.iteritems():
                        print key + ' = ' + value
                else:
                    print 'yes'
                continue
            parent = copy.deepcopy(current_rule.parent)
            unify(current_rule.rule.goal, current_rule.env,
                  parent.rule.subgoals[parent.index], parent.env)
            parent.index += 1
            stack.append(parent)
            continue

        fact = current_rule.rule.subgoals[current_rule.index]
        for rule in rulebase:
            if not isinstance(rule, Hypo):
                if rule.goal.functor != fact.functor:
                    continue
                if len(rule.goal.args) != len(fact.args):
                    continue
                child = Toprule(rule, current_rule)
                if unify(fact, current_rule.env, rule.goal, child.env):
                    stack.append(child)
    if added_rule:
        rulebase.remove(added_rule)


def replace_char(string, chars):
    '''
    "hello", {"l": "a"} returns "heaao".
    Useful for swapping variables.
    '''

    for k in chars:
        string = re.sub(k, chars[k], string)
    return string


def hypo_search(query):

    fields = [f.replace(':-', '').strip() for f in query.split('=>')]

    (goal, hypo) = (fields[0], fields[1])

    hypo = hypo.split('),')

    pregoal = (hypo[0])[1:] + ')'.strip()

    rule = Rule(hypo[1].replace('))', ')').strip())

    rulebase.append(rule)

    search(Fact(pregoal), rulebase, rule)


def parse(file=sys.argv[1]):
    f = filter(lambda line: line.strip(), open(file))

    extension = file.split('.')[-1]

    if extension != 'ilp':
        raise ParseError('Cannot parse .' + extension + '-files.')

    for (linenumber, line) in enumerate(f):
        line = line.replace(' ', '').strip()

        if line[-1] == '.':
            line = line[0:-1]

        if not line[0].islower():
            continue

        if '=>' in line:
            rulebase.append(Hypo(line))
        else:
            rulebase.append(Rule(line))


if __name__ == '__main__':

    rulebase = []
    parse()

    print '\n'
    while True:

        prompt = raw_input('Query: ')

        for rule in rulebase:
            if isinstance(rule, Hypo):
                line = rule.string

                p = prompt.split('(')[0]

                if p == rule.head.split('(')[0]:

                    args = [i.strip() for i in prompt.split('('
                            )[1].split(')')[0].split(',')]

                    original_args = [i.strip() for i in
                            rule.head.split('(')[1].split(')'
                            )[0].split(',')]

                    mapping = {}

                    for i in range(len(original_args)):
                        mapping[original_args[i]] = args[i]

                    line = replace_char(line, mapping)

                    if hypo_search(line):
                        continue
        else:
            search(Fact(prompt), rulebase)
