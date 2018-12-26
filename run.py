from py.parser import RegexParser
from py.validator import Validator


def main() -> None:
    # Input and validation
    temp = '(a(b|c))*c#'

    valid = Validator(temp)
    print(valid.is_valid())
    print(valid.validation())

    # parser = RegexParser(temp)
    # print(parser.positions)


if __name__ == '__main__':
    main()

