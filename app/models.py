from datetime import datetime, timezone
from bson.objectid import ObjectId
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import extensions  # IMPORTANT: module import, not value import


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin):
    def __init__(self, data):
        self.data = data
        self.id = str(data["_id"])
        self.email = data["email"]
        self.name = data.get("name", "User")

    @staticmethod
    def collection():
        if extensions.mongo_db is None:
            raise RuntimeError("MongoDB not initialized. Check MONGO_URI and app startup.")
        return extensions.mongo_db["users"]

    @staticmethod
    def create(name, email, password):
        col = User.collection()
        email = email.strip().lower()
        if col.find_one({"email": email}):
            return None
        doc = {
            "name": name.strip(),
            "email": email,
            "password_hash": generate_password_hash(password),
            "created_at": utcnow(),
        }
        inserted = col.insert_one(doc)
        doc["_id"] = inserted.inserted_id
        return User(doc)

    @staticmethod
    def get_by_email(email):
        doc = User.collection().find_one({"email": email.strip().lower()})
        return User(doc) if doc else None

    @staticmethod
    def get_by_id(user_id):
        try:
            doc = User.collection().find_one({"_id": ObjectId(user_id)})
            return User(doc) if doc else None
        except Exception:
            return None

    def verify_password(self, password):
        return check_password_hash(self.data["password_hash"], password)
