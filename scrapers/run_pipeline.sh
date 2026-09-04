#!/usr/bin/env bash
set -e   # Stop imidiatly if anything wrong happen  
../.venv/bin/python wbtenders_scraper.py # will run the west bengal tender scraper and save the data in raw folder
../.venv/bin/python load_raw.py  # will load the raw data in raw_tender table 
docker exec -i tender-db psql -U tender -d tenders < sql/01_load_tender_stg.sql  # will use the rewriten sql command to load the raw data to minimal understandale table data in table_stg table  



####################### ABSOLUTE ENTRY POINT OF THIS PROJECT INCASE I FORGOT ############################ 


# run this command bellow inside scrapers folder to run the scraper -> load -> parse pipline (v1.1.1)
# ./run_pipeline.sh    