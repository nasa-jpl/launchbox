import nginx.config.api
import nginx.config.helpers

from .util import LBCLI, LBDir, LBEvent, LBFile, LBPath


class LBNetwork:
    # Nginx
    class nginx:
        # Certs
        class certs:
            @staticmethod
            def create(hostname, contents):
                # Clean up any existing certificate
                LBNetwork.nginx.certs.reset(hostname)
                # Write certificate to file
                cert_path = LBPath.nginx(f"certs/{hostname}.crt")
                LBFile.write(cert_path, contents)
                # Result
                return cert_path

            @staticmethod
            def reset(hostname):
                cert_path = LBPath.nginx(f"certs/{hostname}.crt")
                if LBFile.exists(cert_path):
                    LBFile.remove(cert_path)

            @staticmethod
            def reset_all():
                for cert_path in LBPath.list(LBPath.nginx("certs/*.crt")):
                    LBFile.remove(cert_path)

        # Server
        class server:
            def __init__(self):
                # Config
                self.description = None
                self.headers = {}
                self.hostnames = set()
                self.includes = set()
                self.vars = {}
                # Block
                self.block = nginx.config.api.Section("server")

            def build(self):
                block = str(self.block).strip()
                if self.description:
                    return f"# {self.description}\n{block}\n"
                return f"{block}\n"

            def add_header(self, name, value, always=False):
                # Format
                options = {
                    "always": always,
                }
                self.headers[name] = self.format_value(value, options, quote=True)
                # Set
                headers = [f"{key} {self.headers[key]}" for key in sorted(self.headers.keys())]
                self.block.options["add_header"] = nginx.config.helpers.duplicate_options("add_header", headers)

            def add_hostname(self, hostname):
                if hostname:
                    self.hostnames.add(hostname)
                    self.block.options["server_name"] = " ".join(sorted(self.hostnames))
                else:
                    LBEvent.warn("LBNetwork.nginx.server", "Unable to add empty hostname")

            def format_value(self, value, options, quote=False):
                # Format Nginx directive value and associated options
                enabled = [key for key, value in options.items() if value]
                value = f'"{str(value)}"' if quote else str(value)
                return " ".join([value, *enabled])

            def include(self, file_path):
                if LBFile.exists(file_path):
                    # Add
                    self.includes.add(file_path)
                    # Set
                    includes = sorted(self.includes)
                    self.block.options["include"] = nginx.config.helpers.duplicate_options("include", includes)
                else:
                    LBEvent.warn(
                        "LBNetwork.nginx.server",
                        f"Unable to include: path invalid ({file_path})",
                    )

            def include_routes(self, name):
                self.include(LBPath.nginx(f"routes/{name}.conf"))

            def listen(self, port, ssl_cert=False, proxy=False, default=False):
                # Listener
                options = {
                    "ssl": ssl_cert,
                    "http2": proxy,
                    "proxy_protocol": proxy,
                    "default_server": default,
                }
                self.block.options["listen"] = self.format_value(port, options)

                # Optional: SSL
                if ssl_cert:
                    if LBFile.exists(ssl_cert):
                        # Security
                        self.add_header("Cross-Origin-Opener-Policy", "same-origin", always=True)
                        self.add_header("Strict-Transport-Security", "max-age=31536000", always=True)
                        # SSL: Certificate/Key
                        self.block.options["ssl_certificate"] = ssl_cert
                        self.block.options["ssl_certificate_key"] = ssl_cert
                        # SSL: Parameters
                        dhparam = LBPath.nginx("files/dhparam.pem")
                        if LBFile.exists(dhparam):
                            self.block.options["ssl_dhparam"] = dhparam
                    else:
                        LBEvent.warn(
                            "LBNetwork.nginx.server",
                            f"Unable to add ssl_cert - path invalid: {ssl_cert}",
                        )

            def loc_static(self, route, path):
                # Add static location route
                location = nginx.config.api.Location(route)
                # Check path
                if LBDir.exists(path):
                    if not path.endswith("/"):
                        path = f"{path}/"
                location.options["alias"] = path
                self.block.sections.add(location)

            def loc_uwsgi(self, route, vassal, rewrite=False):
                # Add uWSGI location route
                location = nginx.config.api.Location(route)
                if rewrite:
                    # Optional: Rewrite forwarded path to remove route
                    location.options["rewrite"] = f"^{route}(.*) /$1 break"
                location.options["include"] = "uwsgi_params"
                location.options["uwsgi_pass"] = LBNetwork.uwsgi.vassals.socket(vassal)
                self.block.sections.add(location)

            def redirect(self, target):
                self.block.options["return"] = f"302 {target}"

            def set_var(self, name, value):
                self.vars[name] = value
                variables = [f'${key} "{self.vars[key]}"' for key in sorted(self.vars.keys())]
                self.block.options["set"] = nginx.config.helpers.duplicate_options("set", variables)

        # Sites
        class sites:
            @staticmethod
            def create(name, servers):
                # Params
                site_path = LBPath.nginx(f"sites/{name}.conf")
                # Build contents from server blocks
                built = [server.build() for server in servers]
                contents = "\n".join(built)
                # Write contents to site file
                LBFile.write(site_path, contents)

            @staticmethod
            def reload():
                LBCLI.run(["service", "nginx", "reload"])

            @staticmethod
            def reset(name):
                site_path = LBPath.nginx(f"sites/{name}.conf")
                if LBFile.exists(site_path):
                    LBFile.remove(site_path)

            @staticmethod
            def reset_all():
                for site_path in LBPath.list(LBPath.nginx("sites/*.conf")):
                    LBFile.remove(site_path)

    # uWSGI
    class uwsgi:
        # Vassals
        class vassals:
            @staticmethod
            def create(name, chdir, plugin, module, envdir=None, venv=None):
                template_path = LBPath.uwsgi("files/template.ini")
                vassal_path = LBPath.uwsgi(f"vassals/{name}.ini")
                options = {
                    "chdir": chdir,
                    "envdir": envdir,
                    "venv": venv,
                    "plugin": plugin,
                    "module": module,
                }
                config = "\n".join([f"{key} = {value}" for key, value in options.items() if value])
                LBFile.from_template(template_path, vassal_path, {"config": config})

            @staticmethod
            def reload():
                LBCLI.run(["pkill", "--signal", "SIGHUP", "-x", "uwsgi"])

            @staticmethod
            def reset(name):
                vassal_path = LBPath.uwsgi(f"vassals/{name}.ini")
                if LBFile.exists(vassal_path):
                    LBFile.remove(vassal_path)

            @staticmethod
            def reset_all():
                for vassal_path in LBPath.list(LBPath.uwsgi("vassals/*.ini")):
                    LBFile.remove(vassal_path)

            @staticmethod
            def reset_plugins():
                for vassal_path in LBPath.list(LBPath.uwsgi("vassals/plugin_*.ini")):
                    if LBFile.exists(vassal_path):
                        LBFile.remove(vassal_path)

            @staticmethod
            def reset_site(site_id):
                for vassal_path in LBPath.list(LBPath.uwsgi(f"vassals/{site_id}_*.ini")):
                    if LBFile.exists(vassal_path):
                        LBFile.remove(vassal_path)

            @staticmethod
            def socket(name):
                path = LBPath.uwsgi(f"sockets/{name}.sock")
                return f"unix:{path}"
