from py.spec import specials


class RegexParser:
    """
    Отвечает за валидацию и обработку входных РВ
    Хранит уже обработанный РВ
    Также отвечает за индексирование результирующего РВ
    """
    def __init__(self, regex: str):
        # TODO Validation
        # TODO Convertion
        self.regex = regex
        # True хранят псевдо индексы положения для реальных позиций.
        # Symbol хранят все псевдо индексы для каждого значимого символа
        self.true_indices, self.symbols_indices = self.fill_indices()

    def fill_indices(self) -> (dict, dict):
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
