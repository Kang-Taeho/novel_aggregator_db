
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
  KEY idx_novel_platform (novel_id, platform_id)
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

-- 샘플 데이터
INSERT INTO novels(title, author_name, genre, age_rating, completion_status, mogo_doc_id)
VALUES
('제목1', '작가1', '판타지', 'ALL', 'unknown','몽고데이터1'),
('제목2', '작가2', '현판', '12', 'ongoing','몽고데이터2'),
('제목3', '작가3', '로맨스', '15', 'completed','몽고데이터3'),
('제목4', '작가4', '라이트노벨', '19', 'hiatus','몽고데이터4'),
('제목5', '작가5', '로판', 'ALL', 'unknown','몽고데이터5'),
('제목6', '작가6', '미스테리', '12', 'ongoing','몽고데이터6'),
('제목7', '작가7', '드라마', '15', 'completed','몽고데이터7'),
('제목8', '작가8', '장르8', '19', 'hiatus','몽고데이터8'),
('제목9', '작가9', '장르9', 'ALL', 'unknown','몽고데이터9'),
('제목10', '작가10', '장르10', '12', 'unknown','몽고데이터10')
ON DUPLICATE KEY UPDATE updated_at=CURRENT_TIMESTAMP;

INSERT INTO novel_sources(novel_id, platform_id, platform_item_id, episode_count, first_episode_date, view_count)
VALUES
('샘플1', '플랫폼1', 'id_01', '1', '2025-12-01','100000'),
('샘플2', '플랫폼2', 'id_02', '2', '2025-12-02','200000'),
('샘플3', '플랫폼3', 'id_03', '3', '2025-12-03','300000'),
('샘플4', '플랫폼4', 'id_04', '4', '2025-12-04','400000'),
('샘플5', '플랫폼5', 'id_05', '5', '2025-12-05','500000'),
('샘플6', '플랫폼6', 'id_06', '6', '2025-12-06','600000'),
('샘플7', '플랫폼7', 'id_07', '7', '2025-12-07','700000'),
('샘플8', '플랫폼8', 'id_08', '8', '2025-12-08','800000'),
('샘플9', '플랫폼9', 'id_09', '9', '2025-12-09','900000'),
('샘플10', '플랫폼10', 'id_10', '10', '2025-12-10','1000000')
ON DUPLICATE KEY UPDATE updated_at=CURRENT_TIMESTAMP;