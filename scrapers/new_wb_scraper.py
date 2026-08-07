import json
import os
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin



BASE_URL = "https://wbtenders.gov.in/nicgep/app?page=FrontEndLatestActiveTenders&service=page"
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tenders.json")

tenders = []

ROW_CELLS_JS = """
trs => trs.map(tr=> Array.from(tr.children)
    .filter(c => c.tagName === 'TD')
    .map(c =>[
        c.classList.contains('td_caption') ? 'k' :
        c.classList.contains('td_field') ? 'v' : 'x',
        c.innerText
    ])
)
"""







def clean(text):
    return text.replace("\xa0", " ").strip()






def scrape_detail(page,url):
    page.goto(url)
    page.wait_for_selector("table.tablebg")

    rows = page.evel_on_selector_all("table.tablebg tr", ROW_CELLS_JS )

    details = {}

    for cells in rows:
        label = None
        for kind, text in cells:
            if kind == "k":
                lable = text
            elif kind == "v" and lable is not None:
                key = clean(label).replace(" ","_").lower()
                if key:
                    details[key] = clean(text)
                label = None

    return details


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    list_page = context.new_page()
    details_page = context.new_page()

    list_page.goto(BASE_URL)
    input("Solve the captcha in the browser, then press Enter...")

    list_page.wait_for_selector("table#table")

    raw_rows = list_page.eval_on_selector_all(
        "table#table tbody tr",
        """trs => trs.map(tr => ({
                cells: Array.from(tr.cells).map(c => c.innerText),
                href: tr.cells[4] && tr.cells[4].querySelector('a') ? tr.cells[4].querySelector('a').getAttribute('href') : null

        }))"""
    )



    rows=[r for r in raw_rows if len(r["cells"]) >= 7 and r["href"]]

    print(f"{len(rows)} tenders found")


    for n, r in enumerate(rows, start=1):
        c = r["cells"]
        detail_url = urljoin(list_page.url,r["href"])

        data = {
            "serial_number": clean(c[0]),
            "e_published_data": clean(c[1]),
            "bid_submission_closing_date": clean(c[2]),
            "tender_opening_date" : clean(c[3]),
            "tender_information": detail_url,
            "tender_id" : clean(c[4]),
            "organisation_chain": clean(c[5]),
            "tender_value": clean(c[6])
        }

        try:
            data["details"] = scrape_detail(details_page, detail_url)
        except Exception as e:
            print(f" [{n}] detail failed: {type(e).__name__}:{e}")
            data["details"] = None
            data["error"] = str(e)

        print(f"[{n}/{len(rows)}] {data['tender_id'][:60]}")
        tenders.append(data)
    browser.close()

with open(OUT_PATH,"w",encoding="utf-8") as f:
    json.dump(tenders, f, indent=4,ensure_ascii=False)

print(f"Wrote {len(tenders)} tenders to {OUT_PATH}")
