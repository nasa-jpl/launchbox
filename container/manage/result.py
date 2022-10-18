from manage.util import LBEvent, LBStack


class LBError:
    def __init__(self, kind, data, log_level=None):
        # Params
        self.kind = kind
        self.data = data
        self.log_level = log_level
        # Stack
        stack = LBStack.get(2) or {}
        caller = stack.get("caller")
        filename = stack.get("filename")
        lineno = stack.get("lineno")
        # Format
        source = f"{caller} ({filename}:{lineno})"
        message = f"[{self.kind}]: {self.data}"
        # Log
        match self.log_level:
            case "error":
                LBEvent.error(source, message)
            case "warn":
                LBEvent.warn(source, message)

    def __bool__(self):
        return False
