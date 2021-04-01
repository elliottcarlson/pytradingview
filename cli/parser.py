from pyparsing import alphanums, printables, LineEnd, Literal, OneOrMore, Optional, Suppress, Word, WordEnd

class Parser:
    def __init__(self, command_prefix='!'):
        prefix = Suppress(Literal(command_prefix))
        eoc = WordEnd() | LineEnd()
        command = prefix + Word(alphanums) + eoc
        parameter = Word(printables)
        parameters = Optional(OneOrMore(parameter))
        command = command + parameters

        self.EBNF = command

    def parse(self, line):
        try:
            parsed = self.EBNF.parseString(line)
            return parsed.asList()
        except:
            return
