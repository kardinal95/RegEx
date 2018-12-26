from copy import copy

from py.spec import specials, priorities


class Node:
    value = None
    left = None
    right = None
    nullable = None
    first_pos = None
    last_pos = None

    def __init__(self, regex: str, positions: dict, shift=0):
        if regex[0] == '(' and regex[-1] == ')':
            regex = regex[1:-1]
            shift += 1

        position = shift
        if len(regex) == 1:
            if regex in specials:
                raise Exception('Special symbol cannot be an endpoint!')
            self.value = regex
            self.left = None
            self.right = None
        else:
            split = self.find_current_position(regex)
            position += split
            self.value = regex[split]
            if self.value == '*':
                self.right = Node(regex[:split], positions, shift)
            else:
                self.left = Node(regex[:split], positions, shift)
                self.right = Node(regex[split+1:], positions, shift+split+1)
        self.nullable = self.get_nullable()
        self.first_pos = self.get_first_post(positions, position)
        self.last_pos = self.get_last_post(positions, position)

    @staticmethod
    def find_current_position(regex: str) -> int:
        level = 0
        result = 0
        priority = 5
        for index, symbol in enumerate(regex):
            if symbol == '(':
                level += 1
                continue
            if symbol == ')':
                level -= 1
                continue
            if symbol in specials and level == 0 and priorities[symbol] <= priority:
                result = index
                priority = priorities[symbol]
        return result

    def get_nullable(self) -> bool:
        nullable = None
        if self.value not in specials:
            nullable = True if self.value == 'E' else False
        else:
            if self.value == '|':
                nullable = self.left.nullable or self.right.nullable
            elif self.value == '.':
                nullable = self.left.nullable and self.right.nullable
            elif self.value == '*':
                nullable = True
        return nullable

    def get_first_post(self, positions: dict, position: int) -> set:
        result = set()
        if self.value not in specials and self.value != 'E':
            result.add(positions[position])
        else:
            if self.value == '|':
                result = self.left.first_pos.union(self.right.first_pos)
            elif self.value == '.':
                result = copy(self.left.first_pos)
                if self.left.nullable:
                    result = result.union(self.right.first_pos)
            elif self.value == '*':
                result = copy(self.right.first_pos)
        return result

    def get_last_post(self, positions: dict, position: int) -> set:
        result = set()
        if self.value not in specials and self.value != 'E':
            result.add(positions[position])
        else:
            if self.value == '|':
                result = self.left.last_pos.union(self.right.last_pos)
            elif self.value == '.':
                result = copy(self.right.last_pos)
                if self.right.nullable:
                    result = result.union(self.left.last_pos)
            elif self.value == '*':
                result = copy(self.right.last_pos)
        return result
