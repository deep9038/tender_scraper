SELECT tender_id, cover_no, count(*) FROM {{ref("stg_covers")}}
GROUP BY tender_id,cover_no HAVING count(*) > 1