from queue import Queue

from py.node import Node


class FiniteStateMachine:
    states = dict()
    transitions = []
    start = 0
    end = set()
    queue = Queue()

    def __init__(self, tree: Node, symbols: dict, follow_pos: dict):
        # Создаем стартовое состояние из корня дерева
        self.states[0] = tree.first_pos
        # Заполняем по алгоритму
        self.fill(follow_pos, symbols)
        # Все состояния с индексом конечного символа - конечные состояния
        for name, values in self.states.items():
            if list(symbols['#'])[0] in values:
                self.end.add(name)
        # Сокращаем по классам
        self.shorten()

    """
    Добавление всех возможных переходов для данного состояния в очередь
    """

    def append_to_queue(self, state: int, symbols: dict) -> None:
        for sym in symbols.keys():
            # Переходы по символу окончания не существуют
            if sym == '#':
                continue
            self.queue.put((state, sym))

    """
    Заполнение автомата состояниями и переходами из исходного дерева РВ
    """

    def fill(self, follow_pos: dict, symbols: dict) -> None:
        # Добавляем все потенциальные переходы из стартового состояния в очередь
        self.append_to_queue(0, symbols)
        # Следующий доступный индекс для создания состояния
        index = 1
        while not self.queue.empty():
            job = self.queue.get()
            # Получаем пересечение для псевдо-позиций состояния и позиций по символу
            values = self.states[job[0]].intersection(symbols[job[1]])
            # Псевдо-позиции перехода из состояния по символу
            targets = set()
            # Закидываем все позции перехода для пересечения
            for i in values:
                targets = targets.union(follow_pos[i])
            # Нет конечных переходов - нет состояния
            if len(targets) == 0:
                continue
            # Добавляем переход в уже существующее состояние если возможно
            if targets in self.states.values():
                for name, values in self.states.items():
                    if values == targets:
                        self.transitions.append(Transition(job[0], job[1], name))
                        break
            # Создаем новый при необходимости
            else:
                self.states[index] = targets
                self.transitions.append(Transition(job[0], job[1], index))
                # Добавляем потенциальные переходы для нового состояния
                self.append_to_queue(index, symbols)
                # Смещаем индекс свободного места для состояния
                index += 1

    """
    Сокращение автомата по классам
    """

    def shorten(self):
        state_class = self.find_next_class()
        while state_class is not None:
            # Пока находятся классы - сокращаем каждый и переносим соответствующие переходы
            self.collapse_class(state_class)
            state_class = self.find_next_class()

    """
    Класс - состояния, у которых исходящие переходы совпадают (приводят к одинаковому состоянию)
    """

    def find_next_class(self) -> list or None:
        for item in self.states.keys():
            state_class = [item]
            for secondary in self.states:
                if item == secondary:
                    continue
                if self.in_same_class(item, secondary):
                    state_class.append(secondary)
            # Работаем с классами содержащими хотя бы 2 элемента
            if len(state_class) > 1:
                return state_class
        return None

    def in_same_class(self, state1: int, state2: int) -> bool:
        state_1_transitions = [(x.by, x.to_state) for x in self.transitions if x.from_state == state1]
        state_2_transitions = [(x.by, x.to_state) for x in self.transitions if x.from_state == state2]
        return state_1_transitions == state_2_transitions

    """
    Сокращает класс эквивалентности
    """

    def collapse_class(self, state_class: list) -> None:
        # Оставляем первое состояние и удаляем остальные
        remaining = state_class[0]
        # Корректируем начальное и конечные состояния
        for item in state_class[1:]:
            if item == self.start:
                self.start = remaining
            if item in self.end:
                self.end.add(remaining)
        # Переносим конечные точки переходов
        for index, item in enumerate(self.transitions):
            if item.to_state in state_class[1:]:
                self.transitions[index].to_state = remaining
        # Удаляем все ненужные переходы
        for item in self.transitions:
            if item.from_state in state_class[1:]:
                self.transitions.remove(item)
        for state in state_class[1:]:
            self.states.pop(state)

    """
    Восстановление РВ из ДКА
    """

    def restore_re(self) -> str:
        # Последовательно удаляем состояния не явл. конечными и начальным
        while True:
            state = self.find_deletable_state()
            if state == -1:
                break
            else:
                self.delete_state(state)
        # Сокращаем оставшиеся
        self.shorten_similar(self.transitions)
        # Разбираемся с начальным и конечными состояниями
        return self.finalize_re()

    def find_deletable_state(self) -> int:
        available = [x for x in self.states.keys() if x not in self.end and x != self.start]
        if len(available) == 0:
            return -1
        filtered = [x for x in self.transitions if x.from_state != x.to_state]
        available.sort(key=lambda x: len([y for y in filtered if y.from_state == x or y.to_state == x]))
        return available[0]

    """
    Удаляем состояние с обьединением частей перехода в РВ
    """

    def delete_state(self, state: int) -> None:
        connected = []
        # Вычисляем зависимые от состояния переходы и удаляем из общей кучи
        for transition in self.transitions:
            if transition.from_state == state or transition.to_state == state:
                connected.append(transition)
        for item in connected:
            self.transitions.remove(item)
        # Удаляем само состояние
        self.states.pop(state)
        # Вносим правки в оставшуюся часть автомата
        self.compensate_transitions(connected, state)

    """
    Восстанавливаем переходы для возврата к РВ
    """

    def compensate_transitions(self, transitions: list, state: int) -> None:
        # Объединяем переходы между парами состояний через |
        self.shorten_similar(transitions)
        # Делим переходы на классы
        cycle, starts, ends = self.split_transitions(transitions, state)
        # Переносим циклический переход на входные переходы
        if cycle is not None:
            for item in starts:
                item.by = item.by + '{}*'.format(safe_wrap(cycle.by))
        # Now interconnect
        for first in starts:
            for second in ends:
                self.transitions.append(Transition(first.from_state,
                                                   safe_wrap(first.by) + safe_wrap(second.by),
                                                   second.to_state))

    """
    Объединение пар схожих переходов (между одной парой состояний)
    """

    @staticmethod
    def shorten_similar(transitions: list) -> None:
        for transition in transitions:
            similar = [transition]
            for second in transitions:
                if transition == second:
                    continue
                if transition.from_state == second.from_state and transition.to_state == second.to_state:
                    similar.append(second)
            # Заменяем пачку состояний на одно
            if len(similar) > 1:
                for item in similar:
                    transitions.remove(item)

                transitions.append(Transition(similar[0].from_state,
                                              '|'.join([safe_wrap(i.by) for i in similar]),
                                              similar[0].to_state))

    def finalize_re(self, state=0) -> str:
        result = ''
        cycle, starts, ends = self.split_transitions(self.transitions, state)
        if cycle is not None:
            result += '{}*'.format(safe_wrap(cycle.by))
        # Если есть куда идти дальше
        if len(ends) > 0:
            sub = ''
            # Если переходим от финального узла необходим эпсилон
            if state in self.end:
                sub += 'E'
            # Добавляем следующий уровень идя дальше по переходам
            for item in ends:
                if state in self.end:
                    sub += '|'
                sub += item.by
                sub += self.finalize_re(item.to_state)
            result += safe_wrap(sub)
        return result

    @staticmethod
    def split_transitions(transitions: list, state: int) -> (list, list, list):
        cycle = None
        starts = []
        ends = []
        for item in transitions:
            if item.to_state == state:
                if item.from_state == state:
                    cycle = item
                    continue
                else:
                    starts.append(item)
                    continue
            elif item.from_state == state:
                ends.append(item)
                continue
        return cycle, starts, ends


def safe_wrap(inp: str) -> str:
    if inp[0] == '(' and inp[-1] == ')':
        return inp
    if len(inp) == 1:
        return inp
    if inp[-1] == '*':
        return inp
    if '|' not in inp and '*' not in inp:
        return inp
    if '|' in inp:
        if inp.count('|') < inp.count('('):
            return inp
        return '(' + inp + ')'
    return inp


class Transition:
    def __init__(self, from_state: int, by: str, to_state: int):
        self.from_state = from_state
        self.by = by
        self.to_state = to_state
