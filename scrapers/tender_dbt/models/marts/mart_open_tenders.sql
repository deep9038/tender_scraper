{{config(materialized='view')}}

select * from {{ref('stg_tenders')}} where bid_closes_at > now()