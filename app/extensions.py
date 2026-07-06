from flask_login import LoginManager
from pymongo import MongoClient

login_manager = LoginManager()
login_manager.login_view = "auth.login"

mongo_client = None
mongo_db = None


def init_mongo(app):
    global mongo_client, mongo_db
    uri = app.config.get("MONGO_URI")
    db_name = app.config.get("MONGO_DB_NAME", "unmute_db")

    if not uri:
        raise RuntimeError("MONGO_URI is missing in .env")

    mongo_client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command("ping")  # fail fast if URI/network/auth is wrong
    mongo_db = mongo_client[db_name]
