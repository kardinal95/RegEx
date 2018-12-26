from py.node import Node
from py.spec import specials


class RegexParser:
    def __init__(self, regex: str):
        self.regex = regex
        self.positions = self.fill_positions()
        self.tree = Node(regex, self.positions)

    def fill_positions(self) -> dict:
        result = dict()
        counter = 1
        for index, symbol in enumerate(self.regex):
            if symbol not in specials:
                result[index] = counter
                counter += 1
        return result
