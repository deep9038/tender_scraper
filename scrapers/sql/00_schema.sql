-- DUMP layer raw data will be here wait for cleaning
-- raw_tenders = loading zone. never edited, naver parsed.
CREATE TABLE IF NOT EXISTS raw_tenders(
    tender_id TEXT PRIMARY KEY,
    raw JSONB NOT NULL,
    scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);



-- CLEAN layer
-- Only the columns someone actually filters, groups, or reads.
-- The other ~46 fields stay in raw_tenders until asked for.
CREATE TABLE IF NOT EXISTS tender_stg (
    tender_id TEXT PRIMARY KEY,
    department TEXT,
    title          TEXT,
    description    TEXT,
    category       TEXT,
    location       TEXT,
    pincode TEXT,
    tender_value NUMERIC(15,2),
    published_at   TIMESTAMPTZ,
    bid_closes_at  TIMESTAMPTZ,
    bid_opens_at TIMESTAMPTZ
);




CREATE OR REPLACE FUNCTION safe_ts(txt TEXT, fmt text)
RETURNS timestamptz AS $$
BEGIN
    RETURN to_timestamp(txt, fmt);
EXCEPTION WHEN others THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


CREATE TABLE IF NOT EXISTS tender_covers (
    tender_id TEXT REFERENCES tender_stg(tender_id),
    cover_no SMALLINT,
    cover_type TEXT,
    PRIMARY KEY (tender_id, cover_no)
);




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
