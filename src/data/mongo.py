from pymongo import MongoClient
from src.core.config import settings

def get_client():
    _client = None
    if _client is None:
        _client = MongoClient(settings.MONGODB_URI)
    return _client

def upsert_meta(title, author_name, description, keywords):
    col = get_client()[settings.MONGODB_DB][settings.MONGODB_META_COLLECTION]
    doc = {"title": title, "author_name": author_name, "description": description, "keywords": keywords or []}
    mongo_doc_id = col.find_one({"title": title, "author_name": author_name}, {"_id": 1}) or None

    if mongo_doc_id and keywords : return str(col.update_one({"_id": mongo_doc_id}, {"$set": {"keywords": keywords}}).upserted_id)
    elif mongo_doc_id : return str(mongo_doc_id['_id'])
    else : return str(col.insert_one(doc).inserted_id)
