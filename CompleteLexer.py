from Etapa2 import DFA, NFA


def regexToPrenex(regex):
    regex = regex.split(';')[0]
    regex = regex.replace("\'", '')
    regex = regex.replace("\\n", "\n")

    stacks = [[]]

    unions = [False]
    el = ""

    op = ['*', '|', '+', '(', ')']
    current_stack = 0
    current_union = 0
    i = 0
    while i < len(regex):
        if regex[i] not in op:
            if len(stacks[current_stack]) > 1:
                a = stacks[current_stack].pop()
                b = stacks[current_stack].pop()
                if unions[current_union]:
                    stacks[current_stack].append(f"UNION {b} {a}")
                    stacks[current_stack].append(regex[i])
                    unions[current_union] = False
                else:
                    stacks[current_stack].append(f"CONCAT {b} {a}")
                    stacks[current_stack].append(regex[i])
            else:
                stacks[current_stack].append(regex[i])
        else:
            if regex[i] == '*':
                a = stacks[current_stack].pop()
                stacks[current_stack].append(f"STAR {a}")
            elif regex[i] == '+':
                a = stacks[current_stack].pop()
                stacks[current_stack].append(f"PLUS {a}")
            elif regex[i] == '|':
                unions[current_union] = True
            elif regex[i] == '(':
                current_stack += 1
                current_union += 1
                stacks.append([])
                unions.append(False)
            elif regex[i] == ')':
                while (len(stacks[current_stack]) > 1):
                    a = stacks[current_stack].pop()
                    b = stacks[current_stack].pop()
                    if unions[current_union]:
                        stacks[current_stack].append(f"UNION {b} {a}")
                        unions[current_union] = False
                    else:
                        stacks[current_stack].append(f"CONCAT {b} {a}")
                stacks[current_stack -
                       1].append(stacks[current_stack].pop())
                current_stack -= 1
                current_union -= 1
        i += 1

    while (len(stacks[current_stack]) > 1):
        a = stacks[current_stack].pop()
        b = stacks[current_stack].pop()
        if unions[current_union]:
            stacks[current_stack].append(f"UNION {b} {a}")
            unions[current_union] = False
        else:
            stacks[current_stack].append(f"CONCAT {b} {a}")

    return stacks[current_stack].pop()


def nextConf(dfa, conf):
    state = conf[0]
    word = conf[1]

    if (state, word[0]) in dfa.delta:
        nextConfig = (dfa.delta[(state, word[0])], word[1:])
    else:
        nextConfig = ("-1", "Nu am gasit starea")
    return nextConfig


def longest_prefix(dfa, word):
    conf = (dfa.initialState, word)
    index = 0
    finalIndex = 0

    while conf[1] != "":

        conf = nextConf(dfa, conf)
        if conf[0] == dfa.states - 1:
            return (finalIndex, index)
        if (conf[0] == "-1"):
            return (finalIndex, index)
        index += 1
        if conf[0] in dfa.finalStates:
            finalIndex = index
    return (finalIndex, index)


def runcompletelexer(lexer, finput, foutput):
    res = []
    result = ""
    lex = ""
    with open(lexer, "rt") as f:
        lex = f.readlines()

    with open(finput) as f:
        word = "".join(f.readlines())

    dfas = []

    for l in lex:
        lSplit = l.split(' ', 1)
        prenex = regexToPrenex(lSplit[1])
        dfa = DFA(NFA(prenex))
        dfas.append(dfa)
        dfa.name = lSplit[0]

    index = 0
    lenW = len(word)
    while word:
        indexes = []
        indexes2 = []
        maximum = 0
        for dfa in dfas:
            r = longest_prefix(dfa, word)
            indexes.append(r[0])
            indexes2.append(r[1])

        if sum(indexes) == 0:
            ind = index + max(indexes2)
            if ind == lenW:
                ind = "EOF"
            result = f"No viable alternative at character {ind}, line 0\n"
            break

        maximum = max(indexes)

        res += (str(dfas[indexes.index(maximum)].name) + " " +
                "\\n".join(str(word[:maximum]).split("\n")) + "\n")
        index += maximum

        word = word[maximum:]
    if result == "":
        result = "".join(res)

    with open(foutput, "wt") as f:
        f.write(result[:-1])


def runparser(finput, foutput):
    pass
