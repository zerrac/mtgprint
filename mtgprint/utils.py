def colored_print(string: str, color):
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    print(color + BOLD + string + ENDC)

def print_header(string: str):
    HEADER = '\033[95m'
    colored_print(string,HEADER)

def print_ok(string: str):
    OK = '\033[92m'
    colored_print(string, OK)

def print_error(string: str):
    ERROR = '\033[91m'
    colored_print(string, ERROR)

def print_warn(string: str):
    WARN = '\033[33m'
    colored_print(string, WARN)