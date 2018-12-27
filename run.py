from py.fsm import FiniteStateMachine
from py.parser import RegexParser
from py.tree import Tree
from py.validator import Validator


def main() -> None:
    # TODO Input from KB
    temp = input('Regex: ')
    validator = Validator(temp)
    try:
        parser = RegexParser(validator.validation())
    except ValueError:
        print('Incorrent input')
        return
    tree = Tree(parser)
    fsm = FiniteStateMachine(tree.root, parser.symbols_indices, tree.follow_pos)
    try:
        print(fsm.restore_re())
    except:
        print('Unavailable type of conversion!')


if __name__ == '__main__':
    main()
