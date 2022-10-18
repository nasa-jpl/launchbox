import base64

import cachetools.func
import requests
import yaml

from manage.result import LBError

from .util import LBCLI, LBURL, LBEvent, LBPath


class LBGit:
    @staticmethod
    def clean(path):
        result = LBCLI.run(["rm", "-rf", ".git"], cwd=path)
        return result.returncode == 0

    @staticmethod
    def clone(path, repo_url, branch):
        args = [
            "git",
            "clone",
            repo_url,
            LBPath.basename(path),
            "--branch",
            branch,
            "--single-branch",
        ]
        result = LBCLI.run(args, cwd=LBPath.parent(path))
        return result.returncode == 0

    @staticmethod
    def get_commit(path, repo_url, branch, commit_sha):
        # Clone repo
        if not LBGit.clone(path, repo_url, branch):
            return False
        # Reset head
        if not LBGit.reset(path, commit_sha):
            return False
        # Check head
        if LBGit.head(path) != commit_sha:
            return False
        # Clean
        if not LBGit.clean(path):
            return False
        # Result
        return True

    @staticmethod
    def head(path):
        args = ["git", "rev-parse", "HEAD"]
        result = LBCLI.run(args, cwd=path, output=True)
        if result.returncode == 0:
            return result.stdout.decode("utf-8").strip("\n")

    @staticmethod
    def reset(path, commit):
        args = ["git", "reset", "--hard", commit]
        result = LBCLI.run(args, cwd=path)
        return result.returncode == 0


class LBGithub:
    @staticmethod
    def branches(repo_url, token=None):
        repo = LBGithub.parse.repo_url(repo_url)
        if response := LBGithub.API.query(repo, resource="branches", token=token):
            return [LBGithub.parse.branch(item) for item in response]

    @staticmethod
    def commit(repo_url, commit_sha, token=None):
        repo = LBGithub.parse.repo_url(repo_url)
        if response := LBGithub.API.query(repo, resource=f"commits/{commit_sha}", token=token):
            return LBGithub.parse.commit(response)

    @staticmethod
    @cachetools.func.ttl_cache(ttl=20)
    def commits(repo_url, branch=None, token=None):
        # Prepare
        repo = LBGithub.parse.repo_url(repo_url)
        params = {"sha": branch} if branch else {}
        # Call
        if response := LBGithub.API.query(repo, resource="commits", params=params, token=token):
            return [LBGithub.parse.commit(item) for item in response]

    @staticmethod
    def content(repo_url, path=None, branch=None, token=None):
        repo = LBGithub.parse.repo_url(repo_url)
        params = {"ref": branch} if branch else {}
        if response := LBGithub.API.query(repo, resource=f"contents/{path}", params=params, token=token):
            if type(response) is dict:
                return LBGithub.parse.content(response)

    @staticmethod
    def repo(repo_url, token=None):
        try:
            repo = LBGithub.parse.repo_url(repo_url)
            response = LBGithub.API.query(repo, token=token)
            return LBGithub.parse.repo(response)
        except Exception:
            LBError("LBGithub.repo", "Error querying repo", log_level="warn")
            return False

    class parse:
        @staticmethod
        def branch(data):
            return {
                "name": data["name"],
                "sha": data["commit"]["sha"],
                "url": data["commit"]["url"],
            }

        @staticmethod
        def commit(data):
            return {
                "sha": data["sha"],
                "date": data["commit"]["author"]["date"],
                "message": data["commit"]["message"],
                "author": {
                    "id": data["author"]["login"],
                    "type": str(data["author"]["type"]).lower(),
                    "name": data["commit"]["author"]["name"],
                    "avatar": data["author"]["avatar_url"],
                    "email": data["commit"]["author"]["email"],
                    "url": data["author"]["html_url"],
                },
                "url": data["html_url"],
            }

        @staticmethod
        def content(data):
            if content := yaml.safe_load(base64.b64decode(data["content"])):
                return content

        @staticmethod
        def repo(data):
            results = {
                "name": data["name"],
                "description": data["description"],
                "url": data["html_url"],
                "default_branch": data["default_branch"],
                "owner": {
                    "name": data["owner"]["login"],
                    "type": data["owner"]["type"].lower(),
                },
            }
            if clone_token := data.get("temp_clone_token"):
                results["clone_url"] = LBURL.basic_auth(data["clone_url"], "oauth2", clone_token)
            else:
                results["clone_url"] = data["clone_url"]
            return results

        @staticmethod
        def repo_url(url):
            # Clean: Scheme
            for prefix in ["http://", "https://", "ssh://"]:
                if url.startswith(prefix):
                    url = url[len(prefix) :]
            # Clean: Separator
            if ":" in url.split("/")[0]:
                url = url.replace(":", "/", 1)
            # Clean: End
            if url.endswith(".git"):
                url = url[:-4]
            # Components
            parts = url.split("/")
            if len(parts) > 2:
                # Clean: Username
                if "@" in parts[0]:
                    parts[0] = parts[0].split("@")[1]
                # Result
                return {
                    "host": parts[0],
                    "owner": parts[1],
                    "name": parts[2],
                }

    class API:
        @staticmethod
        def endpoint(repo, resource):
            # Determine
            if repo["host"] == "github.com":
                base = f"api.{repo['host']}"
            else:
                base = f"{repo['host']}/api/v3"
            # Compose
            url = f"https://{base}/repos/{repo['owner']}/{repo['name']}"
            return LBURL.join(url, resource)

        @staticmethod
        def headers(token):
            results = {
                "Accept": "application/vnd.github+json",
            }
            if token:
                results["Authorization"] = f"token {token}"
            return results

        @staticmethod
        def params(data):
            if type(data) is dict:
                defaults = {
                    "per_page": 30,
                }
                return {**data, **defaults}
            else:
                LBEvent.warn("LBGithub.API.params", "Provided params must be type: dict")

        @staticmethod
        def query(repo, resource=None, params={}, token=None):
            url = LBGithub.API.endpoint(repo, resource)
            headers = LBGithub.API.headers(token)
            params = LBGithub.API.params(params)
            # Call
            response = requests.get(url, headers=headers, params=params, timeout=15)
            # Results
            if response.status_code == 200:
                try:
                    payload = response.json()
                except Exception:
                    LBEvent.error("LBGithub.API", "Query: Unable to decode response JSON")
                    return False
                else:
                    return payload
            else:
                LBEvent.warn(
                    "LBGithub.API",
                    f"Query: Invalid response [code: {response.status_code}]",
                )
                return False
