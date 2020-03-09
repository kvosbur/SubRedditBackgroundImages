import datetime
LoggingFile = ""
LoggingEnabled = False


def log_to_file(logString):
    with open(LoggingFile, "a") as f:
        f.write(logString)


def log(*args, is_heading=False):
    if LoggingEnabled:
        output_str = [str(datetime.datetime.now().strftime("")) + ": "]
        if is_heading:
            output_str.append("### ")
        for arg in args:
            output_str.append(str(arg) + " ")
        if is_heading:
            output_str.append("###")
        output_str.append("\n")
        output = "".join(output_str)
        print(output, end="")
        log_to_file(output)

