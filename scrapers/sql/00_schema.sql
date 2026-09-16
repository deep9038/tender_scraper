-- DUMP layer raw data will be here wait for cleaning
-- raw_tenders = loading zone. never edited, naver parsed.
CREATE TABLE IF NOT EXISTS raw_tenders(
    tender_id TEXT PRIMARY KEY,
    raw JSONB NOT NULL,
    scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);







CREATE OR REPLACE FUNCTION safe_ts(txt TEXT, fmt text)
RETURNS timestamptz AS $$
BEGIN
    RETURN to_timestamp(txt, fmt);
EXCEPTION WHEN others THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql IMMUTABLE;






CREATE TABLE IF NOT EXISTS tender_history(
    tender_id TEXT NOT NULL,
    published_at TIMESTAMPTZ,
    bid_closes_at TIMESTAMPTZ,
    bid_opens_at TIMESTAMPTZ,
    valid_from TIMESTAMPTZ NOT NULL,
    valid_to TIMESTAMPTZ,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (tender_id, valid_from)
);
