from py.fsm import FiniteStateMachine
from py.parser import RegexParser
from py.tree import Tree


def main() -> None:
    # TODO Input from KB
    temp = '(a|b*)|(a|c).#'
    parser = RegexParser(temp)
    tree = Tree(parser)
    fsm = FiniteStateMachine(tree.root, parser.symbols_indices, tree.follow_pos)
    print(fsm.restore_re())
    pass


if __name__ == '__main__':
    main()
