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