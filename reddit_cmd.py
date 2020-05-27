import cmd


class RedditShell(cmd.Cmd):

    prompt = "> "

    def do_daily_blacklist(self, position):
        """daily_blacklist [position]
        Blacklist the image given by position, default is 0"""
        try:
            pos = int(position)
        except Exception:
            pos = 0

        print("do daily blacklist", pos)

    def do_rerun_weekly(self, line):
        """rerun_weekly - rerun the weekly blacklisting any deleted images from the source directory"""
        print("do rerun of weekly")

    def do_safe(self, line):
        """safe - Switch source of images to the safe subreddit"""
        print("switch to safe mode")

    def do_exit(self, line):
        """exit - exit program"""
        exit(0)

    def do_quit(self, line):
        """quit - other alias for exit"""
        self.do_exit(line)

    def do_1(self, line):
        """1 - alias for safe command"""
        self.do_safe(line)

    def do_2(self, line):
        """2 - alias for daily_blacklist"""
        self.do_daily_blacklist(line)
