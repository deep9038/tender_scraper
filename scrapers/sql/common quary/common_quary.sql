SELECT tender_id,title,bid_closes_at From tender_stg WHERE bid_closes_at > now() limit 5;

SELECT count(*) FROM tender_stg WHERE bid_closes_at > now();

SELECT count(*) FROM tender_stg WHERE bid_closes_at BETWEEN now() AND now() + interval '7 days';

--Open tenders, category Works, worth over ₹10,00,000, closing within 14 days.Show title, department, value, closing date. Soonest first. Top 20.
SELECT title,category,department,tender_value,bid_closes_at FROM tender_stg WHERE  category = 'Works' AND tender_value > 1000000 AND bid_closes_at BETWEEN now() AND now() + interval '14 days' ORDER BY bid_closes_at  limit 20;





-- Every department with more than 50 open tenders and over ₹5,00,000 total value, biggest total first.
select department, count(*) as tenders, sum(tender_value) as total_value 
from mart_open_tenders
group by department
having count(*) > 50 and sum(tender_value) > 500000
order by total_value desc;




SELECT tender_id,count(*) as occurence FROM raw_tenders GROUP BY tender_id HAVING count(*) > 1;


UPDATE tender_stg SET bid_closes_at = bid_closes_at + interval '7 days' WHERE tender_id = '2026_WRDD_1039575_1' ;
SELECT tender_id,bid_closes_at,valid_from,valid_to,is_current FROM tender_history WHERE tender_id = '2026_WRDD_1039575_1';


SELECT bid_closes_at FROM tender_history WHERE tender_id = '2026_WRDD_1039575_1' AND valid_from <= '2026-09-09 15:26:20+05:30' AND (valid_to > '2026-09-09 15:26:20+05:30' OR valid_to IS NULL);





UPDATE tender_stg SET bid_closes_at = bid_closes_at + interval '3 days' WHERE tender_id = '2026_MAD_1039255_1';


SELECT bid_closes_at, valid_from,valid_to,is_current FROM tender_history WHERE tender_id = '2026_MAD_1039255_1' ORDER BY valid_from;



SELECT tender_id, bid_closes_at,
lag(bid_closes_at) OVER (PARTITION BY tender_id ORDER BY valid_from) AS previous
FROM tender_history
ORDER BY tender_id, valid_from
LIMIT 20;


WITH changes AS (
    SELECT tender_id, valid_from, bid_closes_at,
        lag(bid_closes_at) OVER (PARTITION BY tender_id ORDER BY valid_from) AS previous
    FROM tender_history
)
SELECT tender_id,
    previous AS old_deadline,
    bid_closes_at AS new_deadline,
    bid_closes_at - previous AS move_by,
    valid_from AS noticed_at
FROM changes 
WHERE previous IS NOT NULL
ORDER BY valid_from DESC;