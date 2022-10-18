import json
import statistics

from manage.infra import LBInfra
from manage.monitor import LBMonitor
from manage.util import LBDB


class LBStats:
    @staticmethod
    def latest():
        with LBDB() as db:
            if db.connect(LBDB.core):
                # Construct
                query = """
                    SELECT DISTINCT ON ("container_id") "container_id", "data", "timestamp"::timestamptz
                    FROM stats
                    WHERE "timestamp" >= (NOW() - INTERVAL '80 SECONDS')
                    ORDER BY "container_id", "timestamp" DESC, "data"
                """
                # Select
                stats = db.select(query) or []
                # Infra
                results = LBInfra.cluster.describe()
                for identifier in results.keys():
                    results[identifier]["stats"] = False
                    for item in stats:
                        if item["container_id"] == identifier:
                            results[identifier]["stats"] = {
                                "sites": item["data"],
                                "timestamp": item["timestamp"],
                            }
                # Results
                return results
        return []

    @staticmethod
    def timeline():
        with LBDB() as db:
            if db.connect(LBDB.core):
                query = """
                    SELECT "container_id", "data", "timestamp"::timestamptz
                    FROM stats
                    WHERE "data" != '[]'
                    ORDER BY "timestamp" ASC
                """
                if stats := db.select(query):
                    # Compile
                    results = {}
                    for row in stats:
                        container_id = row["container_id"]
                        results.setdefault(container_id, [])
                        result = {
                            "sites": {},
                            "timestamp": row["timestamp"],
                        }
                        for site in row["data"]:
                            site_id = site["site_id"]
                            for vassal, workers in site.get("uwsgi", {}).items():
                                route_id = vassal.replace(f"{site_id}_", "")
                                result["sites"].setdefault(site_id, {"routes": {route_id: {"workers": {}}}})
                                for worker in workers:
                                    worker_id = f"worker{worker['id']}"
                                    cumulative = worker["requests"]
                                    last_spawn = worker["last_spawn"]
                                    for entry in reversed(results[container_id]):
                                        if previous := entry["sites"][site_id]["routes"][route_id]["workers"].get(
                                            worker_id
                                        ):
                                            cumulative = previous["cumulative"]
                                            if last_spawn > previous["last_spawn"]:
                                                cumulative += worker["requests"]
                                            else:
                                                cumulative += worker["requests"] - previous["requests"]
                                            break
                                    result["sites"][site_id]["routes"][route_id]["workers"][worker_id] = {
                                        "avg_rt": worker["avg_rt"],
                                        "cumulative": cumulative,
                                        "requests": worker["requests"],
                                        "last_spawn": last_spawn,
                                    }
                        for site_id, site in result["sites"].items():
                            for route_id, route in site["routes"].items():
                                if route["workers"]:
                                    results[container_id].append(result)
                                    break
                    # Reduce
                    for container_id, entries in results.items():
                        for entry in entries:
                            for site_id, site in entry["sites"].items():
                                for route_id, route in site["routes"].items():
                                    site["routes"][route_id] = {
                                        "avg_rt": statistics.fmean(
                                            [worker["avg_rt"] for worker in route["workers"].values()]
                                        ),
                                        "requests": sum([worker["cumulative"] for worker in route["workers"].values()]),
                                    }
                    return {"containers": results}
        return []

    @staticmethod
    def update():
        # Params
        if container_id := LBInfra.current.identifier():
            # Connect
            with LBDB() as db:
                if db.connect(LBDB.core):
                    # Cleanup expired stats (older than 7 days)
                    query = """DELETE FROM stats WHERE "timestamp" < (NOW() - INTERVAL '7 DAYS')"""
                    db.execute(query)
                    # Data
                    data = LBMonitor.check()
                    # Construct
                    query = """INSERT INTO stats("container_id", "data") VALUES(%s, %s)"""
                    # Insert
                    db.execute(query, [container_id, json.dumps(data)])
