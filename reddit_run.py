import os
from dotenv import load_dotenv
from util import base_directory, init_directories
env_file_path = os.path.join(base_directory, ".env")
load_dotenv(env_file_path)

from reddit_api import RedditAPI
import argparse
import signal
import reddit_logging
import traceback

apiObject = None

parser = argparse.ArgumentParser(description="Run EDI")
parser.add_argument("--show-progress", action="store_true", help="Show Progress Bars for Downloads")
parser.add_argument("--no-weekly", default=False, action="store_true", help="Disables the program from trying to run the weekly lockscreen photos portion")
parser.add_argument("--verbose", default=False, action="store_true", help="Show output for every action")
parser.add_argument("--log-file", help="File to store logging into")
parser.add_argument("--no-log-file", default=False, action="store_true", help="Don't log program into log file")

def sigterm_handler(signalNum, frame):
    print("\nCleaning Up Files Before Termination\n")
    if apiObject is not None:
        apiObject.do_cleanup()
    exit(0)


if __name__ == "__main__":
    init_directories()
    signal.signal(signal.SIGTERM, sigterm_handler)

    args = parser.parse_args()

    reddit_logging.VerboseLogging = args.verbose

    if args.log_file is None or not os.path.exists(args.log_file):
        reddit_logging.LoggingFile = os.path.join(base_directory, "PictureSource", "log.txt")
    else:
        reddit_logging.LoggingFile = args.log_file

    reddit_logging.FileLogging = not args.no_log_file

    reddit_logging.log("Begin Program")
    try:

        apiObject = RedditAPI(args)
        apiObject.do_daily_iteration()
        if not args.no_weekly:
            apiObject.do_weekly_iteration()
    except Exception:
        reddit_logging.log(traceback.format_exc())

    reddit_logging.log("End Program")



