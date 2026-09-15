select tender_id , tender_value, bid_closes_at, from dbt.stg_tenders
except
select tender_id , tender_value,bid_closes_at from public.tender_stg;


select tender_id, department, title,location,pincode,tender_value,published_at,bid_closes_at,bid_opens_at,category,description from dbt.stg_tenders
except
select tender_id, department,title,location,pincode,tender_value,published_at,bid_closes_at,bid_opens_at,category,description from public.tender_stg;



select tender_id, cover_no, cover_type from dbt.stg_covers
except 
select tender_id, cover_no, cover_type from public.tender_covers;




select tender_id, cover_no, cover_type from public.tender_covers
except
select tender_id,cover_no, cover_type from dbt.stg_covers;

select tender_id, cover_no, count(*) from dbt.stg_covers
group by tender_id,cover_no having count(*) > 1;