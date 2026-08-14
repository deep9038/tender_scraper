import json
import psycopg
from psycopg.types.json import Jsonb


DSN = "postgresql://tender:tender@localhost:5432/tenders"
SRC = "tenders.jsonl"


SQL = """
INSERT INTO raw_tenders (tender_id,raw)
VALUES (%s, %s)
ON CONFLICT (tender_id) DO UPDATE
SET raw = EXCLUDED.raw,
    scraped_at = now()
"""


def rows(path):
    skipped = 0 
    with open(path,encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            tid = (rec.get("detail_tender_id") or "").strip()
            if not tid:
                skipped += 1 
                continue
            yield tid, Jsonb(rec)
    if skipped:
        print(f"skipped {skipped} records with no tender_id")



with psycopg.connect(DSN) as conn:
    with conn.cursor() as cur:
        batch, total = [], 0
        for row in rows(SRC):
            batch.append(row)
            if len(batch) >= 500:
                cur.executemany(SQL, batch)
                total += len(batch)
                batch = []
        if batch:
            cur.executemany(SQL, batch)
            total += len(batch)
    conn.commit()

print(f"sent {total} rows")