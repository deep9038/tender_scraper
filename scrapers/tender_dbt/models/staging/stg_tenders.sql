{{ config(materialized='view') }}
select 
tender_id AS tender_id,
split_part(raw->>'organisation_chain','||',1) AS department,
raw->>'work_item_title' AS title,
raw->>'location' AS location,
raw->>'pincode' AS pincode,
NULLIF(NULLIF(NULLIF(replace(raw->>'tander_value',',',''),'NA'),'')::numeric,0) AS tender_value,
safe_ts(NULLIF(raw->>'published_date','NA'),'DD-Mon-YYYY HH12:MI AM') AS published_at,
safe_ts(NULLIF(raw->>'bid_submition_closing_date','NA'),'DD-Mon-YYYY HH12:MI AM') AS bid_closes_at,
raw->>'tender_category' AS category,
raw->>'work_description' AS description,
safe_ts(NULLIF(raw->>'bid_opening_date','NA'),'DD-Mon-YYYY HH12:MI AM') AS bid_opens_at
from {{source('tender','raw_tenders')}}