from py.spec import error_list, left_operands, right_operands


class Validator:

    def __init__(self, regex: str):
        self.regex = regex

    def is_valid(self) -> bool:
        count = 0
        for left, right in zip(self.regex[:-1], self.regex[1:]):
            if not self.is_valid_pair(left, right):
                return False
            if left == '(':
                count += 1
            if left == ')':
                count -= 1
        if self.regex[-1] == '(':
            count += 1
        if self.regex[-1] == ')':
            count -= 1
        if count == 0:
            return True
        else:
            return False

    @staticmethod
    def is_valid_pair(first_let: str, second_let: str) -> bool:
        for pair in error_list:
            if first_let == pair[0] and second_let == pair[1]:
                return False
        return True

    def validation(self) -> str:
        if not self.is_valid():
            raise ValueError('Regex is not valid')
        i = 0
        result = self.regex

        while i < len(result) - 1:
            if result[i] not in left_operands and result[i+1] not in right_operands:
                result = result[:i + 1] + '.' + result[i + 1:]
                i += 1
            i += 1
        return result

