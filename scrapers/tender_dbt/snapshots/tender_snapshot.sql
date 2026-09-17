{% snapshot tender_snapshot %}

{{
    config(
        unique_key = 'tender_id',
        check_cols = ['published_at','bid_closes_at','bid_opens_at'],
        strategy = 'check'
    )
}}

select tender_id, published_at, bid_closes_at , bid_opens_at from {{ ref('stg_tenders')}}


{% endsnapshot %}