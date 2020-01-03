# Set of utils for logging and debugging
from inspect import getframeinfo, stack

VERBOSE = True
DEBUG = True
NOT_NOW = -1

MONITOR = dict()


def debuginfo(function_calls_before_now = 1):
    caller = getframeinfo(stack()[function_calls_before_now][0])
    return f"{caller.filename}({caller.lineno})"

def log_verbose(verbose_content):
    global VERBOSE
    if VERBOSE:
        log(verbose_content)

def log_debug(debugging_content):
    global DEBUG
    if DEBUG:
        log(debugging_content)

def log_value(var_name, value, stack_layer=2):
    location_id = debuginfo(stack_layer)
    log_debug(f">>>\t@{location_id}:{var_name} = {value}")

def logg(data, log_level):
    if log_level is NOT_NOW:
        pass
    else:
        log(data)

def log(printable_data):
    print(printable_data)

def track_var(var_name, reference):
    log_value(var_name, reference, 3)

    global MONITOR
    MONITOR[var_name] = reference

def inspect_var(var_name):
    pass

def inspect_var():
    for var in MONITOR.keys():
        log_debug(f"{var}: {MONITOR[var]}")

    input()
