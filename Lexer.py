from typing import final
import os


class Dfa:
    def __init__(self, str):
        strSp = str.split('\n')

        self.initialState = strSp[2]
        self.alphabet = []
        self.name = strSp[1]
        self.delta = {}
        self.revDelta = {}
        self.states = []

        for i in range(3, len(strSp) - 1):
            elemSp = strSp[i].split(',')
            self.states.append(elemSp[0])
            self.states.append(elemSp[2])
            if (elemSp[0] not in self.delta):
                self.delta[elemSp[0]] = [(elemSp[1][1:-1], elemSp[2])]
            else:
                self.delta[elemSp[0]].append((elemSp[1][1:-1], elemSp[2]))
            if (elemSp[2] not in self.revDelta):
                self.revDelta[elemSp[2]] = [(elemSp[1][1:-1], elemSp[0])]
            else:
                self.revDelta[elemSp[2]].append((elemSp[1][1:-1], elemSp[0]))
            self.alphabet.append(elemSp[1][1:-1])

        self.alphabet = set(self.alphabet)
        self.finalStates = strSp[-1].split(' ')
        self.states = list(set(self.states))

    def nextConf(self, conf):
        state = conf[0]
        word = conf[1]

        if state in self.delta:
            found = False
            for entry in self.delta[state]:

                if entry[0] == word[0] or (word[0] == '\n' and entry[0] == '\\n'):
                    nextConfig = (entry[1], word[1:])
                    found = True
            if not found:
                nextConfig = ("-1", "Nu merge tranzitia")

        else:
            nextConfig = ("-1", "Nu am gasit starea")
        return nextConfig

    def removeSinkStates(self):
        queue = []
        visited = []

        for state in self.finalStates:
            queue.append(state)
            visited.append(state)

        while queue:
            el = queue.pop()

            if el in self.revDelta:
                for el2 in self.revDelta[el]:
                    if el2[1] not in visited:
                        visited.append(el2[1])
                        queue.append(el2[1])

        for state in self.states:
            if state not in visited:
                del self.revDelta[state]

        delta = {}
        for el in self.revDelta:
            for el2 in self.revDelta[el]:
                if el2[1] not in delta:
                    delta[el2[1]] = [(el2[0], el)]
                else:
                    delta[el2[1]].append((el2[0], el))

        self.delta = delta

    def longest_prefix(self, word):
        conf = (self.initialState, word)
        index = 0
        finalIndex = 0

        while conf[1] != "":
            conf = self.nextConf(conf)
            if (conf[0] == "-1"):
                return (finalIndex, index)
            index += 1
            if conf[0] in self.finalStates:
                finalIndex = index
        return (finalIndex, index)


class Lexer:
    def __init__(self, components):
        self.components = components


def runlexer(Lexer, finput, foutput):
    res = []
    result = ""

    with open(finput) as f:
        word = "".join(f.readlines())

    help = ""
    with open(Lexer) as f:
        help = "".join(f.readlines())

    help = help.split(2 * os.linesep)

    dfas = []
    for el in help:
        dfa = Dfa(el)
        dfa.removeSinkStates()
        dfas.append(dfa)
        print(dfa.delta)

    index = 0
    lenW = len(word)
    while word:
        indexes = []
        indexes2 = []
        maximum = 0
        for dfa in dfas:
            r = dfa.longest_prefix(word)
            indexes.append(r[0])
            indexes2.append(r[1])

        if sum(indexes) == 0:
            ind = index + max(indexes2)
            if ind == lenW:
                ind = "EOF"
            result = f"No viable alternative at character {ind}, line 0"
            break

        maximum = max(indexes)

        res += (str(dfas[indexes.index(maximum)].name) + " " +
                "\\n".join(str(word[:maximum]).split("\n")) + "\n")
        index += maximum

        word = word[maximum:]
    if result == "":
        result = "".join(res)
    with open(foutput, "wt") as f:
        f.write(result)
