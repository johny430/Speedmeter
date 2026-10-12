from enum import IntEnum


class ExitCode(IntEnum):
    OK = 0
    FAILURE = 1
    USAGE = 2  # выставляет argparse при неверных аргументах
    INTERRUPTED = 130
