
{{config(materialized='view')}}
SELECT tender_id AS tender_id , title AS title , department AS department ,location AS location, tender_value AS tender_value , bid_opens_at AS bid_opens_at , bid_closes_at AS bid_closes_at FROM {{ref("stg_tenders")}} 
WHERE bid_closes_at > now() 