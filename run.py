from py.parser import RegexParser


def main() -> None:
    # Input and validation
    temp = '(a|a*|a|a).c.#'
    parser = RegexParser(temp)
    fsm = parser.fsm
    print(fsm.restore_re())
    pass


if __name__ == '__main__':
    main()
