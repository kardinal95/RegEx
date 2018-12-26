from py.node import Node
from py.parser import RegexParser


class Tree:
    follow_pos = None
    root = None

    """
    Создает дерево из текущего обработанного регулярного выражения в парсере
    """
    def __init__(self, parser: RegexParser) -> None:
        self.root = Node(parser.regex, parser.true_indices)
        self.init_follow_pos(parser.true_indices)

    """
    Создаем таблицу с позициями следующих элементов перехода
    """
    def init_follow_pos(self, true_indices: dict) -> None:
        self.follow_pos = dict()
        # Нам нужны все псевдо позиции
        for index in true_indices.values():
            self.follow_pos[index] = set()
        # Заполняем список перебором дерева
        self.add_follow(self.root, self.follow_pos)

    """
    Перебираем дерево и заполняем позиции элементов перехода по алгоритму
    """
    def add_follow(self, node, follow_pos) -> None:
        # На пустых выходим
        if node is None:
            return
        if node.value == '.':
            for index in node.left.last_pos:
                follow_pos[index] = follow_pos[index].union(node.right.first_pos)
        elif node.value == '*':
            for index in node.right.last_pos:
                follow_pos[index] = follow_pos[index].union(node.right.first_pos)
        # Рекурсивно обходим остальное дерево
        self.add_follow(node.left, follow_pos)
        self.add_follow(node.right, follow_pos)