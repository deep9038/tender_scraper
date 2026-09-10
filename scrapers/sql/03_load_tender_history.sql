BEGIN;

UPDATE tender_history h 
SET valid_to = now(), is_current = false
FROM tender_stg s 
WHERE h.tender_id = s.tender_id
AND h.is_current
AND (h.published_at,h.bid_closes_at, h.bid_opens_at) IS DISTINCT FROM 
(s.published_at, s.bid_closes_at, s.bid_opens_at);


INSERT INTO tender_history (tender_id, published_at, bid_closes_at,bid_opens_at, valid_from)
SELECT s.tender_id, s.published_at,s.bid_closes_at,s.bid_opens_at, now()
FROM tender_stg s
WHERE NOT EXISTS (
    SELECT 1 FROM tender_history h
    WHERE h.tender_id = s.tender_id
    AND h.is_current
);

COMMIT;