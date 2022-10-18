from manage.util import LBDB, LBUUID


class LBAuth:
    # Cleanup outdated tokens (older than 1 day)
    @staticmethod
    def cleanup():
        with LBDB() as db:
            if db.connect(LBDB.core):
                query = """DELETE FROM auth WHERE "created" < (NOW() - INTERVAL '1 DAY')"""
                if db.execute(query):
                    return True

    # Create token for user
    @staticmethod
    def create(user_id):
        with LBDB() as db:
            if db.connect(LBDB.core):
                token = LBUUID.uuid()
                query = """INSERT INTO auth("user_id", "token") VALUES(%s, %s)"""
                if db.execute(query, [user_id, token]):
                    return token
        return False

    # Verify token
    @staticmethod
    def verify(token):
        with LBDB() as db:
            if db.connect(LBDB.core):
                query = """SELECT "user_id" FROM auth WHERE "token" = %s"""
                if results := db.select(query, [token]):
                    return results[0]["user_id"]
        return False
