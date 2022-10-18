from manage.util import LBCLI, LBDir, LBEnv, LBPath


class python3:
    @classmethod
    def setup(cls, path):
        # Create python virtual env
        if cls.venv(path):
            # Required modules
            modules = ["pip", "setuptools", "wheel"]
            if cls.install(path, modules):
                return True

    @classmethod
    def action(cls, path, action, env={}):
        # Run user-provided phase action command
        if args := LBCLI.args(action):
            return cls.run(path, args, env)

    @classmethod
    def clean(cls, path):
        if args := LBCLI.args("find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete"):
            result = LBCLI.run(args, cwd=path)
            return result.returncode == 0

    @classmethod
    def install(cls, path, modules):
        # Install and upgrade python modules
        args = ["pip3", "install", "--upgrade", *modules]
        return cls.run(path, args)

    @classmethod
    def requirements(cls, path, reqs_path):
        # Install python3 modules from requirements.txt
        args = ["pip3", "install", "-r", reqs_path]
        return cls.run(path, args)

    @classmethod
    def run(cls, path, args, env={}):
        # Run command inside python virtual env
        if venv_path := cls.venv(path):
            env["PATH"] = f"{venv_path}/bin:{LBEnv.get('PATH')}"
            env["VIRTUAL_ENV"] = venv_path
            result = LBCLI.run(args, cwd=path, setenv=env)
            if result.returncode == 0:
                return True

    @classmethod
    def venv(cls, path):
        # Verify/create python virtual env
        dirname = "venv"
        venv_path = LBPath.join(path, dirname)
        if LBDir.exists(venv_path):
            return venv_path
        else:
            result = LBCLI.run(["python3", "-m", "venv", dirname], cwd=path)
            if result.returncode == 0:
                return venv_path
