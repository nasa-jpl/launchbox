from .result import LBError
from .util import LBFile, LBPath


class LBConfig:
    def __init__(self, path):
        # Params
        self.path = LBPath.join(path, "launch.yaml")
        # Load
        self.data = None
        self.yaml = None
        self.load()

    def load(self):
        if LBFile.exists(self.path):
            self.data = LBFile.read(self.path)
            self.yaml = LBFile.read_yaml(self.path)

    def validate(self):
        # File
        if self.data is None:
            return LBError("launch.yaml", "File does not exist", log_level="warn")
        elif self.data == "":
            return LBError("launch.yaml", "File is empty", log_level="warn")
        elif not self.yaml:
            return LBError("launch.yaml", "File is not valid yaml", log_level="warn")
        # Schema
        for section, contents in self.yaml.items():
            if type(contents) is not dict:
                text = f"[section: {section}] should have type: dict"
                return LBError("launch.yaml", text, log_level="warn")
            match section:
                case "env":
                    for env, config in contents.items():
                        if type(config) is not dict:
                            text = f"[env: {env}] should have type: dict"
                            return LBError("launch.yaml", text, log_level="warn")
                case "phases":
                    for phase, actions in contents.items():
                        if phase not in ["setup", "tenant"]:
                            text = f"[section: phases] unsupported phase: {phase}"
                            return LBError("launch.yaml", text, log_level="warn")
                        elif type(actions) is not list:
                            text = f"[phase: {phase}] should have type: list"
                            return LBError("launch.yaml", text, log_level="warn")
                        for action in actions:
                            if type(action) is not str:
                                text = f"[phase: {phase}] invalid action format"
                                return LBError("launch.yaml", text, log_level="warn")
                case "resources":
                    for resource, config in contents.items():
                        if type(config) is not dict:
                            text = f"[resource: {resource}] should have type: dict"
                            return LBError("launch.yaml", text, log_level="warn")
                        if "type" in config:
                            if config["type"] not in ["postgres", "redis", "s3"]:
                                text = f"[resource: {resource}] unsupported type: {config['type']}"
                                return LBError("launch.yaml", text, log_level="warn")
                        else:
                            text = f"[resource: {resource}] missing key: type"
                            return LBError("launch.yaml", text, log_level="warn")
                case "routes":
                    for route, config in contents.items():
                        if type(config) is not dict:
                            text = f"[route: {route}] should have type: dict"
                            return LBError("launch.yaml", text, log_level="warn")
                        for key in ["route", "type", "options"]:
                            if key not in config:
                                text = f"[route: {route}] missing key: {key}"
                                return LBError("launch.yaml", text, log_level="warn")
                        if config["type"] not in ["static", "wsgi"]:
                            text = f"[route: {route}] unsupported type: {config['type']}"
                            return LBError("launch.yaml", text, log_level="warn")
                case "workers":
                    for worker, config in contents.items():
                        if type(config) is not dict:
                            text = f"[worker: {worker}] should have type: dict"
                            return LBError("launch.yaml", text, log_level="warn")
                        for key in ["runtime", "options"]:
                            if key not in config:
                                text = f"[worker: {worker}] missing key: {key}"
                                return LBError("launch.yaml", text, log_level="warn")
                        if config["runtime"] not in ["python3"]:
                            text = f"[worker: {worker}] unsupported type: {config['runtime']}"
                            return LBError("launch.yaml", text, log_level="warn")
        return True

    @property
    def env(self):
        return self.yaml.get("env", {})

    @property
    def phases(self):
        return self.yaml.get("phases", {})

    @property
    def resources(self):
        return self.yaml.get("resources", {})

    @property
    def routes(self):
        return self.yaml.get("routes", {})

    @property
    def workers(self):
        return self.yaml.get("workers", {})
