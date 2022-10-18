from manage.util import LBDB, LBEnv
from storage.s3 import LBS3


class LBResources:
    @staticmethod
    def env_vars(name, config, site_id):
        results = {}
        if params := LBResources.params(name, config, site_id):
            for key, value in params.items():
                results[f"LB_{name}_{key}"] = value
        return results

    @staticmethod
    def make(name, config, site_id):
        if params := LBResources.params(name, config, site_id):
            match params["type"]:
                case "postgres":
                    # Create database (if needed)
                    with LBDB() as db:
                        if not db.connect("template1"):
                            return False
                        if db.db_exists(params["name"]):
                            return True
                        else:
                            if db.db_create(params["name"]):
                                return True
                case "s3":
                    # Create bucket (if needed)
                    if not LBS3.bucket.exists(params["bucket"]):
                        LBS3.bucket.create(params["bucket"])
                    # Make public (local only)
                    LBS3.bucket.make_public(params["bucket"])

    @staticmethod
    def params(name, config, site_id):
        match config["type"]:
            case "postgres":
                return {
                    "type": config["type"],
                    "hostname": LBEnv.get("POSTGRES_HOST"),
                    "name": f"{site_id}_{name}",
                    "username": LBEnv.get("POSTGRES_USER"),
                    "password": LBEnv.get("POSTGRES_PASSWORD"),
                    "port": LBEnv.get("POSTGRES_PORT"),
                }
            case "redis":
                return {
                    "type": config["type"],
                    "url": LBEnv.get("REDIS_CACHE_URL"),
                    "prefix": f"{site_id}_{name}",
                }
            case "s3":
                return {
                    "type": config["type"],
                    "bucket": f"{site_id}-{name}",
                }

    @staticmethod
    def update(resources, site_id):
        for name, config in resources.items():
            LBResources.make(name, config, site_id)
