from manage.config import LBConfig
from manage.git import LBGit, LBGithub
from manage.util import LBDB, LBDir, LBEnv, LBFile, LBPath
from models.deploys import LBDeploys
from models.services import LBServices
from runtimes import LBRuntime
from storage.s3 import LBS3
from sync.util import LBEC


class LBDeployServices:
    class complete:
        @staticmethod
        def check():
            with LBDB() as db:
                if db.connect(LBDB.core):
                    # Get latest complete service deployments by service_id
                    query = """
                        SELECT DISTINCT ON ("service_id") "service_id",
                        "deploy_id", "build", "status", "created"
                        FROM deploy_services
                        WHERE "status" = 'complete'
                        ORDER BY "service_id", "created" DESC
                    """
                    results = db.select(query)
                    # Check if query succeeded
                    if results is not False:
                        # Verify each deployment has been handled
                        for deploy_service in results:
                            # Params
                            deploy_id = deploy_service["deploy_id"]
                            service_id = deploy_service["service_id"]
                            build = deploy_service["build"]
                            # Check if service deployment folder exists
                            if not LBDeployServices.complete.exists(service_id, deploy_id):
                                # Get build archive
                                LBDeployServices.complete.get(service_id, deploy_id, build)
                                # Action
                                return LBEC.action
                        # No action
                        return LBEC.inaction
            # Connection or query failed
            return LBEC.failure

        @staticmethod
        def exists(service_id, deploy_id):
            path = LBDeploys.service.path(service_id, deploy_id)
            return LBDir.exists(path)

        @staticmethod
        def get(service_id, deploy_id, build):
            LBDeploys.service.actions.add(deploy_id, "complete", "Found complete service build", status="complete")
            # Create service dir (if needed)
            if not LBDir.exists(LBPath.services(service_id)):
                LBDir.create(LBPath.services(), service_id)
            # Params
            deploy_path = LBDeploys.service.path(service_id, deploy_id)
            archive_path = f"{deploy_path}.tar.gz"
            # Get build archive from S3
            action_get = LBDeploys.service.actions.add(deploy_id, "complete", "Retrieve service build from S3")
            if LBS3.object.get(bucket="builds", key=build, local_path=archive_path):
                LBDeploys.service.actions.complete(action_get)
                # Decompress build archive to service deploy path
                action_unpack = LBDeploys.service.actions.add(deploy_id, "complete", "Unpack service build archive")
                if LBDir.decompress(archive_path, deploy_path):
                    LBDeploys.service.actions.complete(action_unpack)
                    # Cleanup
                    action_clean = LBDeploys.service.actions.add(deploy_id, "complete", "Cleanup temporary files")
                    if LBFile.remove(archive_path):
                        LBDeploys.service.actions.complete(action_clean)
                        # Result
                        return True
                    else:
                        LBDeploys.service.actions.failed(action_clean)
                else:
                    LBDeploys.service.actions.failed(action_unpack)
            else:
                LBDeploys.service.actions.failed(action_get)

    class pending:
        @staticmethod
        def check():
            with LBDB() as db:
                if db.connect(LBDB.core, autocommit=False):
                    # Get latest pending service deployment
                    query = """
                        SELECT "deploy_id", "service_id", "commit_sha", "status", "created"
                        FROM deploy_services
                        WHERE "status" = 'pending'
                        ORDER BY "created" ASC
                        FOR UPDATE SKIP LOCKED LIMIT 1
                    """
                    results = db.select(query)
                    # Check if query succeeded
                    if results is not False:
                        # Check for results
                        if len(results) == 0:
                            # No action
                            return LBEC.inaction
                        else:
                            # Pending
                            deploy_service = results[0]
                            # Params
                            deploy_id = deploy_service["deploy_id"]
                            service_id = deploy_service["service_id"]
                            commit_sha = deploy_service["commit_sha"]
                            # Build
                            if LBDeployServices.pending.build(deploy_id, service_id, commit_sha):
                                if LBEnv.local():
                                    # Move to service folder
                                    build_key = LBDeployServices.pending.move(deploy_id, service_id)
                                else:
                                    # Upload to build bucket
                                    build_key = LBDeployServices.pending.put(deploy_id)
                            else:
                                # Build failed
                                build_key = None
                            # Cleanup
                            LBDeployServices.pending.cleanup(deploy_id)
                            # Format
                            build_key = build_key or ""
                            status = "complete" if build_key else "failed"
                            # Update pending row
                            query = """
                                UPDATE deploy_services SET "status" = %s, "build" = %s
                                WHERE "deploy_id" = %s
                            """
                            if db.execute(query, [status, build_key, deploy_id]):
                                if db.commit():
                                    # Action
                                    return LBEC.action
            # Connection or query failed
            return LBEC.failure

        @staticmethod
        def build(deploy_id, service_id, commit_sha):
            LBDeploys.service.actions.add(deploy_id, "pending", "Found pending service build", status="complete")
            # Params
            path = LBDeploys.service.build_path(deploy_id)
            # Get service
            action_service = LBDeploys.service.actions.add(deploy_id, "pending", "Get service status")
            if service := LBServices.get(service_id):
                LBDeploys.service.actions.complete(action_service)
                repo_url = service["repo_url"]
                branch = service["branch"]
                token = LBEnv.get("GIT_TOKEN")
                # Get repo
                action_repo = LBDeploys.service.actions.add(deploy_id, "pending", "Get repository status")
                if repo := LBGithub.repo(repo_url, token=token):
                    LBDeploys.service.actions.complete(action_repo)
                    clone_url = repo["clone_url"]
                    # Build folder
                    action_folder = LBDeploys.service.actions.add(deploy_id, "pending", "Prepare build folder")
                    if LBDeployServices.pending.start(deploy_id):
                        LBDeploys.service.actions.complete(action_folder)
                        # Clone
                        action_clone = LBDeploys.service.actions.add(deploy_id, "pending", "Get deploy commit")
                        if LBGit.get_commit(path, clone_url, branch, commit_sha):
                            LBDeploys.service.actions.complete(action_clone)
                            # Read launch.yaml
                            action_config = LBDeploys.service.actions.add(deploy_id, "pending", "Parse launch.yaml")
                            config = LBConfig(path)
                            # Validate
                            valid = config.validate()
                            if valid:
                                LBDeploys.service.actions.complete(action_config)
                            else:
                                LBDeploys.service.actions.failed(
                                    action_config,
                                    {"error": valid.data},
                                )
                                return False
                            # Runtime: setup
                            action_runtime = LBDeploys.service.actions.add(deploy_id, "pending", "Setup runtime")
                            if LBRuntime.python3.setup(path):
                                LBDeploys.service.actions.complete(action_runtime)
                                # Phase: Setup
                                for action in config.phases.get("setup", []):
                                    action_step = LBDeploys.service.actions.add(deploy_id, "pending", action)
                                    if LBRuntime.python3.action(path, action):
                                        LBDeploys.service.actions.complete(action_step)
                                    else:
                                        LBDeploys.service.actions.failed(action_step)
                                        return False
                                # Runtime: clean
                                LBRuntime.python3.clean(path)
                                # Result
                                return True
                            else:
                                LBDeploys.service.actions.failed(action_runtime)
                        else:
                            LBDeploys.service.actions.failed(action_clone)
                    else:
                        LBDeploys.service.actions.failed(action_folder)
                else:
                    LBDeploys.service.actions.failed(action_repo)

        @staticmethod
        def cleanup(deploy_id):
            path = LBDeploys.service.build_path(deploy_id)
            if LBDir.exists(path):
                LBDir.remove(LBPath.parent(path), LBPath.basename(path))

        @staticmethod
        def move(deploy_id, service_id):
            # Prepare
            build_path = LBDeploys.service.build_path(deploy_id)
            deploy_path = LBDeploys.service.path(service_id, deploy_id)
            # Prepare
            if LBDir.exists(deploy_path):
                LBDir.remove(LBPath.parent(deploy_path), LBPath.basename(deploy_path))
            # Create service dir (if needed)
            if not LBDir.exists(LBPath.services(service_id)):
                LBDir.create(LBPath.services(), service_id)
            # Move
            LBDir.move(build_path, deploy_path)
            LBDeploys.service.actions.add(deploy_id, "complete", "Local only: Deploy build folder", status="complete")
            # Result
            return "local"

        @staticmethod
        def start(deploy_id):
            # Cleanup any past builds
            LBDeployServices.pending.cleanup(deploy_id)
            # Create build dir
            path = LBDeploys.service.build_path(deploy_id)
            if LBDir.create(LBPath.parent(path), LBPath.basename(path)):
                return True

        @staticmethod
        def put(deploy_id):
            # Params
            build_key = f"{deploy_id}.tar.gz"
            build_path = LBDeploys.service.build_path(deploy_id)
            archive_path = f"{build_path}.tar.gz"
            # Compress build folder
            action_compress = LBDeploys.service.actions.add(deploy_id, "pending", "Compress build folder")
            if LBDir.compress(build_path, archive_path):
                LBDeploys.service.actions.complete(action_compress)
                # Upload build archive to S3
                action_put = LBDeploys.service.actions.add(deploy_id, "pending", "Upload build to S3")
                if LBS3.object.put(bucket="builds", key=build_key, local_path=archive_path):
                    LBDeploys.service.actions.complete(action_put)
                    # Cleanup archive
                    action_clean = LBDeploys.service.actions.add(deploy_id, "pending", "Cleanup")
                    LBFile.remove(archive_path)
                    LBDeploys.service.actions.complete(action_clean)
                    # Result
                    return build_key
                else:
                    LBDeploys.service.actions.failed(action_put)
            else:
                LBDeploys.service.actions.failed(action_compress)
