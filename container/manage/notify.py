import json
from functools import partial

from .util import LBDB, LBEvent


class LBNotify:
    @staticmethod
    def callback(encoded, channel, func):
        # Decode
        try:
            payload = json.loads(encoded)
        except Exception:
            LBEvent.warn("notify.listen", f"[channel: {channel}] unable to decode payload")
            return False
        # Parse
        kind = payload["kind"]
        data = payload["data"]
        # Log
        LBEvent.log("notify.listen", f"[channel: {channel}] notification received [kind: {kind}]")
        # Deliver
        func(kind=kind, data=data)

    @staticmethod
    def listen(channel, func):
        with LBDB() as db:
            if db.connect(LBDB.core):
                callback = partial(LBNotify.callback, channel=channel, func=func)
                db.listen(channel, callback)

    @staticmethod
    def send(channel, kind, data):
        # Format
        payload = {
            "kind": kind,
            "data": data,
        }
        # Encode
        try:
            encoded = json.dumps(payload)
        except Exception:
            LBEvent.warn("notify.send", f"[channel: {channel}] unable to encode payload")
            return False
        # Connect
        with LBDB() as db:
            if db.connect(LBDB.core):
                # Log
                LBEvent.log("notify.send", f"[channel: {channel}] sending notification [kind: {kind}]")
                # Send
                db.notify(channel, encoded)
                return True
