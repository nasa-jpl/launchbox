import re

import bcrypt
import bottle

from manage.result import LBError
from manage.util import LBDB
from models.auth import LBAuth


class LBUsers:
    # Create user
    @staticmethod
    def create(user_id, password):
        if LBUsers.get(user_id):
            return LBError("username-exists", "provided username already exists")
        if not LBUsers.valid(user_id):
            return LBError("username-invalid", "username contains invalid characters")
        with LBDB() as db:
            if db.connect(LBDB.core):
                # Check
                if password:
                    # Password
                    salt = bcrypt.gensalt()
                    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
                    # Construct
                    query = """
                        INSERT INTO users("user_id", "provider", "first_name", "last_name", "password")
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    args = [user_id, "", "", "", hashed.decode("utf-8")]
                    # Create user database records
                    if db.execute(query, args):
                        # Login
                        return LBUsers.login(user_id, password)
        return LBError("database", "database connection or query error")

    # Get user_id for authenticated user (if valid session)
    @staticmethod
    def current():
        # Get cookie
        if token := bottle.request.get_cookie("launchbox"):
            # Verify token is valid
            if user_id := LBAuth.verify(token):
                return user_id
        return False

    # Get user
    @staticmethod
    def get(user_id):
        with LBDB() as db:
            if db.connect(LBDB.core):
                query = """SELECT "user_id", "provider" FROM users WHERE "user_id" = %s"""
                if results := db.select(query, [user_id]):
                    return results[0]
        return False

    # Login user
    @staticmethod
    def login(user_id, password):
        # Get user
        if user := LBUsers.get(user_id):
            # Check password
            with LBDB() as db:
                if db.connect(LBDB.core):
                    query = """SELECT "password" FROM users WHERE "user_id" = %s"""
                    if results := db.select(query, [user_id]):
                        hashed = results[0]["password"].encode("utf-8")
                        if bcrypt.checkpw(password.encode("utf-8"), hashed):
                            # Generate token
                            if token := LBAuth.create(user_id):
                                # Set cookie
                                bottle.response.set_cookie("launchbox", token, path="/")
                                # Result
                                return user
        return LBError("credentials", "provided credentials are invalid")

    # Logout user
    @staticmethod
    def logout():
        bottle.response.delete_cookie("launchbox", path="/")

    # Validate user_id
    @staticmethod
    def valid(user_id):
        return re.match(r"^[A-Za-z0-9-]+$", user_id) is not None
