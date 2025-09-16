from pymongo import MongoClient
from bson import ObjectId
from src.core.config import settings

_client = None
def get_client():
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGODB_URI)
    return _client

def upsert_meta(title, author_name, description, keywords, mongo_doc_id):
    col = get_client()[settings.MONGODB_DB][settings.MONGODB_META_COLLECTION]
    doc = {"title": title, "author_name": author_name, "description": description, "keywords": keywords or []}
    if mongo_doc_id:
        col.update_one({"_id": ObjectId(mongo_doc_id)}, {"$set": doc}, upsert=True)
        return mongo_doc_id
    return str(col.insert_one(doc).inserted_id)
