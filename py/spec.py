# Спецсимволы
specials = ['.', '*', '(', ')', '|']
# Приоритеты операций (чем меньше тем выше)
priorities = {
    '.': 1,
    '|': 0,
    '*': 2
}
left_operands = ['(', '|']
right_operands = ['*', '|', ')']
error_list = [['|', '|'], ['|', '*'], ['|', ')'], ['(', '|'], ['(', '*'], ['(', ')'], ['*', '*']]