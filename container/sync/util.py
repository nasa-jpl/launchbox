import time

from manage.util import LBEvent


class LBEC:
    failure = -1
    inaction = 0
    action = 1

    @staticmethod
    def check(steps):
        # Call each step function, in order
        for step in steps:
            match step():
                case LBEC.failure:
                    LBEvent.error("LBEC.check", f"Step failure: {step.__qualname__}")
                    return time.sleep(10)
                case LBEC.inaction:
                    continue
                case LBEC.action:
                    LBEvent.complete("LBEC.check", f"Step produced action: {step.__qualname__}")
                    return
                case _:
                    LBEvent.exit("LBEC.check", f"Step result not recognized: {step.__qualname__}")
        # No step produced action
        return time.sleep(4)

    @staticmethod
    def loop(steps):
        while True:
            LBEC.check(steps)
