/* 
Used materials from:
https://postgrespro.ru/docs/postgresql/9.6/sql-createtable
https://postgrespro.ru/docs/postgresql/9.6/datatype-numeric
https://www.postgresql.org/docs/9.1/sql-createindex.html
*/

CREATE TABLE IF NOT EXISTS web_monitoring (
  id            BIGSERIAL,
  topic         TEXT,
  url           TEXT,
  event_date    TIMESTAMP,
  is_fine       BOOLEAN,
  transport     TEXT,
  response_code SMALLINT,
  response_time REAL,
  regexp        TEXT,
  regexp_found  BOOLEAN,
  timeout       REAL,
  period        REAL,
  date_created  TIMESTAMP
);

ALTER TABLE web_monitoring ADD CONSTRAINT uniq_web_monitoring UNIQUE (url, event_date, is_fine);

CREATE INDEX url_idx_web_monitoring ON web_monitoring (url);
CREATE INDEX event_date_idx_web_monitoring ON web_monitoring (event_date);
CREATE INDEX is_fine_idx_web_monitoring ON web_monitoring (is_fine);
CREATE INDEX response_code_idx_web_monitoring ON web_monitoring (response_code);
CREATE INDEX regexp_found_idx_web_monitoring ON web_monitoring (regexp_found);

COMMIT;
