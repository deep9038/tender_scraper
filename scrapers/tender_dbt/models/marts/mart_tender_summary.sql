
WITH cover_counts AS (
    SELECT tender_id, COUNT(*) AS cover_count
    FROM {{ref("stg_covers")}}
    GROUP BY tender_id
)


SELECT t.tender_id, t.title,t.department,t.location,t.tender_value,t.bid_opens_at,t.bid_closes_at, COALESCE(c.cover_count, 0) AS cover_count 
FROM {{ref("stg_tenders")}} t 
LEFT JOIN cover_counts c USING (tender_id)