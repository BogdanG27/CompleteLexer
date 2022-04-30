# requires at least python 3.6 for f-strings

from sys import argv, settrace
from collections import defaultdict
import sys


class miniNFA():
    def __init__(self):
        self.initialState = 0
        self.finalState = 0
        self.delta = defaultdict(set)


class Regex:
    def __init__(self, prenexForm):
        self.prenex = prenexForm


class Lexem(Regex):
    def __init__(self, lexem):
        # super().__init__(prenexForm)
        self.lexem = lexem
        self.nfa = miniNFA()

    def __str__(self) -> str:
        return self.lexem


class Star(Regex):
    def __init__(self, lexem):
        # super().__init__(prenexForm)
        self.lexem = lexem
        self.nfa = miniNFA()

    def __str__(self):
        return f"STAR({str(self.lexem)})"


class Union(Regex):
    def __init__(self, lexem1, lexem2):
        self.lexem1 = lexem1
        self.lexem2 = lexem2
        self.nfa = miniNFA()

    def __str__(self) -> str:
        return f"UNION({str(self.lexem1)}, {str(self.lexem2)})"


class Concat(Regex):
    def __init__(self, lexem1, lexem2):
        self.lexem1 = lexem1
        self.lexem2 = lexem2
        self.nfa = miniNFA()

    def __str__(self) -> str:
        return f"CONCAT({str(self.lexem1)}, {str(self.lexem2)})"


class Plus(Regex):
    def __init__(self, lexem):
        self.lexem = lexem
        self.nfa = miniNFA()

    def __str__(self) -> str:
        return f"PLUS({str(self.lexem)})"


class NFA():
    def __init__(self, prenexForm):
        splited = [' ']
        if prenexForm != ' ':
            prenexForm = prenexForm.replace('  ', ' &')
            splited = prenexForm.split(' ')
            splited = [a if a != '&' else ' ' for a in splited]

        op = ["STAR", "CONCAT", "UNION", "PLUS"]
        stack = []
        i = 0
        # print(f":{prenexForm}:")

        self.alphabet = []

        curerentStateCount = 0

        for el in splited:
            #print(f"elem: {el}")
            if el in op:
                stack.append(el)
            else:
                lex = Lexem(el)
                self.alphabet.append(el)
                lex.nfa.initialState = curerentStateCount
                curerentStateCount += 1
                lex.nfa.finalState = curerentStateCount
                curerentStateCount += 1
                lex.nfa.delta[(lex.nfa.initialState, el)
                              ].add(lex.nfa.finalState)
                stack.append(lex)
                # print(stack)

                while (len(stack) > 1):
                    if stack[-2] == "STAR":
                        stack.pop(-2)
                        lexem = stack.pop()
                        star = Star(lexem)
                        for key in lexem.nfa.delta:
                            for value in lexem.nfa.delta[key]:
                                star.nfa.delta[key].add(value)

                        newInitialState = curerentStateCount
                        curerentStateCount += 1
                        newFinalState = curerentStateCount
                        curerentStateCount += 1

                        # conectare noua stare initiala cu veche stare initiala
                        star.nfa.delta[(newInitialState, 'E')].add(
                            lexem.nfa.initialState)

                        # conectare veche stare finala cu noua stare finala
                        star.nfa.delta[(lexem.nfa.finalState, 'E')].add(
                            newFinalState)

                        # conectare noua stare initiala cu noua stare finala
                        star.nfa.delta[(newInitialState, 'E')].add(
                            newFinalState)

                        # conectare veche stare finala cu vechea stare initiala
                        star.nfa.delta[(lexem.nfa.finalState, 'E')].add(
                            lexem.nfa.initialState)

                        star.nfa.initialState = newInitialState
                        star.nfa.finalState = newFinalState

                        stack.append(star)
                    elif stack[-2] == "PLUS":
                        stack.pop(-2)
                        lexem = stack.pop()
                        plus = Plus(lexem)
                        for key in lexem.nfa.delta:
                            for value in lexem.nfa.delta[key]:
                                plus.nfa.delta[key].add(value)

                        newInitialState = curerentStateCount
                        curerentStateCount += 1
                        newFinalState = curerentStateCount
                        curerentStateCount += 1

                        # conectare noua stare initiala cu veche stare initiala
                        plus.nfa.delta[(newInitialState, 'E')].add(
                            lexem.nfa.initialState)

                        # conectare veche stare finala cu noua stare finala
                        plus.nfa.delta[(lexem.nfa.finalState, 'E')].add(
                            newFinalState)

                        # conectare veche stare finala cu vechea stare initiala
                        plus.nfa.delta[(lexem.nfa.finalState, 'E')].add(
                            lexem.nfa.initialState)

                        plus.nfa.initialState = newInitialState
                        plus.nfa.finalState = newFinalState

                        stack.append(plus)
                    elif isinstance(stack[-2], Regex) and stack[-3] == "UNION":
                        stack.pop(-3)
                        lexem1 = stack.pop(-2)
                        lexem2 = stack.pop(-1)
                        union = Union(lexem1, lexem2)
                        for key in lexem1.nfa.delta:
                            for value in lexem1.nfa.delta[key]:
                                union.nfa.delta[key].add(value)

                        for key in lexem2.nfa.delta:
                            for value in lexem2.nfa.delta[key]:
                                union.nfa.delta[key].add(value)

                        newInitialState = curerentStateCount
                        curerentStateCount += 1
                        newFinalState = curerentStateCount
                        curerentStateCount += 1

                        # conectare noua stare initiala cu primul automat
                        union.nfa.delta[(newInitialState, 'E')
                                        ].add(lexem1.nfa.initialState)

                        # conectare noua stare initiala cu al doilea automat
                        union.nfa.delta[(newInitialState, 'E')
                                        ].add(lexem2.nfa.initialState)

                        # conectare primul automat cu noua stare finala
                        union.nfa.delta[(lexem1.nfa.finalState, 'E')
                                        ].add(newFinalState)

                        # conectare al doilea automat cu noua stare finala
                        union.nfa.delta[(lexem2.nfa.finalState, 'E')
                                        ].add(newFinalState)

                        union.nfa.initialState = newInitialState
                        union.nfa.finalState = newFinalState
                        stack.append(union)
                    elif isinstance(stack[-2], Regex) and stack[-3] == "CONCAT":
                        stack.pop(-3)
                        lexem1 = stack.pop(-2)
                        lexem2 = stack.pop(-1)
                        concat = Concat(lexem1, lexem2)
                        for key in lexem1.nfa.delta:
                            for value in lexem1.nfa.delta[key]:
                                concat.nfa.delta[key].add(value)

                        for key in lexem2.nfa.delta:
                            for value in lexem2.nfa.delta[key]:
                                concat.nfa.delta[key].add(value)

                        concat.nfa.delta[(lexem1.nfa.finalState, 'E')
                                         ].add(lexem2.nfa.initialState)
                        concat.nfa.initialState = lexem1.nfa.initialState
                        concat.nfa.finalState = lexem2.nfa.finalState
                        stack.append(concat)
                    else:
                        break
        # print(stack)
        self.initialState = stack[0].nfa.initialState
        self.finalState = stack[0].nfa.finalState
        self.delta = stack[0].nfa.delta
        self.states = curerentStateCount
        self.alphabet.sort()

        # #print(self.initialState)
        # #print(self.finalState)
        # #print(self.delta)


class DFA():
    def __init__(self, nfa):
        epsilonClosures = {}
        self.alphabet = nfa.alphabet
        self.delta = {}
        self.states = 0
        self.finalStates = []
        self.name = ""

        for i in range(0, nfa.states):
            visited = [i]
            for stateVisited in visited:
                if (stateVisited, 'E') in nfa.delta:
                    for value in nfa.delta[(stateVisited, 'E')]:
                        if value not in visited:
                            visited.append(value)
            epsilonClosures[i] = tuple(visited)
        # #print(epsilonClosures)

        queue = [epsilonClosures[nfa.initialState]]

        mapStates = {}  # maps a new state to a group of states from nfa
        # (group of states: state)

        mapStates[epsilonClosures[nfa.initialState]] = 0
        currentState = 1
        visited = []  # for a group of states visited

        while queue != []:
            currentStates = queue.pop()
            for symbol in self.alphabet:
                statesNext = []
                for state in currentStates:
                    if (state, symbol) in nfa.delta:
                        for value in nfa.delta[(state, symbol)]:
                            if value not in statesNext:
                                statesNext.append(value)
                        for stateNext in statesNext:
                            for value in epsilonClosures[stateNext]:
                                if value not in statesNext:
                                    statesNext.append(value)
                statesNext = tuple(statesNext)
                if statesNext != ():
                    if statesNext not in mapStates:
                        mapStates[statesNext] = currentState
                        currentState += 1
                        queue.append(statesNext)
                        self.delta[(mapStates[currentStates], symbol)
                                   ] = mapStates[statesNext]
                    else:
                        self.delta[(mapStates[currentStates], symbol)
                                   ] = mapStates[statesNext]

        self.states = currentState + 1
        sinkState = currentState
        for state in range(0, currentState + 1):
            for symbol in self.alphabet:
                if (state, symbol) not in self.delta:
                    self.delta[(state, symbol)] = sinkState

        for group in mapStates:
            if nfa.finalState in group:
                self.finalStates.append(mapStates[group])

        self.initialState = 0


def statesToString(states):
    s = ""
    for state in states:
        s += str(state) + " "

    return s[:-1]


def transitionsToString(states, alphabet, delta):
    s = ""
    for state in range(0, states):
        for symbol in alphabet:
            s += f"{state},'{symbol}',{delta[(state, symbol)]}\n"
    return s[:-1]


def main():
    args = sys.argv
    inFile = args[1]
    outFile = args[2]

    input = open(inFile, "rt")
    output = open(outFile, "wt")
    expr = input.readline()

    dfa = DFA(NFA(expr))

    alph = "".join(dfa.alphabet)
    output.write(f"{alph}\n")
    output.write(f"{dfa.states}\n")
    output.write(f"{dfa.initialState}\n")
    output.write(f"{statesToString(dfa.finalStates)}\n")
    output.write(f"{transitionsToString(dfa.states, dfa.alphabet, dfa.delta)}")


if __name__ == '__main__':
    main()
