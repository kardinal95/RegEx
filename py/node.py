from copy import copy

from py.spec import specials, priorities


class Node:
    value = None
    left = None
    right = None
    nullable = None
    first_pos = None
    last_pos = None

    """
    Узер дерева РВ
    Shift - сдвиг относительно реальной позиции в исходном РВ
    (эквивалентен реальной позиции первого символа входной строки в исходном РВ)
    """

    def __init__(self, regex: str, positions: dict, shift=0):
        # Отбрасываем скобки. Корректируем сдвиг символа
        regex, shift = self.fix_brackets(regex, shift)

        # Позиция символа текущего листа в исходном РВ
        real_pos = shift
        # Для конечных листов специальная обработка
        if len(regex) == 1:
            if regex in specials:
                raise Exception('Special symbol cannot be an endpoint!')
            self.value = regex
            self.left = None
            self.right = None
        else:
            # Находим позицию для разделения
            current_pos = self.find_current_position(regex)
            # Корректируем реальную позицию
            real_pos += current_pos
            self.value = regex[current_pos]
            # У * только правый ребенок!
            # Учитываем необходимый сдвиг при создании правых/левых детей для текущего узла
            if self.value == '*':
                self.right = Node(regex[:current_pos], positions, shift)
            else:
                self.left = Node(regex[:current_pos], positions, shift)
                self.right = Node(regex[current_pos + 1:], positions, shift + current_pos + 1)
        self.nullable = self.get_nullable()
        self.first_pos = self.get_first_post(positions, real_pos)
        self.last_pos = self.get_last_post(positions, real_pos)

    """
    Получение необходимой позиции для разделения
    (Эквивалентно позиции символа текущего узла)
    """

    @staticmethod
    def find_current_position(regex: str) -> int:
        level = 0
        result = 0
        priority = 5
        # Пропускаем скобки и ищем высший приоритет (самый правый при одинаковых)
        for index, symbol in enumerate(regex):
            if symbol == '(':
                level += 1
                continue
            if symbol == ')':
                level -= 1
                continue
            # Делим только по спецсимволам
            if symbol in specials and level == 0 and priorities[symbol] <= priority:
                result = index
                priority = priorities[symbol]
        return result

    """
    Проверяем может ли результат подвыражения быть равен пустой строке
    """

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

    """
    Находим первую позицию (псевдо-позиция!)
    """

    def get_first_post(self, positions: dict, position: int) -> set:
        result = set()
        # У эпсилона не заполняем
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

    """
    Находим последнюю позицию (псевдо-позиция!)
    """

    def get_last_post(self, positions: dict, position: int) -> set:
        result = set()
        # У эпсилона не заполняем
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

    @staticmethod
    def fix_brackets(regex: str, shift: int) -> (str, int):
        if regex[0] != '(' or regex[-1] != ')':
            return regex, shift
        counter = 0
        for i in regex[:-1]:
            if i == '(':
                counter += 1
            elif i == ')':
                counter -= 1
                if counter == 0:
                    return regex, shift
        if counter == 1:
            return Node.fix_brackets(regex[1:-1], shift + 1)
        else:
            return regex, shift
