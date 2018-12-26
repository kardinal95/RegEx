from py.parser import RegexParser


def main() -> None:
    # Input and validation
    temp = '(a.(b|c))*.c.#'
    parser = RegexParser(temp)
    print(parser.positions)


if __name__ == '__main__':
    main()