# 역할: DTO↔ORM 변환, 쿼리/업서트 유즈케이스.
#
# 핵심: ON DUPLICATE KEY UPDATE 기반 idempotent upsert, 변경필드만 갱신, last_seen_at 스탬프.