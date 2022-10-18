from packaging import version

from manage.git import LBGit, LBGithub
from manage.util import LBDir, LBFile, LBPath
from models.plugins import LBPlugins
from runtimes.python3.runtime import python3
from sync.network.plugins import LBNetworkPlugins
from sync.util import LBEC


class LBDeployPlugins:
    class pending:
        @staticmethod
        def check():
            if plugins := LBPlugins.list():
                for plugin in plugins:
                    plugin_id = plugin["plugin_id"]
                    # Install
                    if not LBDeployPlugins.pending.exists(plugin_id):
                        if LBDeployPlugins.pending.create(plugin):
                            LBNetworkPlugins.update()
                            # Action
                            return LBEC.action
                    # Update
                    else:
                        if config := LBDeployPlugins.pending.config(plugin_id):
                            # Check for update
                            if version.parse(config["version"]) < version.parse(plugin["version"]):
                                if LBDeployPlugins.pending.cleanup(plugin_id):
                                    if LBDeployPlugins.pending.create(plugin):
                                        LBNetworkPlugins.update()
                                        # Action
                                        return LBEC.action
            # No action
            return LBEC.inaction

        @staticmethod
        def cleanup(plugin_id):
            if LBDeployPlugins.pending.exists(plugin_id):
                LBDir.remove(LBPath.plugins(), plugin_id)
                return True
            return False

        @staticmethod
        def config(plugin_id):
            path_to_yaml = LBPath.plugins(plugin_id) + "/plugin.yaml"
            if config := LBFile.read_yaml(path_to_yaml):
                return config["plugin"]

        @staticmethod
        def create(plugin):
            commit_sha = None
            for commit in LBGithub.commits(plugin["repo_url"], plugin["branch"], token=LBPlugins.token):
                # Latest commit
                commit_sha = commit["sha"]
                break
            # Verify commit
            if LBGithub.commit(plugin["repo_url"], commit_sha, token=LBPlugins.token):
                # Params
                plugin_path = LBPath.plugins(plugin["plugin_id"])
                # Prepare
                LBDir.create(LBPath.plugins(), plugin["plugin_id"])
                repo = LBGithub.repo(plugin["repo_url"], token=LBPlugins.token)
                # Clone files
                if LBGit.get_commit(plugin_path, repo["clone_url"], plugin["branch"], commit_sha):
                    # Runtime
                    python3.setup(plugin_path)
                    python3.requirements(plugin_path, plugin["requirements"])
                    return True
            return False

        @staticmethod
        def exists(plugin_id):
            return LBDir.exists(LBPath.plugins(plugin_id))
