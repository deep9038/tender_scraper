insert into tender_stg(tender_id,department, title, location, pincode, tender_value, published_at, bid_closes_at, category, description)
select 
tender_id,
split_part(raw->>'organisation_chain','||',1),
raw->>'work_item_title',
raw->>'location',
raw->>'pincode',
-- some values for tender_values are '0.00' whitch mean not desided yet that's why this secuation is converted to have NULL insted of 0.00
NULLIF(NULLIF(NULLIF(replace(raw->>'tander_value',',',''),'NA'),'')::numeric,0),
to_timestamp(NULLIF(raw->>'published_date','NA'),'DD-Mon-YYYY HH12:MI AM'),
to_timestamp(NULLIF(raw->>'bid_submition_closing_date','NA'),'DD-Mon-YYYY HH12:MI AM'),
raw->>'tender_category',
raw->>'work_description' 
from raw_tenders 
on conflict (tender_id) do update
set department = excluded.department,
    title = excluded.title,
    location = excluded.location,
    pincode = excluded.pincode,
    tender_value = excluded.tender_value,
    published_at = excluded.published_at,
    bid_closes_at = excluded.bid_closes_at,
    category = excluded.category,
    description = excluded.description
;