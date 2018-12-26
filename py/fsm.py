from queue import Queue

from py.node import Node


class FiniteStateMachine:
    states = dict()
    symbols = None
    transitions = []
    queue = Queue()

    def __init__(self, tree: Node, symbols: dict, follow_pos: dict):
        self.symbols = symbols
        self.states[0] = tree.first_pos
        self.append_to_queue(0)
        self.fill(follow_pos)

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
                self.transitions.append([template[0], template[1], str(index)])
                self.append_to_queue(index)
                index += 1

    def append_to_queue(self, state: int) -> None:
        for sym in self.symbols.keys():
            if sym == '#':
                continue
            self.queue.put((state, sym))
