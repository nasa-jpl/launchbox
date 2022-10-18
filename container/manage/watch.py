import asyncio
import sys

import watchfiles

from .network import LBNetwork
from .util import LBEnv, LBEvent, LBPath

# Check
if not LBEnv.local():
    LBEvent.log("manage.watch", "Non-local environment detected, skipping python file watch..")
    sys.exit(0)


async def main():
    # Filter
    ignore_paths = [LBPath.builds(), LBPath.services(), LBPath.sites()]
    wfilter = watchfiles.PythonFilter(ignore_paths=ignore_paths)
    # Event
    LBEvent.log("manage.watch", "Watching python files for changes...")
    # Watch
    async for changes in watchfiles.awatch(LBPath.app(), debounce=1000, watch_filter=wfilter):
        # Reload
        LBEvent.log("manage.watch", "Change detected, reloading uWSGI vassals...")
        LBNetwork.uwsgi.vassals.reload()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
