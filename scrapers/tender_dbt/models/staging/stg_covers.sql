

{{config(materialized='table')}}

SELECT r.tender_id AS tender_id, (c->>'cover_no')::SMALLINT AS cover_no, c->>'cover_type' AS cover_type
FROM {{source('tender','raw_tenders')}} r ,LATERAL jsonb_array_elements(r.raw->'covers') AS c

