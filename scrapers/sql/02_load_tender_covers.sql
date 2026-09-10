INSERT INTO tender_covers (tender_id, cover_no,cover_type)
SELECT r.tender_id, (c->>'cover_no')::SMALLINT, c->>'cover_type'
FROM raw_tenders r ,
    LATERAL jsonb_array_elements(r.raw->'covers') AS c
ON CONFLICT (tender_id, cover_no) DO UPDATE
SET cover_type = excluded.cover_type;

WITH cover_counts AS (
    SELECT tender_id, count(*) AS cover_count 
    FROM tender_covers
    GROUP BY tender_id
)

SELECT s.department, sum(s.tender_value) AS total_value, avg(cc.cover_count) AS avg_cover
FROM tender_stg s
JOIN cover_counts cc USING (tender_id)
GROUP BY s.department
ORDER BY total_value DESC NULLS LAST
limit 10;


select department,
       sum(tender_value) as total,
       round(avg(tender_value),2) as average,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY tender_value) AS median ,
       max(tender_value) AS biggest
FROM tender_stg
GROUP BY department
ORDER BY total DESC NULLS LAST 
LIMIT 10;