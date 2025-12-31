from pymongo import MongoClient
from src.core.config import settings

def get_client():
    _client = None
    if _client is None:
        _client = MongoClient(settings.MONGODB_URI)
    return _client

def upsert_meta(title : str, author_name : str, description, keywords):
    """
       메타데이터 document를 upsert 한다.
       1) title + author_name 기준으로 document 존재하면
           - keywords(인자)가 있으면 keywords만 업데이트 후 해당 id 반환
           - keywords(인자) 없으면 기존 id 그대로 반환
       2) 존재하지 않으면 새 document 생성 후 Mongo ObjectId 반환
       """
    client = get_client()
    try:
        col = client[settings.MONGODB_DB][settings.MONGODB_META_COLLECTION]
        doc = {"title": title.strip(), "author_name": author_name.strip(), "description": description, "keywords": keywords or []}
        mongo_doc_id = col.find_one({"title": title, "author_name": author_name}, {"_id": 1}) or None

        if mongo_doc_id and keywords : return str(col.update_one({"_id": mongo_doc_id}, {"$set": {"keywords": keywords}}).upserted_id)
        elif mongo_doc_id : return str(mongo_doc_id['_id'])
        else : return str(col.insert_one(doc).inserted_id)
    finally:
        client.close()

def delete_meta(title, author_name):
    """
        테스트 목적 document 제거
    """
    client = get_client()
    try:
        col = client[settings.MONGODB_DB][settings.MONGODB_META_COLLECTION]
        col.delete_one({"title": title, "author_name": author_name})
    finally:
        client.close()