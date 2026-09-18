select 
tender_id AS tender_id,
split_part(raw->>'organisation_chain','||',1) AS department,
raw->>'work_item_title' AS title,
raw->>'location' AS location,
raw->>'pincode' AS pincode,
NULLIF(NULLIF(NULLIF(replace(raw->>'tander_value',',',''),'NA'),'')::numeric(15,2),0) AS tender_value,
{{ wb_date('published_date') }} AS published_at,
{{ wb_date('bid_submition_closing_date') }} AS bid_closes_at,
raw->>'tender_category' AS category,
raw->>'work_description' AS description,
{{ wb_date('bid_opening_date') }} AS bid_opens_at
from {{source('tender','raw_tenders')}}