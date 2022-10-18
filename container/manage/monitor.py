import json

from models.sites import LBSites

from .util import LBCLI, LBEnv, LBEvent, LBPath


class LBMonitor:
    @staticmethod
    def check():
        # Prepare
        results = []
        # List sites
        for site in LBSites.list():
            site_id = site["site_id"]
            result = {
                "site_id": site_id,
                "hostnames": {},
                "uwsgi": LBMonitor.uwsgi(site_id),
            }
            # Hostnames
            for item in site["hostnames"]:
                hostname = item["name"]
                ssl = item["ssl_cert"]
                status = LBMonitor.status(hostname, ssl)
                result["hostnames"][hostname] = status
            # Add
            results.append(result)
        # Results
        return results

    @staticmethod
    def status(hostname, ssl):
        # Params
        args = ["curl", "-I", "-o", "/dev/null", "-sw", "%{http_code}"]
        # URL
        proto = "https" if ssl else "http"
        args += [f"{proto}://{hostname}"]
        # Connect
        external = f"{hostname}:{443 if ssl else 80}"
        internal = f"127.0.0.1:{8443 if ssl else 8080}"
        args += ["--connect-to", f"{external}:{internal}"]
        # Env
        if LBEnv.aws():
            args += ["--haproxy-protocol"]
        # Request
        try:
            response = LBCLI.run(args, output=True)
            code = int(response.stdout)
        except Exception:
            code = False
        # Result
        return code

    @staticmethod
    def uwsgi(site_id):
        results = {}
        for path in LBPath.list(LBPath.uwsgi(f"stats/{site_id}_*.sock")):
            # Params
            vassal = LBPath.basename(path).split(".")[0]
            results[vassal] = []
            # Call
            args = ["uwsgi", "--connect-and-read", path]
            response = LBCLI.run(args, output=True)
            if response.returncode == 0:
                # Decode
                try:
                    if json_data := response.stderr.decode("utf-8"):
                        # Parse
                        data = json.loads(json_data)
                        workers = data["workers"]
                        # Format
                        for worker in workers:
                            result = {}
                            targets = [
                                "id",
                                "accepting",
                                "avg_rt",
                                "exceptions",
                                "harakiri_count",
                                "last_spawn",
                                "requests",
                                "status",
                            ]
                            for key, value in worker.items():
                                if key in targets:
                                    result[key] = value
                                elif key == "cores":
                                    busy = [item["in_request"] for item in value]
                                    result["threads"] = {
                                        "count": len(value),
                                        "busy": sum(busy),
                                    }
                            results[vassal].append(result)
                except Exception:
                    LBEvent.warn("LBMonitor", f"Error decoding uWSGI stats for path: {path}")
        return results
