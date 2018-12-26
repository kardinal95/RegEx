from queue import Queue

from py.node import Node


class FiniteStateMachine:
    states = dict()
    symbols = None
    transitions = []
    start = 0
    end = set()
    queue = Queue()

    def __init__(self, tree: Node, symbols: dict, follow_pos: dict):
        self.symbols = symbols
        self.states[0] = tree.first_pos
        self.append_to_queue(0)
        self.fill(follow_pos)
        for name, values in self.states.items():
            if list(symbols['#'])[0] in values:
                self.end.add(name)
        self.shorten()

    def fill(self, follow_pos: dict) -> None:
        index = 1
        while not self.queue.empty():
            template = self.queue.get()
            values = self.states[template[0]].intersection(self.symbols[template[1]])
            targets = set()
            for i in values:
                targets = targets.union(follow_pos[i])
            if len(targets) == 0:
                continue
            if targets in self.states.values():
                for name, values in self.states.items():
                    if values == targets:
                        self.transitions.append([template[0], template[1], name])
                        break
            else:
                self.states[index] = targets
                self.transitions.append([template[0], template[1], index])
                self.append_to_queue(index)
                index += 1

    def append_to_queue(self, state: int) -> None:
        for sym in self.symbols.keys():
            if sym == '#':
                continue
            self.queue.put((state, sym))

    def shorten(self):
        state_class = self.find_next_class()
        while state_class is not None:
            self.collapse_class(state_class)
            state_class = self.find_next_class()

    def find_next_class(self):
        for item in self.states.keys():
            state_class = [item]
            for secondary in self.states:
                if item == secondary:
                    continue
                if self.in_same_class(item, secondary):
                    state_class.append(secondary)
            if len(state_class) > 1:
                return state_class
        return None

    def in_same_class(self, state1, state2) -> bool:
        state_1_transitions = [(x[1], x[2]) for x in self.transitions if x[0] == state1]
        state_2_transitions = [(x[1], x[2]) for x in self.transitions if x[0] == state2]
        return state_1_transitions == state_2_transitions

    def restore_re(self) -> str:
        while True:
            state = self.find_deletable_state()
            if state == -1:
                break
            else:
                self.delete_state(state)
        self.shorten_similar(self.transitions)
        return self.finalize_re()

    def find_deletable_state(self) -> int:
        for state in self.states.keys():
            if state == self.start or state in self.end:
                continue
            return state
        return -1

    @staticmethod
    def shorten_similar(transitions: list) -> None:
        for transition in transitions:
            similar = [transition]
            for second in transitions:
                if transition == second:
                    continue
                if transition[0] == second[0] and transition[2] == second[2]:
                    similar.append(second)
            if len(similar) > 1:
                for item in similar:
                    transitions.remove(item)

                transitions.append([similar[0][0],
                                    '|'.join([i[1] if len(i[1]) == 1 else '({})'.format(i[1]) for i in similar]),
                                    similar[0][2]])

    def delete_state(self, state: int) -> None:
        connected = []
        for transition in self.transitions:
            if transition[0] == state or transition[2] == state:
                connected.append(transition)
        for item in connected:
            self.transitions.remove(item)
        self.states.pop(state)
        self.compensate_transitions(connected, state)

    def compensate_transitions(self, transitions: list, state: int) -> None:
        self.shorten_similar(transitions)
        cycle, starts, ends = self.split_transitions(transitions, state)
        # Fix self cycle
        if cycle is not None:
            for item in starts:
                item[1] = item[1] + '{}*'.format(cycle[1]) if len(cycle[1]) == 1 else '({})*'.format(cycle[1])
        # Now interconnect
        for first in starts:
            for second in ends:
                self.transitions.append([first[0], self.safe_connect(first[1], second[1]), second[2]])
        pass

    @staticmethod
    def safe_connect(left: str, right: str) -> str:
        if len(left) > 1:
            left = '({})'.format(left)
        if len(right) > 1:
            right = '({})'.format(right)
        return left + right

    def finalize_re(self, state=0) -> str:
        result = ''
        cycle, starts, ends = self.split_transitions(self.transitions, state)
        if cycle is not None:
            result += '{}*'.format(cycle[1]) if len(cycle[1]) == 1 else '({})*'.format(cycle[1])
        #if len(ends) == 1:
        #    result += ends[0][1]
        #    result += self.finalize_re(ends[0][2])
        if len(ends) > 0:
            result += '(E' if state in self.end else '('
            for item in ends:
                if state in self.end:
                    result += '|'
                result += item[1]
                result += self.finalize_re(item[2])
            result += ')'
        return result

    @staticmethod
    def split_transitions(transitions: list, state: int) -> (list, list, list):
        cycle = None
        starts = []
        ends = []
        for item in transitions:
            if item[2] == state:
                if item[0] == state:
                    cycle = item
                    continue
                else:
                    starts.append(item)
                    continue
            elif item[0] == state:
                ends.append(item)
                continue
        return cycle, starts, ends

    def collapse_class(self, state_class):
        remaining = state_class[0]
        for item in state_class[1:]:
            if item == self.start:
                self.start = remaining
            if item in self.end:
                self.end.add(remaining)
        for index, item in enumerate(self.transitions):
            if item[2] in state_class[1:]:
                self.transitions[index][2] = remaining
        for item in self.transitions:
            if item[0] in state_class[1:]:
                self.transitions.remove(item)
