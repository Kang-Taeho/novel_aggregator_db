CREATE DATABASE IF NOT EXISTS novel_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE novel_db;

CREATE TABLE IF NOT EXISTS platforms (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(50)  NOT NULL,
  UNIQUE KEY uq_platform_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO platforms (name, slug) VALUES
  ('KakaoPage',   'KP'),
  ('Naver Series','NS'),
  ('Munpia',      'MP')
ON DUPLICATE KEY UPDATE name = VALUES(name);

CREATE TABLE IF NOT EXISTS novels (
  id                  INT AUTO_INCREMENT PRIMARY KEY,
  title               VARCHAR(200) NOT NULL,
  author_name         VARCHAR(100) NULL,
  genre               VARCHAR(100) NULL,
  age_rating          ENUM('ALL','12','15','19') NOT NULL DEFAULT 'ALL',
  completion_status   ENUM('ongoing','completed','hiatus','unknown') NOT NULL DEFAULT 'unknown',
  mongo_doc_id        CHAR(24) NULL,
  normalized_title    VARCHAR(200) GENERATED ALWAYS AS (LOWER(TRIM(title))) STORED,
  normalized_author   VARCHAR(100) GENERATED ALWAYS AS (LOWER(TRIM(COALESCE(author_name,'')))) STORED,
  UNIQUE KEY uq_canonical (normalized_title, normalized_author),
  KEY idx_mongo_doc (mongo_doc_id),
  created_at          DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at          DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS novel_sources (
  id                 INT AUTO_INCREMENT PRIMARY KEY,
  novel_id           INT NOT NULL,
  platform_id        INT NOT NULL,
  platform_item_id   VARCHAR(200) NOT NULL,
  episode_count      INT UNSIGNED NULL,
  first_episode_date DATE NULL,
  view_count         BIGINT UNSIGNED NULL,
  UNIQUE KEY uq_platform_item (platform_id, platform_item_id),
  KEY idx_novel_platform (novel_id, platform_id),
  CONSTRAINT fk_ns_novel FOREIGN KEY (novel_id) REFERENCES novels(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_ns_platform FOREIGN KEY (platform_id) REFERENCES platforms(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS job_runs (
  id              BIGINT PRIMARY KEY AUTO_INCREMENT,
  job_key         VARCHAR(120) NOT NULL,
  platform        VARCHAR(8)   NOT NULL,
  mode            VARCHAR(32)  NOT NULL,
  started_at      DATETIME NULL,
  finished_at     DATETIME NULL,
  status          ENUM('RUNNING','SUCCEEDED','FAILED','SKIPPED') NOT NULL,
  metrics_json    JSON NULL,
  error_sample_json JSON NULL,
  KEY ix_job_runs_platform_started (platform, started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;