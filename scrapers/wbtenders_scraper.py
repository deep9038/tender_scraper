import json
import re
from playwright.sync_api import sync_playwright;
from urllib.parse import urljoin
base_url = "https://wbtenders.gov.in/nicgep/app?page=FrontEndLatestActiveTenders&service=page"
tenders = []

# Reads every <tr> in a table and returns its cells as ('k'|'v', text) pairs.
PAIRS_JS = """
table => Array.from(table.querySelectorAll('tr')).map(
    tr => Array.from(tr.children)
        .filter(c => c.tagName === 'TD')
        .map(c => [
            c.classList.contains('td_caption') ? 'k' :
            c.classList.contains('td_field')   ? 'v' : 'x',
            c.innerText
        ])
)
"""


def clean(text):
    return text.replace("\xa0", " ").strip()


def slug(text):
    # "No. of Covers" -> "no_of_covers"   "EMD Fee Type " -> "emd_fee_type"
    return re.sub(r"[^a-z0-9]+", "_", clean(text).lower()).strip("_")


def extract_pairs(table):
    """caption -> field, paired inside each row so a missing section can't shift things."""
    if table.count() == 0:
        return {}
    out = {}
    for cells in table.evaluate(PAIRS_JS):
        label = None
        for kind, text in cells:
            if kind == "k":
                label = text
            elif kind == "v" and label is not None:
                key = slug(label)
                if key:
                    out[key] = clean(text)
                label = None          # one caption consumes one field
    return out


def block_with_caption(page, caption):
    """Find the tablebg table containing a given caption -- no positional index."""
    return page.locator("table.tablebg").filter(
        has=page.locator("td.td_caption", has_text=caption)
    ).first




    

htmlpage = []


def payment_block_process(page):
    # unique id on the page -- no need to locate the surrounding tablebg block
    rows = page.locator("#onlineInstrumentsTableView tr")
    if rows.count() == 0:
        return ""
    texts = rows.evaluate_all(
        "trs => trs.slice(1).map(tr => tr.cells[1] ? tr.cells[1].innerText.trim() : '')"
    )
    return " / ".join(t for t in texts if t)


def extract_cover_table(page):
    table = page.locator("#packetTableView")
    if table.count() == 0:            # not every tender has a Covers section
        return []

    # single round-trip: grab every field cell as a 2D array
    rows = table.evaluate("""
        table => Array.from(table.querySelectorAll('tr'))
            .map(r => Array.from(r.querySelectorAll('td.td_field'))
                        .map(td => td.innerText.trim()))
            .filter(cells => cells.length === 4)
    """)

    covers = []
    current = None
    for cover_no, cover_type, description, doc_type in rows:
        if cover_no:                      # non-empty => a new cover starts
            current = {
                "cover_no": cover_no,
                "cover_type": cover_type,
                "documents": [],
            }
            covers.append(current)
        if current:
            current["documents"].append({
                "description": description,
                "document_type": doc_type,
            })
    return covers






with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    
    list_page = context.new_page()
    detail_page = context.new_page()

    list_page.goto(base_url)
    input("Press Enter to continue the browser...")

    list_page.wait_for_selector("table#table")

    rows = list_page.locator("table#table tbody tr")

    for i in range(1,rows.count() -1):
        row = rows.nth(i).locator("td")
        detail_url = urljoin(list_page.url, row.nth(4).locator("a").get_attribute("href"))


        serial_numder = row.nth(0).inner_text()
        e_pubshed_date = row.nth(1).inner_text()
        bid_submition_closing_date = row.nth(2).inner_text()
        tender_opening_date = row.nth(3).inner_text()
        tender_information = detail_url
        tender_id = row.nth(4).inner_text()
        tander_value = row.nth(6).inner_text()


        detail_page.goto(detail_url)
        detail_page.wait_for_selector("table.tablebg")

        basic = extract_pairs(block_with_caption(detail_page, "Organisation Chain"))

        organisation_chain      = basic.get("organisation_chain", "")
        tender_reference_number = basic.get("tender_reference_number", "")
        detail_tender_id        = basic.get("tender_id", "")
        withdrawal_allowed      = basic.get("withdrawal_allowed", "")
        tender_type             = basic.get("tender_type", "")
        form_of_contract        = basic.get("form_of_contract", "")
        tender_category         = basic.get("tender_category", "")
        no_of_covers            = basic.get("no_of_covers", "")
        gte_allowed             = basic.get("general_technical_evaluation_allowed", "")
        itemwise_gte_allowed    = basic.get("itemwise_technical_evaluation_allowed", "")
        payment_mode            = basic.get("payment_mode", "")
        multi_currency_boq      = basic.get("is_multi_currency_allowed_for_boq", "")
        multi_currency_fee      = basic.get("is_multi_currency_allowed_for_fee", "")
        two_stage_bidding       = basic.get("allow_two_stage_bidding", "")

        online_bankers     = payment_block_process(detail_page)
        covers_information = extract_cover_table(detail_page)




        data = {
            "serial_numder": serial_numder,
            "e_pubshed_date": e_pubshed_date,
            "bid_submition_closing_date": bid_submition_closing_date,
            "tender_opening_date": tender_opening_date,
            "tender_information": tender_information,
            "tender_id": tender_id,
            "organisation_chain": organisation_chain,
            "tander_value": tander_value,
            "tender_reference_number": tender_reference_number,
            "detail_tender_id": detail_tender_id,
            "withdrawal_allowed": withdrawal_allowed,
            "tender_type": tender_type,
            "form_of_contract": form_of_contract,
            "tender_category": tender_category,
            "no_of_covers": no_of_covers,
            "general_technical_evaluation_allowed": gte_allowed,
            "item_wise_technical_evaluation_allowed": itemwise_gte_allowed,
            "payment_mode": payment_mode,
            "is_multi_currency_allowed_for_boq": multi_currency_boq,
            "is_multi_currency_allowed_for_fee": multi_currency_fee,
            "allow_two_stage_bidding": two_stage_bidding,
            "online_bankers": online_bankers,
            "covers": covers_information,
        }



        tenders.append(data)
        


        print("__________________")




with open("htmlcontent.json", "w", encoding="utf-8") as file:
    json.dump(tenders, file, indent=4, ensure_ascii=False)
