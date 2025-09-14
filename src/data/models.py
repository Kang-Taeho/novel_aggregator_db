# 엔티티:
# Platform(id, name, slug)
# Novel(id PK, platform_id FK, platform_item_id, title, author_name, status, genres JSON, tags JSON, cover_url, rating DECIMAL(3,2), last_seen_at, updated_at)
# Episode(id, novel_id FK, no, title, published_at, is_free)
# ScrapeJob(id, platform, scope, status, started_at, finished_at, stats_json)

# 인덱스:
# UNIQUE(platform_id, platform_item_id) (업서트 키)
# INDEX(title), INDEX(author_name), 필요 시 FULLTEXT(title, author_name)