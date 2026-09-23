Titles are sometimes reference numbers. work_item_title occasionally contains a code (NIeT-16/AD/26-27/07) instead of a description. Affects an unknown share of rows. Other tender sites have the same problem. Possible fix: fall back to description via CASE. Not started.

I let my own pipeline go 15 days stale and only noticed because a count dropped


there is imposible data issue . e_pubshed_date values have one imposible data "31 secptembor" tender_id = '2026_MAD_1039828_4'


when a tender reopen or dedline changes data base have historical knowleg of that . 

HARD PROBLEM ENCOUNTER AND SOLUTION . 
    PROBLME: to run this scraper i have to keep a computer on becasue to scrap data i need to reach the list first to reach the list there is a captcha protecting it so to run everytime i need to open a pc then manually run it and see captha then input in . so it's not moduler enughf 

    SOLUTION: to solve this first the scraper will pic the captha from the ui then it will send me it to the my mobile through a discord bot i anser it there if fail then refresh the captcha then re try . succesfully captha input and t will start automatictly .  



Refresh keys off publish date, not change date — a tender published 60 days ago whose deadline moves today is never re-fetched, at any REFRESH_DAYS. The portal exposes no last-modified field.

    STATUS: built and working (22 Sep 2026). scrapers/discord_relay.py sends the
    captcha, waits up to 180s for a reply, and the scraper retries 3x with the
    site's Refresh button. I no longer need to be at the computer.

    EVIDENCE FOR THE BLIND SPOT ABOVE: 102 tenders in tenders.jsonl have had
    their published_date change between scrapes, and 28 have had their closing
    date change. So tenders really do get edited after publication - the ones
    edited outside the refresh window are simply invisible to us.


HISTORY ONLY STARTS 17 SEP 2026.
    The dbt snapshot (dbt.tender_snapshot) was created on 17 Sep and only records
    changes it has seen since. The 28 deadline extensions already sitting in
    tenders.jsonl happened before it existed and were never captured. The old
    hand-built public.tender_history was dropped and held nothing real either -
    all 4 of its closed versions were my own test edits.
    POSSIBLE FIX: replay tenders.jsonl in timestamp order to backfill. Not started.


tenders.jsonl HAS NO BACKUP.
    It was removed from git on 21 Sep because it passed GitHub's 50MB warning
    (56MB). It is now ignored, so nothing backs it up.
    This file is the only copy of every observation ever made - the portal only
    shows currently-active tenders, so none of it can be re-scraped. If this disk
    dies, the raw layer and all history are gone.
    FIX: copy it somewhere off this machine. Properly solved in Phase 6 (S3).
