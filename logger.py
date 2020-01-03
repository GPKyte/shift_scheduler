VERBOSE = True
DEBUG = True

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

def log_value(var_name, value):
    location_id = debuginfo(2)
    log_debug(f"{var_name} @{location_id}: {value}")

def log(printable_data):
    print(printable_data)
