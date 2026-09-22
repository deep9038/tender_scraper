Titles are sometimes reference numbers. work_item_title occasionally contains a code (NIeT-16/AD/26-27/07) instead of a description. Affects an unknown share of rows. Other tender sites have the same problem. Possible fix: fall back to description via CASE. Not started.

I let my own pipeline go 15 days stale and only noticed because a count dropped


there is imposible data issue . e_pubshed_date values have one imposible data "31 secptembor" tender_id = '2026_MAD_1039828_4'


when a tender reopen or dedline changes data base have historical knowleg of that . 

HARD PROBLEM ENCOUNTER AND SOLUTION . 
    PROBLME: to run this scraper i have to keep a computer on becasue to scrap data i need to reach the list first to reach the list there is a captcha protecting it so to run everytime i need to open a pc then manually run it and see captha then input in . so it's not moduler enughf 

    SOLUTION: to solve this first the scraper will pic the captha from the ui then it will send me it to the my mobile through teligram bot i anser it there if fail then refresh the captcha then re try . succesfully captha input and t will start automatictly .  



Refresh keys off publish date, not change date — a tender published 60 days ago whose deadline moves today is never re-fetched, at any REFRESH_DAYS. The portal exposes no last-modified field.