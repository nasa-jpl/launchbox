import time

from models.auth import LBAuth
from models.stats import LBStats

from .util import LBEvent


class LBJob:
    def __init__(self, method, frequency, initial=0):
        # Params
        self.method = method
        self.name = self.method.__qualname__
        # Timing
        self.frequency = frequency
        self.remaining = initial

    def tick(self):
        # Each tick represents one second
        if self.remaining > 0:
            # Decrement
            self.remaining -= 1
        else:
            try:
                # Run
                LBEvent.log("LBJob", f"Running job: {self.name}()")
                self.method()
            except Exception as error:
                LBEvent.error("LBJob", error)
            finally:
                # Reset
                self.remaining = self.frequency


jobs = [
    LBJob(LBAuth.cleanup, frequency=3600),
    LBJob(LBStats.update, frequency=60, initial=30),
]

while True:
    # Tick
    for job in jobs:
        job.tick()
    # Sleep
    time.sleep(1)
