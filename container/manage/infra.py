import boto3
import requests

from manage.util import LBEnv


class LBInfra:
    class current:
        @staticmethod
        def cluster():
            if LBEnv.local():
                return None
            elif metadata := LBInfra.current.metadata():
                if cluster_arn := metadata.get("Cluster"):
                    return LBInfra.util.shortname(cluster_arn)
            return False

        @staticmethod
        def identifier():
            if LBEnv.local():
                return "local"
            elif metadata := LBInfra.current.metadata():
                if task_arn := metadata.get("TaskARN"):
                    return LBInfra.util.shortname(task_arn)
            return False

        @staticmethod
        def metadata():
            if LBEnv.aws():
                if metadata_uri := LBEnv.get("ECS_CONTAINER_METADATA_URI_V4", False):
                    # Request
                    response = requests.get(f"{metadata_uri}/task", timeout=1)
                    if response.status_code == 200:
                        # Results
                        return response.json()
            return False

        @staticmethod
        def service():
            if LBEnv.local():
                return None
            elif metadata := LBInfra.current.metadata():
                if family := metadata.get("Family"):
                    return family
            return False

    class cluster:
        @staticmethod
        def describe():
            # Params
            cluster = LBInfra.current.cluster()
            tasks = LBInfra.cluster.list()
            # Check
            if LBEnv.local():
                return {identifier: {"cluster": cluster} for identifier in tasks}
            else:
                # ECS
                client = boto3.client("ecs")
                # Request
                response = client.describe_tasks(cluster=cluster, tasks=tasks)
                # Parse
                results = {}
                for item in response.get("tasks", []):
                    if task_arn := item.get("taskArn"):
                        task = LBInfra.util.shortname(task_arn)
                        results[task] = {
                            "az": item["availabilityZone"],
                            "cluster": cluster,
                            "service": item["group"].replace("service:", ""),
                            "created": item["createdAt"].timestamp() if "createdAt" in item else False,
                            "started": item["startedAt"].timestamp() if "startedAt" in item else False,
                            "status": {
                                "current": item["lastStatus"],
                                "desired": item["desiredStatus"],
                            },
                        }
                # Results
                return results

        @staticmethod
        def list():
            if LBEnv.local():
                return [LBInfra.current.identifier()]
            else:
                # ECS
                client = boto3.client("ecs")
                cluster = LBInfra.current.cluster()
                service = LBInfra.current.service()
                # Request
                response = client.list_tasks(cluster=cluster, serviceName=service)
                # Parse
                task_arns = response.get("taskArns", [])
                # Results
                return [LBInfra.util.shortname(item) for item in task_arns]

    class util:
        @staticmethod
        def shortname(arn):
            if type(arn) == str:
                return arn.split("/")[-1]
            return False
