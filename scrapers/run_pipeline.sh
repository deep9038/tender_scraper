#!/usr/bin/env bash
set -euo pipefail   # Stop imidiatly if anything wrong happen  
cd "$(dirname "$0")"
../.venv/bin/python wbtenders_scraper.py # will run the west bengal tender scraper and save the data in raw folder
../.venv/bin/python load_raw.py  # will load the raw data in raw_tender table 
../.venv/bin/dbt build --project-dir tender_dbt # transform the raw_tenders into staging then mart 
# docker exec -i tender-db psql -U tender -d tenders < sql/03_load_tender_history.sql  # will use the rewriten sql command to load the raw data to minimal understandale table data in tender history table  



####################### ABSOLUTE ENTRY POINT OF THIS PROJECT INCASE I FORGOT ############################ 


# run this command bellow inside scrapers folder to run the 
   # scraper -> load -> parse pipline (v1.1.1) 
   # scraper -> load -> dbt -> history pipline (v2.0.0) : latest version of this project

# ./run_pipeline.sh    