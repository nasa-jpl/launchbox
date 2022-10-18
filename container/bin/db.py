from manage.util import LBCLI, LBEnv, LBEvent, LBPath

# Params
postgres_db = "lb"

postgres_host = LBEnv.get("POSTGRES_HOST")
postgres_port = LBEnv.get("POSTGRES_PORT")

postgres_user = LBEnv.get("POSTGRES_USER")
postgres_pass = LBEnv.get("POSTGRES_PASSWORD")

# Format
postgres_auth = f"{postgres_user}:{postgres_pass}"
postgres_url = f"{postgres_host}:{postgres_port}"

postgres_url = f"postgresql://{postgres_auth}@{postgres_url}/{postgres_db}"

# Log
LBEvent.log("cli.db", f"Opening connection to Postgres database: {postgres_db}")

# Run
LBCLI.run(["psql", postgres_url], cwd=LBPath.app())
