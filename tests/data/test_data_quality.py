# src/data/test_data_quality.py
from __future__ import annotations
from datetime import datetime
from pathlib import Path

import pandas as pd
from pymongo.collection import Collection
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.core.config import settings
from src.data.database import SessionLocal
from src.data.mongo import get_client
from src.data.models import JobRun


def collect_quality(session: Session, collection : Collection) -> dict:
    """
    플랫폼별/전체 품질 지표를 MySQL, MongoDB에서 수집.
    """
    pds_dict : dict = {
        "outlier_pd": pd.DataFrame(),
        "missing_pd": pd.DataFrame(),
        "dup_des_pd": pd.DataFrame(),
        "dup_plf_pd": pd.DataFrame(),
        "mysql_only_pd": pd.DataFrame(),
        "mongo_only_pd": pd.DataFrame()
    }

    # 총 작품 수
    total_num_dict : dict = {
    "total_novels" : session.execute(text("SELECT COUNT(*) FROM novels")).scalar_one(),
    "total_novel_sources" : session.execute(text("SELECT COUNT(*) FROM novel_sources")).scalar_one(),
    "total_novel_meta" : collection.count_documents({})
    }
    # ---------------- 1) 이상치 : NULL or 0 값 ----------------
    dic = {}
    mysql_query =  text("""
        SELECT 
        SUM(CASE WHEN author_name IS NULL THEN 1 ELSE 0 END) / :total AS author_outlier_ratio,
        SUM(CASE WHEN genre IS NULL THEN 1 ELSE 0 END) / :total AS genre_outlier_ratio,
        SUM(CASE WHEN mongo_doc_id IS NULL THEN 1 ELSE 0 END) / :total AS mongo_outlier_ratio
        FROM novels
    """)
    col1 =session.execute(mysql_query,{"total" : total_num_dict["total_novels"]}).mappings().one()
    dic.update(col1)
    mysql_query = text("""
        SELECT 
        SUM(CASE WHEN episode_count IS NOT NULL AND episode_count < 0 THEN 1 ELSE 0 END) / :total AS episode_outlier_ratio,
        SUM(CASE WHEN view_count IS NOT NULL AND view_count < 0 THEN 1 ELSE 0 END) / :total AS view_outlier_ratio
        FROM novel_sources
    """)
    col2 = session.execute(mysql_query, {"total": total_num_dict["total_novel_sources"]}).mappings().one()
    dic.update(col2)
    mongo_cond = {
        "$or": [
            {"description": None},
            {"description": {"$exists": False}}
        ]
    }
    doc1 = collection.count_documents(mongo_cond)
    col3 = {"description_outlier_ratio": doc1 / total_num_dict["total_novel_meta"]}
    dic.update(col3)
    pds_dict["outlier_pd"] = pd.DataFrame([dic])


    # ---------------- 2) 결측치 : KP, NS ----------------
    row1 = (
        session.query(JobRun.metrics_json)
        .filter(JobRun.platform == "KP")
        .order_by(JobRun.finished_at.desc())
        .limit(1)
        .one()
    )
    metrics_json1 = row1.metrics_json
    metrics_json1["platform_slug"] = "KP"
    row2 = (
        session.query(JobRun.metrics_json)
        .filter(JobRun.platform == "NS")
        .order_by(JobRun.finished_at.desc())
        .limit(1)
        .one()
    )
    metrics_json2 = row2.metrics_json
    metrics_json2["platform_slug"] = "NS"
    pds_dict["missing_pd"] = pd.DataFrame([metrics_json1,metrics_json2])

    # ---------------- 3).1 중복 : description 중복  ----------------
    mongo_pipeline = [
    {
        "$group": {
            "_id": { "$trim": { "input": "$description" } },
            "count": { "$sum": 1 }
        }
    },
    {
        "$match": {
            "count": { "$gt": 1 }
        }
    },
    {
        "$group": {
            "_id": "$count",
            "groups": { "$sum": 1 }
        }
    },
    {
        "$project": {
            "_id": 0,
            "duplicate_numbers": "$_id",
            "counts": "$groups"
        }
    },
    { "$sort": { "duplicate_numbers": 1 } }
    ]
    docs = collection.aggregate(mongo_pipeline)
    pds_dict["dup_des_pd"] = pd.DataFrame(list(docs))

    # ---------------- 3).2 중복 : 플랫폼 중복 소설  ----------------
    mysql_query = text("""
                    SELECT dup_count, COUNT(*) AS group_count
                    FROM(
                        SELECT novel_id, COUNT(*) AS dup_count
                        FROM novel_sources
                        GROUP BY novel_id
                        HAVING COUNT(*) > 1 ) t
                    GROUP BY dup_count 
                """)
    rows = session.execute(mysql_query).mappings().all()
    pds_dict["dup_plf_pd"] = pd.DataFrame(rows)

    # ---------------- 4) Rule 위반 : mysql,mongodb 제약  ----------------
    mysql_query = text("""
                        SELECT mongo_doc_id, 
                        title AS MySQL_title , 
                        author_name AS MySQL_author
                        FROM novels
                    """)
    rows = session.execute(mysql_query).mappings().all()
    mysql_df = pd.DataFrame(rows)
    if not mysql_df.empty:
        mysql_df["mongo_doc_id"] = mysql_df["mongo_doc_id"].astype(str)
    mongo_pipeline =[
        {
            "$project": {
                 "_id": 0,
                "mongo_doc_id": { "$toString": "$_id" },
                "Mongo_title": "$title",
                "Mongo_author" : "$author_name"
            }
        }
    ]
    docs = collection.aggregate(mongo_pipeline)
    mongo_df = pd.DataFrame(list(docs))

    merged = pd.merge(
        mysql_df,
        mongo_df,
        how="outer",
        on="mongo_doc_id",
        indicator=True
    )
    pds_dict["mysql_only_pd"] = merged[merged["_merge"] == "left_only"].copy()
    pds_dict["mongo_only_pd"] = merged[merged["_merge"] == "right_only"].copy()
    return pds_dict, total_num_dict

def render_markdown(pds_dict : dict, total_num_dict : dict) -> str:
    # "outlier_pd": pd.DataFrame(),
    # "missing_pd": pd.DataFrame(),
    # "dup_des_pd": pd.DataFrame(),
    # "dup_plf_pd": pd.DataFrame(),
    # "mysql_only_pd": pd.DataFrame(),
    # "mongo_only_pd": pd.DataFrame()
    lines: list[str] = []
    today = datetime.now().strftime("%Y%m%d")

    lines.append("# Data Quality Report")
    lines.append("")
    lines.append(f"- 생성시간 : `{today}`")
    lines.append(f"- 대상 데이터 셋 : (mysql) novels({total_num_dict['total_novels']}), novel_sources({total_num_dict['total_novel_sources']}), job_runs")
    lines.append(f"-                (mongodb) novel_meta({total_num_dict['total_novel_meta']})")
    lines.append("")
    lines.append("## 이상치 통계")
    lines.append(pds_dict["outlier_pd"].to_markdown(index=False))
    lines.append("")
    lines.append("## 결측치 비율")
    lines.append(pds_dict["missing_pd"].to_markdown(index=False))
    lines.append("")
    lines.append("## 중복 비율")
    lines.append("### description 중복")
    lines.append(pds_dict["dup_des_pd"].to_markdown(index=False))
    lines.append("")
    lines.append("### 플랫폼 중복 소설 (현재 KP,NS)")
    lines.append(pds_dict["dup_plf_pd"].to_markdown(index=False))
    lines.append("")
    lines.append("## Rule 위반 (매핑 안 된 것들)")
    lines.append("### MySQL만 존재")
    lines.append(pds_dict["mysql_only_pd"].to_markdown(index=False))
    lines.append("")
    lines.append("### MongoDB만 존재")
    lines.append(pds_dict["mongo_only_pd"].to_markdown(index=False))
    lines.append("")
    return "\n".join(lines)

def test_data_quality_report():
    """
    JSON + Markdown 리포트를 생성
    """
    c = get_client()
    s = SessionLocal()
    try:
        collection = c[settings.MONGODB_DB][settings.MONGODB_META_COLLECTION]
        pds_dict, total_num_dict = collect_quality(s, collection)
        Path("./tests/reports/data_quality_report.md").write_text(render_markdown(pds_dict, total_num_dict), encoding="utf-8")
    finally:
        c.close()
        s.close()
