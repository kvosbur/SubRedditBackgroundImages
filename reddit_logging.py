

LoggingEnabled = False

def log(*args, is_heading=False):
    if LoggingEnabled:
        if is_heading:
            print("###", end=" ")
        for arg in args:
            print(arg, end=" ")
        if is_heading:
            print(" ###", end="")
        print("")  # force newline