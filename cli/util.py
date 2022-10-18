import argparse
import json
import sys


class LBCLI:
    def __init__(self, description):
        self.args = {}
        self.parser = argparse.ArgumentParser(
            description=description,
            usage="%(prog)s [argument]",
        )

    def arg(self, name, param=None, param_type=None, help=None):
        self.args[name] = param_type
        if param:
            metavar = self.metavar(param, param_type)
            self.parser.add_argument(f"--{name}", metavar=metavar, nargs=1, help=help)
        else:
            self.parser.add_argument(name, action="store_true", help=help)

    def decode(self, value, kind):
        if kind in [float, int, str]:
            return kind(value)
        elif kind == "json":
            try:
                return json.loads(value)
            except Exception:
                pass
        elif kind is None:
            return value

    def help(self):
        self.parser.print_help()

    def metavar(self, param, param_type):
        if type(param_type) == type:
            param_type = param_type.__name__
        return f"<{param} :{param_type}>"

    def parse(self):
        if parsed := self.parser.parse_args():
            for name, kind in self.args.items():
                if value := getattr(parsed, name):
                    return (name, self.decode(value, kind))
        return False

    def output(self, value):
        try:
            print(json.dumps(value))
        except Exception as error:
            sys.exit(error)
