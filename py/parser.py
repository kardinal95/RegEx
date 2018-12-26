from py.fsm import FiniteStateMachine
from py.node import Node
from py.spec import specials


class RegexParser:
    def __init__(self, regex: str):
        self.regex = regex
        self.positions, self.symbols = self.fill_positions()
        self.tree = Node(regex, self.positions)
        self.follow_pos = self.get_follow_pos()
        self.fsm = FiniteStateMachine(self.tree, self.symbols, self.follow_pos)

    def fill_positions(self) -> (dict, dict):
        result = dict()
        symbols = dict()
        counter = 1
        for index, symbol in enumerate(self.regex):
            if symbol not in specials:
                result[index] = counter
                if symbol not in symbols.keys():
                    symbols[symbol] = set()
                symbols[symbol].add(counter)
                counter += 1
        return result, symbols

    def get_follow_pos(self) -> dict:
        follow_pos = dict()
        for index in self.positions.values():
            follow_pos[index] = set()
        self.add_follow(self.tree, follow_pos)
        return follow_pos

    def add_follow(self, node, follow_pos) -> None:
        if node is None:
            return
        if node.value == '.':
            for index in node.left.last_pos:
                follow_pos[index] = follow_pos[index].union(node.right.first_pos)
        elif node.value == '*':
            for index in node.right.last_pos:
                follow_pos[index] = follow_pos[index].union(node.right.first_pos)
        self.add_follow(node.left, follow_pos)
        self.add_follow(node.right, follow_pos)