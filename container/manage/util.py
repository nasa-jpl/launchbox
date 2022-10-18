import datetime
import glob
import inspect
import json
import os
import pathlib
import select
import shlex
import shutil
import socket
import subprocess
import sys
import urllib.parse
import uuid
from functools import partial
from string import Template

import dateutil.parser
import envdir
import psycopg2
import psycopg2.extensions
import psycopg2.extras
import termcolor
import yaml


class LBCLI:
    @staticmethod
    def args(command):
        if type(command) == str:
            return shlex.split(command, posix=True)

    @staticmethod
    def run(args, cwd=None, setenv={}, stdin=None, output=False):
        # Extend existing environment variables
        env = LBEnv.copy()
        for var_name, value in setenv.items():
            env[var_name] = str(value)
        # Check stdin (invalid stdin can cause commands that expect it to hang)
        if stdin is not None:
            if type(stdin) is not bytes:
                LBEvent.warn("LBCLI", "Unable to run command: stdin value must use byte format")
                return False
        return subprocess.run(args, cwd=cwd, env=env, input=stdin, capture_output=output)


class LBDB:
    core = "lb"
    template = "template1"

    def __init__(self):
        # Specify database connection settings
        self.config = {
            "host": LBEnv.get("POSTGRES_HOST", "localhost"),
            "port": LBEnv.get("POSTGRES_PORT", 5342),
            "user": LBEnv.get("POSTGRES_USER", "postgres"),
            "password": LBEnv.get("POSTGRES_PASSWORD", "postgres"),
        }
        # Params
        self.link = None

    def __enter__(self):
        # Enter hook (for with blocks)
        return self

    def __exit__(self, type, value, traceback):
        # Exit hook (for with blocks)
        self.close()

    def connect(self, dbname, autocommit=True):
        # Check if connection exists
        if self.connected(dbname):
            self.link.autocommit = autocommit
            return True
        # New connection
        try:
            self.close()
            self.link = psycopg2.connect(dbname=dbname, **self.config)
            self.link.autocommit = autocommit
            self.types()
        except Exception as error:
            self.link = None
            LBEvent.warn("LBDB", f"Failed to connect to database: {dbname}")
            LBEvent.error("LBDB", error)
        finally:
            return bool(self.link)

    def connected(self, dbname):
        if self.link:
            if self.link.info.dbname == dbname:
                # Check if connection is valid with query
                return self.execute("SELECT 1")
        return False

    def close(self):
        if self.link:
            self.link.close()
        self.link = None

    def commit(self):
        if self.link:
            if not self.link.autocommit:
                if self.link.get_transaction_status() == 2:
                    self.link.commit()
                    return True
        return False

    def db_create(self, dbname):
        return self.execute(f"CREATE DATABASE {self.quote(dbname)}")

    def db_exists(self, dbname):
        results = self.select("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", [dbname])
        return len(results) > 0

    def db_remove(self, dbname):
        return self.execute(f"DROP DATABASE {self.quote(dbname)}")

    def execute(self, query, params=[], options={}, runner=None):
        if self.link:
            with self.link.cursor(**options) as cursor:
                try:
                    cursor.execute(query, params)
                    return runner(cursor=cursor) if runner else True
                except Exception as error:
                    LBEvent.error("LBDB", error)
        else:
            LBEvent.warn("LBDB", "Unable to execute query: not connected to database")
        return False

    def file_import(self, path):
        if LBFile.exists(path):
            contents = LBFile.read(path)
            return self.execute(contents)
        else:
            LBEvent.exit("LBDB", f"Failed to import file: {path}")
            return False

    def listen(self, channel, callback):
        # Define runner function to poll for notifications
        def runner(channel, cursor):
            while True:
                if not select.select([self.link], [], [], 5) == ([], [], []):
                    self.link.poll()
                    while self.link.notifies:
                        notify = self.link.notifies.pop(0)
                        if notify.channel == channel:
                            callback(notify.payload)

        # Execute query with runner
        runner = partial(runner, channel=channel)
        self.execute(f"LISTEN {self.quote(channel)}", runner=runner)

    def notify(self, channel, payload):
        return self.execute(f"NOTIFY {self.quote(channel)}, %s", [payload])

    def quote(self, value):
        return psycopg2.extensions.quote_ident(value, self.link)

    def select(self, query, params=[]):
        options = {"cursor_factory": psycopg2.extras.RealDictCursor}
        runner = lambda cursor: cursor.fetchall()
        results = self.execute(query, params, options=options, runner=runner)
        if type(results) is list:
            return [dict(item) for item in results]
        elif type(results) is bool:
            return results
        else:
            LBEvent.warn("LBDB", f"Unhandled select result type: {type(results)}")

    def table_exists(self, tbname):
        results = self.select("SELECT 1 FROM information_schema.tables WHERE table_name = %s", [tbname])
        return len(results) == 1

    def table_schema(self, tbname):
        # Select
        query = """
            SELECT * FROM information_schema.columns
            WHERE table_name = %s AND table_schema = %s
            ORDER BY ordinal_position ASC
        """
        columns = self.select(query, [tbname, "public"])
        # Format
        default = lambda val: val.split("::")[0].strip("'") if type(val) == str else None
        parse = lambda column: {
            "default": default(column["column_default"]),
            "length": column["character_maximum_length"],
            "nullable": column["is_nullable"] == "YES",
            "type": column["data_type"],
        }
        return {column["column_name"]: parse(column) for column in columns}

    def types(self):
        # Postgres Column: timestamp -> Unix Timestamp
        psycopg2.extensions.register_type(
            psycopg2.extensions.new_type(
                psycopg2.extensions.PYDATETIME.values,
                "UNIX_TIMESTAMP",
                lambda value, cursor: dateutil.parser.parse(value).timestamp(),
            ),
            self.link,
        )
        # Postgres Column: timestamptz -> Unix Timestamp
        psycopg2.extensions.register_type(
            psycopg2.extensions.new_type(
                psycopg2.extensions.PYDATETIMETZ.values,
                "UNIX_TIMESTAMP_TZ",
                lambda value, cursor: dateutil.parser.parse(value).timestamp(),
            ),
            self.link,
        )


class LBDNS:
    @staticmethod
    def entrypoint():
        return LBDNS.host(LBDNS.root())

    @staticmethod
    def host(hostname):
        try:
            target, alts, addrs = socket.gethostbyname_ex(hostname)
        except Exception:
            # DNS lookup failed
            return False
        else:
            if target != hostname:
                # Points to another hostname
                # Record types: CNAME
                return target
            elif addrs:
                # Points to IP address(es)
                # Record types: A, AAAA
                return addrs[0]
            else:
                # No result
                return False

    @staticmethod
    def root():
        envs = {
            "local": "launchbox.run",
        }
        return envs.get(LBEnv.type(), envs["local"])

    @staticmethod
    def verify(hostname):
        # Check if hostname points at entrypoint
        return LBDNS.host(hostname) == LBDNS.entrypoint()


class LBDir:
    @staticmethod
    def compress(source_path, output_path):
        if LBDir.exists(source_path):
            result = LBCLI.run(
                ["tar", "-czf", output_path, "."],
                cwd=source_path,
            )
            return result.returncode == 0
        return False

    @staticmethod
    def create(path, name):
        dir_path = LBPath.join(path, name)
        if not LBDir.exists(dir_path):
            try:
                os.mkdir(dir_path)
                return True
            except Exception:
                LBEvent.warn("LBDir.create", f"Unable to create directory at path: {dir_path}")
        return False

    @staticmethod
    def create_random(path):
        name = LBUUID.uuid()
        if LBDir.create(path, name):
            return name
        return False

    @staticmethod
    def decompress(source_path, output_path):
        if LBFile.exists(source_path) and not LBDir.exists(output_path):
            if LBDir.create(LBPath.parent(output_path), LBPath.basename(output_path)):
                args = ["tar", "-xf", source_path, "-C", output_path]
                result = LBCLI.run(args)
                return result.returncode == 0
        return False

    @staticmethod
    def exists(path):
        if os.path.exists(path):
            return os.path.isdir(path)
        return False

    @staticmethod
    def move(source_path, target_path):
        if not LBDir.exists(source_path):
            return False
        if LBDir.exists(target_path):
            return False
        try:
            shutil.move(source_path, target_path)
        except Exception:
            LBEvent.warn("LBDir.move", f"Unable to move directory at path: {source_path} to path: {target_path}")
            return False
        else:
            return True

    @staticmethod
    def remove(path, name):
        dir_path = LBPath.join(path, name)
        if LBDir.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
            except Exception:
                LBEvent.warn("LBDir.remove", f"Unable to remove directory at path: {dir_path}")
            else:
                return True
        return False


class LBEnv:
    @staticmethod
    def copy():
        return os.environ.copy()

    @staticmethod
    def get(name, default=None):
        if value := os.getenv(name, False):
            return value
        elif default is None:
            LBEvent.exit("LBEnv", f"Requested environment variable is not set: {name}")
        return default

    @staticmethod
    def aws():
        return LBEnv.type() != "local"

    @staticmethod
    def local():
        return LBEnv.type() == "local"

    @staticmethod
    def git_branch():
        return LBEnv.get("GIT_BRANCH", "N/A")

    @staticmethod
    def git_sha():
        return LBEnv.get("GIT_SHA", "N/A")

    @staticmethod
    def type():
        if environment := LBEnv.get("ENVIRONMENT", False):
            return environment.lower()
        else:
            line1 = "Environment not specified, assuming: local."
            line2 = "Please add ENVIRONMENT=local to your .env file."
            LBEvent.warn("LBEnv", f"{line1} {line2}")
            return "local"


class LBEnvdir:
    @staticmethod
    def read(path):
        if not LBDir.exists(path):
            return None
        with envdir.open(path) as env:
            return dict(env.items())

    @staticmethod
    def write(path, vars):
        if not LBEnvdir.setup(path):
            return False
        with envdir.open(path) as env:
            for var_name, value in vars.items():
                env[var_name] = str(value)
        return True

    @staticmethod
    def setup(path):
        # Check
        if LBFile.exists(path):
            return False
        # Params
        parent = LBPath.parent(path)
        dirname = LBPath.basename(path)
        # Clean
        if LBDir.exists(path):
            LBDir.remove(parent, dirname)
        # Create
        return LBDir.create(parent, dirname)


class LBEvent:
    colors = {
        "complete": "green",
        "error": "red",
        "event": "blue",
        "exit": "red",
        "warn": "yellow",
    }

    @staticmethod
    def date():
        return datetime.datetime.now().strftime("%m/%d/%y %H:%M:%S %p")

    @staticmethod
    def format(source, kind, message, attrs):
        color = LBEvent.colors[kind]
        line1 = f"> {source} [{LBEvent.date()}]"
        line2 = f"| * [{kind.capitalize()}]: {message}"
        extra = [f"| - {key}: {value}" for key, value in attrs.items()]
        # Result
        return "\n".join([termcolor.colored(line, color) for line in [line1, line2, *extra]])

    @staticmethod
    def complete(source, message, attrs={}):
        print(LBEvent.format(source, "complete", message, attrs))

    @staticmethod
    def log(source, message, attrs={}):
        print(LBEvent.format(source, "event", message, attrs))

    @staticmethod
    def error(source, e, attrs={}):
        message = e if type(e) == str else repr(e)
        print(LBEvent.format(source, "error", message, attrs))

    @staticmethod
    def exit(source, message, attrs={}):
        sys.exit(LBEvent.format(source, "exit", message, attrs))

    @staticmethod
    def warn(source, message, attrs={}):
        print(LBEvent.format(source, "warn", message, attrs))


class LBFile:
    @staticmethod
    def copy(path, dest):
        shutil.copyfile(path, dest)

    @staticmethod
    def exists(path):
        if os.path.exists(path):
            return os.path.isfile(path)
        return False

    @staticmethod
    def from_template(path, dest, params):
        content = LBFile.read(path)
        output = Template(content).safe_substitute(params)
        LBFile.write(dest, output)

    @staticmethod
    def read(path, mode="r"):
        with open(path, mode) as fd:
            return fd.read()

    @staticmethod
    def read_json(path):
        content = LBFile.read(path)
        return json.loads(content)

    @staticmethod
    def read_yaml(path):
        with open(path, "r") as fd:
            try:
                return yaml.safe_load(fd)
            except Exception:
                pass

    @staticmethod
    def remove(path):
        try:
            os.remove(path)
        except Exception:
            return False
        else:
            return True

    @staticmethod
    def write(path, content, mode="w"):
        with open(path, mode) as fd:
            fd.write(content)

    @staticmethod
    def write_json(path, data):
        content = json.dumps(data)
        LBFile.write(path, content)


class LBPath:
    # Helpers
    @staticmethod
    def basename(path):
        path = os.path.normpath(path)
        return os.path.basename(path)

    @staticmethod
    def join(path1, path2):
        path1 = os.path.normpath(path1)
        path2 = path2.strip("/")
        return os.path.join(path1, path2)

    @staticmethod
    def list(path):
        return glob.glob(path)

    @staticmethod
    def parent(path):
        return str(pathlib.Path(path).parents[0])

    @staticmethod
    def script():
        return os.path.realpath(__file__)

    # Locations
    @staticmethod
    def app(path=""):
        base = LBPath.parent(LBPath.manage())
        return LBPath.join(base, path)

    @staticmethod
    def builds(path=""):
        base = LBPath.app("builds")
        return LBPath.join(base, path)

    @staticmethod
    def config(path=""):
        base = LBPath.app("config")
        return LBPath.join(base, path)

    @staticmethod
    def manage(path=""):
        base = LBPath.parent(LBPath.script())
        return LBPath.join(base, path)

    @staticmethod
    def nginx(path=""):
        base = LBPath.app("nginx")
        return LBPath.join(base, path)

    @staticmethod
    def plugins(path=""):
        base = LBPath.app("plugins")
        return LBPath.join(base, path)

    @staticmethod
    def runtimes(path=""):
        base = LBPath.app("runtimes")
        return LBPath.join(base, path)

    @staticmethod
    def services(path=""):
        base = LBPath.app("services")
        return LBPath.join(base, path)

    @staticmethod
    def sites(path=""):
        base = LBPath.app("sites")
        return LBPath.join(base, path)

    @staticmethod
    def uwsgi(path=""):
        base = LBPath.app("uwsgi")
        return LBPath.join(base, path)


class LBStack:
    @staticmethod
    def get(frame=1):
        try:
            stack = inspect.stack()
            frame = stack[frame]
            if parent := frame.frame.f_locals.get("self"):
                caller = f"{parent.__class__.__name__}.{frame.function}"
            else:
                caller = frame.function
        except Exception:
            return None
        else:
            return {
                "filename": frame.filename,
                "lineno": frame.lineno,
                "caller": caller,
            }


class LBURL:
    @staticmethod
    def base(url):
        parsed = LBURL.parse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    @staticmethod
    def basic_auth(url, username, password):
        for prefix in ["http://", "https://"]:
            if url.startswith(prefix):
                return url.replace(prefix, f"{prefix}{username}:{password}@")

    @staticmethod
    def join(base, path):
        if path:
            if not base.endswith("/"):
                base = f"{base}/"
            if path.startswith("/"):
                path = path[1:]
        return urllib.parse.urljoin(base, path)

    @staticmethod
    def netloc(url):
        return LBURL.parse(url).netloc

    @staticmethod
    def parse(url):
        return urllib.parse.urlparse(url)

    @staticmethod
    def path(url):
        return LBURL.parse(url).path

    @staticmethod
    def path_parts(url):
        return [part for part in LBURL.path(url).split("/") if len(part)]


class LBUUID:
    @staticmethod
    def uuid():
        return str(uuid.uuid4())
