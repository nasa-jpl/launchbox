import json
import re

from manage.bridge import LBBridge
from manage.notify import LBNotify
from manage.util import LBDB, LBUUID, LBEvent
from models.deploys import LBDeploys
from models.services import LBServices
from models.users import LBUsers


class LBSites:
    # Add site
    @staticmethod
    def add(site_id, service_id):
        if not LBSites.valid(site_id):
            return False
        if LBSites.exists(site_id):
            return False
        if not LBServices.exists(service_id):
            return False
        with LBDB() as db:
            if db.connect(LBDB.core):
                query = """
                    INSERT INTO sites("site_id", "service_id")
                    VALUES(%s, %s)
                """
                if db.execute(query, [site_id, service_id]):
                    LBEvent.complete(
                        "LBSites.add",
                        f"Added site [site_id: {site_id}, service_id: {service_id}]",
                    )
                    LBSites.events.add(site_id, "create", "site", {"service_id": service_id})
                    return True
        return False

    # Check if site exists
    @staticmethod
    def exists(site_id):
        with LBDB() as db:
            if db.connect(LBDB.core):
                query = """SELECT 1 FROM sites WHERE "site_id" = %s"""
                if results := db.select(query, [site_id]):
                    return len(results) == 1
        return False

    # Get sites for service_id
    @staticmethod
    def for_service(service_id):
        with LBDB() as db:
            if db.connect(LBDB.core):
                query = """SELECT * FROM sites WHERE "service_id" = %s"""
                if results := db.select(query, [service_id]):
                    return results
        return []

    # Get site
    @staticmethod
    def get(site_id, redacted=True):
        with LBDB() as db:
            if db.connect(LBDB.core):
                query = """SELECT * FROM sites WHERE "site_id" = %s"""
                if results := db.select(query, [site_id]):
                    site = results[0]
                    site["deployment"] = LBDeploys.site.latest(site_id)
                    site["events"] = LBSites.events.list(site_id)
                    site["hostnames"] = LBSites.hostnames.list(site_id, redacted=redacted)
                    site["notes"] = LBSites.notes.list(site_id)
                    return site
        return False

    # List sites
    @staticmethod
    def list(redacted=True):
        with LBDB() as db:
            if db.connect(LBDB.core):
                # Results: Sites
                sites = db.select("""SELECT * FROM sites ORDER BY "site_id" ASC""")
                # Results: Hostnames
                hostnames = db.select("""SELECT * FROM hostnames ORDER BY "primary" DESC""")
                # Map
                mapping = {site["site_id"]: site for site in sites}
                for site_id in mapping.keys():
                    mapping[site_id]["deployment"] = LBDeploys.site.latest(site_id)
                    mapping[site_id]["hostnames"] = []
                # Parse
                for hostname in hostnames:
                    site_id = hostname["site_id"]
                    # Redact
                    if redacted:
                        hostname["ssl_cert"] = bool(hostname["ssl_cert"])
                    # Add
                    if site_id in mapping:
                        mapping[site_id]["hostnames"].append(hostname)
                # Results
                return list(mapping.values())
        return []

    # Remove site
    @staticmethod
    def remove(site_id):
        if LBSites.exists(site_id):
            with LBDB() as db:
                if db.connect(LBDB.core):
                    # Remove site database records
                    db.execute("""DELETE FROM sites WHERE "site_id" = %s""", [site_id])
                    db.execute("""DELETE FROM hostnames WHERE "site_id" = %s""", [site_id])
                    db.execute("""DELETE FROM notes WHERE "site_id" = %s""", [site_id])
                    # Event
                    LBSites.events.add(site_id, "delete", "site")
                    # Log
                    LBEvent.complete("LBSites.remove", f"Removed site [site_id: {site_id}]")
                    # Sync
                    LBNotify.send("sites", "remove", {"site_id": site_id})
                    return True
        return False

    # Update site
    @staticmethod
    def update(site_id, attr, value):
        if attr in ["desc", "name"]:
            if LBSites.exists(site_id):
                with LBDB() as db:
                    if db.connect(LBDB.core):
                        query = f"""UPDATE sites SET "{attr}" = %s WHERE "site_id" = %s"""
                        if db.execute(query, [value, site_id]):
                            # Event
                            LBSites.events.add(site_id, "update", "site", {attr: value})
                            # Result
                            return True
        return False

    # Validate site_id
    @staticmethod
    def valid(site_id):
        return re.match(r"^[A-Za-z0-9-]+$", site_id) is not None

    # Events
    class events:
        # Add event
        @staticmethod
        def add(site_id, action, kind, metadata={}):
            # Check
            if type(metadata) is not dict:
                LBEvent.warn(
                    "manager",
                    f"Unable to add event (invalid type) for site [site_id: {site_id}]",
                )
                return False
            with LBDB() as db:
                if db.connect(LBDB.core):
                    # Params
                    source = "API" if LBUsers.current() else "manager"
                    user_id = LBUsers.current() or "lb-manager"
                    # Construct
                    query = """
                        INSERT INTO events("site_id", "user_id", "source", "action", "kind", "metadata")
                        VALUES(%s, %s, %s, %s, %s, %s)
                    """
                    args = [site_id, user_id, source, action, kind, json.dumps(metadata)]
                    # Create events database record
                    if db.execute(query, args):
                        # Log
                        LBEvent.complete(
                            "manager",
                            f"Added event ({action} {kind}) for site [site_id: {site_id}]",
                        )
                        return True
            return False

        # List events
        @staticmethod
        def list(site_id):
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """
                        SELECT e1."site_id", e1."source", e1."user_id",
                        (CASE
                            WHEN e1."user_id" = 'lb-manager' THEN 'System'
                            ELSE u1."first_name"
                        END) as "first_name",
                        (CASE
                            WHEN e1."user_id" = 'lb-manager' THEN 'User'
                            ELSE u1."last_name"
                        END) as "last_name",
                        e1."action", e1."kind", e1."metadata", e1."timestamp"::timestamptz
                        FROM events e1 LEFT JOIN users u1 ON (e1."user_id" = u1."user_id")
                        WHERE e1."site_id" = %s ORDER BY e1.timestamp DESC
                    """
                    if events := db.select(query, [site_id]):
                        return events
            return []

    # Hostnames
    class hostnames:
        # Add hostname
        @staticmethod
        def add(site_id, hostname):
            if not LBSites.hostnames.exists(site_id, hostname):
                with LBDB() as db:
                    if db.connect(LBDB.core):
                        # SSL certificate
                        # TODO: Hook up to plugin system
                        ssl = {}
                        # Determine primary (if first hostname)
                        primary = int(len(LBSites.hostnames.list(site_id)) == 0)
                        # Construct
                        query = """
                            INSERT INTO hostnames(
                                "site_id", "name",
                                "ssl_cert", "ssl_expires", "ssl_req_id",
                                "primary"
                            )
                            VALUES(%s, %s, %s, %s, %s, %s)
                        """
                        args = [
                            site_id,
                            hostname,
                            ssl.get("cert", ""),
                            ssl.get("expires", -1),
                            ssl.get("req_id", ""),
                            primary,
                        ]
                        # Create hostname database records
                        if db.execute(query, args):
                            # Event
                            LBSites.events.add(site_id, "add", "hostname", {"hostname": hostname})
                            # Log
                            LBEvent.complete(
                                "manager",
                                f"Added hostname: {hostname} for site [site_id: {site_id}]",
                            )
                            # Sync
                            LBNotify.send("sites", "add-hostname", {"site_id": site_id})
                            return True
            return False

        # Check if hostname exists
        @staticmethod
        def exists(site_id, hostname):
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """SELECT 1 FROM hostnames WHERE "site_id" = %s AND "name" = %s"""
                    if results := db.select(query, [site_id, hostname]):
                        return len(results) == 1
            return False

        # Get hostname
        @staticmethod
        def get(site_id, hostname):
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """SELECT * FROM hostnames WHERE "site_id" = %s AND "name" = %s"""
                    if results := db.select(query, [site_id, hostname]):
                        return results[0]
            return False

        # List hostnames
        @staticmethod
        def list(site_id, redacted=True):
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """SELECT * FROM hostnames WHERE "site_id" = %s ORDER BY "primary" DESC"""
                    hostnames = db.select(query, [site_id])
                    if redacted:
                        for item in hostnames:
                            item["ssl_cert"] = bool(item["ssl_cert"])
                    return hostnames
            return []

        # Make primary
        @staticmethod
        def make_primary(site_id, hostname):
            if LBSites.hostnames.exists(site_id, hostname):
                with LBDB() as db:
                    if db.connect(LBDB.core):
                        # Update hostname database records
                        query = """
                            UPDATE hostnames SET "primary" = 0
                            WHERE "site_id" = %s;
                            UPDATE hostnames SET "primary" = 1
                            WHERE "site_id" = %s AND "name" = %s
                        """
                        if db.execute(query, [site_id, site_id, hostname]):
                            # Event
                            LBSites.events.add(
                                site_id,
                                "make_primary",
                                "hostname",
                                {"hostname": hostname},
                            )
                            # Log
                            LBEvent.complete(
                                "manager",
                                f"Updated primary hostname for site: {site_id}",
                            )
                            # Sync
                            LBNotify.send("sites", "primary-hostname", {"site_id": site_id})
                            return True
            return False

        # Get primary hostname
        @staticmethod
        def primary(site_id):
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """SELECT * FROM hostnames WHERE "site_id" = %s AND "primary" = 1"""
                    if results := db.select(query, [site_id]):
                        return results[0]
            return False

        # Remove hostname
        @staticmethod
        def remove(site_id, hostname):
            if result := LBSites.hostnames.get(site_id, hostname):
                with LBDB() as db:
                    if db.connect(LBDB.core):
                        # Delete hostname database records
                        query = """DELETE FROM hostnames WHERE "site_id" = %s AND "name" = %s"""
                        if db.execute(query, [site_id, hostname]):
                            if result["ssl_req_id"]:
                                # Revoke/delete certificate
                                # TODO: Hook up to plugin system
                                pass
                            if result["primary"]:
                                # Elect new primary hostname
                                if hostnames := LBSites.hostnames.list(site_id):
                                    LBSites.hostnames.make_primary(site_id, hostnames[0]["name"])
                            # Event
                            LBSites.events.add(site_id, "remove", "hostname", {"hostname": hostname})
                            # Log
                            LBEvent.complete("manager", f"Removed hostname for site [site_id: {site_id}]")
                            # Sync
                            LBNotify.send("sites", "remove-hostname", {"site_id": site_id})
                            return True
            return False

    # Notes
    class notes:
        # Add note
        @staticmethod
        def add(site_id, text):
            with LBDB() as db:
                if db.connect(LBDB.core):
                    # Prepare
                    note_id = LBUUID.uuid()
                    user_id = LBUsers.current() or "lb-manager"
                    # Construct
                    query = """
                        INSERT INTO notes("note_id", "site_id", "user_id", "text")
                        VALUES(%s, %s, %s, %s)
                    """
                    args = [note_id, site_id, user_id, text]
                    # Create notes database record
                    if db.execute(query, args):
                        # Log
                        LBEvent.complete("manager", f"Added note for site [site_id: {site_id}]")
                        return True
            return False

        # List notes
        @staticmethod
        def list(site_id):
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """
                        SELECT
                        n1."note_id", n1."user_id",
                        u1."first_name", u1."last_name",
                        n1."text", n1."timestamp"::timestamptz
                        FROM notes n1 LEFT JOIN users u1 ON
                        (n1."user_id" = u1."user_id")
                        WHERE n1."site_id" = %s ORDER BY n1."timestamp" DESC
                    """
                    if notes := db.select(query, [site_id]):
                        return notes
            return []

    # Users
    class users:
        # Add user
        @staticmethod
        def add(site_id, username):
            # Bridge
            result = LBBridge.users.create(site_id, username)
            # Check
            if "error" not in result.keys():
                # Event
                LBSites.events.add(site_id, "add", "user", {"username": username})
            # Result
            return result

        # List users
        @staticmethod
        def list(site_id):
            return LBBridge.users.read(site_id)

        # Remove user
        @staticmethod
        def remove(site_id, username):
            # Bridge
            result = LBBridge.users.delete(site_id, username)
            # Check
            if "error" not in result.keys():
                # Event
                LBSites.events.add(site_id, "remove", "user", {"username": username})
            # Result
            return result

        # Update user(s)
        @staticmethod
        def update(site_id, users):
            # Format: {"username": {"attr": "value"}}
            # ----
            # Bridge
            result = LBBridge.users.update(site_id, users)
            # Check
            if "error" not in result.keys():
                # Event
                LBSites.events.add(site_id, "update", "user", users)
            # Result
            return result
