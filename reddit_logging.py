import datetime
LoggingFile = ""
VerboseLogging = False
FileLogging = True


def log_to_file(logString):
    with open(LoggingFile, "a") as f:
        f.write(logString)


def log(*args, is_heading=False):
    output_str = [str(datetime.datetime.now().strftime("%Y-%m-%d")) + ": "]
    if is_heading:
        output_str.append("### ")
    for arg in args:
        output_str.append(str(arg) + " ")
    if is_heading:
        output_str.append("###")
    output_str.append("\n")
    output = "".join(output_str)

    if VerboseLogging:
        print(output, end="")
    if FileLogging:
        log_to_file(output)

