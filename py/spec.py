# Спецсимволы
specials = ['.', '*', '(', ')', '|']
# Приоритеты операций (чем меньше тем выше)
priorities = {
    '.': 0,
    '|': 1,
    '*': 2
}
left_operands = ['(', '|']
right_operands = ['*', '|', ')']
error_list = [['|', '|'], ['|', '*'], ['|', ')'], ['(', '|'], ['(', '*'], ['(', ')'], ['*', '*']]