import sys
import time

from manage.util import LBDB, LBEvent, LBPath
from storage.s3 import LBS3


class LBBootstrap:
    @staticmethod
    def connect(attempts=6):
        # Check
        if attempts == 0:
            # Connection unavailable
            LBEvent.exit("bootstrap", "Unable to establish postgres connection")
        # Try connection
        with LBDB() as db:
            if db.connect(LBDB.template):
                # Connection succeeded
                LBEvent.complete("bootstrap", "Successfully connected to postgres")
                return True
            else:
                # Connection failed
                LBEvent.log("bootstrap", "Connection to postgres failed, retrying...")
                time.sleep(5)
                attempts -= 1
                return LBBootstrap.connect(attempts)

    @staticmethod
    def database():
        with LBDB() as db:
            if db.connect(LBDB.template):
                if db.db_exists(LBDB.core):
                    # Management database: exists
                    LBEvent.complete("bootstrap", f"Found management database: {LBDB.core}")
                else:
                    # Management database: create
                    LBEvent.log("bootstrap", "Management database not found, creating...")
                    if db.db_create(LBDB.core):
                        LBEvent.complete("bootstrap", "Management database created")
                    else:
                        LBEvent.exit("bootstrap", "Management database creation failed")

    @staticmethod
    def migrate():
        schema = LBBootstrap.schema()
        LBEvent.log("bootstrap", f"Management database schema version: {schema}")
        with LBDB() as db:
            if db.connect(LBDB.core):
                for version in LBBootstrap.versions():
                    if version > schema:
                        path = LBPath.config(f"schema/{version}.sql")
                        if db.file_import(path):
                            if db.execute("UPDATE metadata SET schema = %s", [version]):
                                LBEvent.complete(
                                    "bootstrap",
                                    f"Applied management database migration: {version}",
                                )
                        else:
                            LBEvent.exit(
                                "bootstrap",
                                f"Failed to apply management database migration: " f"{version}",
                            )

    @staticmethod
    def schema():
        with LBDB() as db:
            if db.connect(LBDB.core):
                # Get management database schema version
                if db.table_exists("metadata"):
                    if result := db.select("SELECT schema FROM metadata"):
                        return result[0]["schema"]
        return -1

    @staticmethod
    def versions():
        versions = []
        for path in LBPath.list(LBPath.config("schema/*.sql")):
            filename = LBPath.basename(path)
            version = int(filename.split(".")[0])
            versions.append(version)
        versions.sort()
        return versions


if __name__ == "__main__":
    # Arguments
    flag = sys.argv[1] if (len(sys.argv) > 1) else None

    # Verify Postgres connection
    LBBootstrap.connect()

    # Create management database
    LBBootstrap.database()

    # Migrate management database
    LBBootstrap.migrate()

    # Create S3 builds bucket
    if not LBS3.bucket.exists("builds"):
        LBS3.bucket.create("builds")
        LBEvent.complete("bootstrap", "Created S3 builds bucket")
