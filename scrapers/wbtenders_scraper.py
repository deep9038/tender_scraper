import json
import re
from playwright.sync_api import sync_playwright;
from urllib.parse import urljoin
from datetime import datetime, timedelta
import traceback
import os
os.makedirs("failures", exist_ok=True)

TRACE = False   # True records a Playwright trace -- heavy, debugging runs only
REFRESH_DAYS = 1
base_url = "https://wbtenders.gov.in/nicgep/app?page=FrontEndLatestActiveTenders&service=page"

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



def parse_data(s):
    return datetime.strptime(s.strip(),"%d-%b-%Y %I:%M %p")


def gepnic_id(cell_text):
    parts = re.findall(r"\[([^\[\]]+)\]", cell_text)
    return parts[-1].strip() if parts else ""

known = set()
if os.path.exists("tenders.jsonl"):
    with open("tenders.jsonl",encoding="utf-8") as f:
        for line in f:
            if line.strip():
                known.add(json.loads(line)["detail_tender_id"])
print(f"already have {len(known)} tenders")

cutoff = datetime.now() - timedelta(days=REFRESH_DAYS)









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

    if TRACE:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    try:

    
        list_page = context.new_page()
        detail_page = context.new_page()
        list_page.goto(base_url)
        input("Press Enter to continue the browser...")
        list_page.wait_for_selector("table#table")


        done = set()
        empty_pages = 0
        page_no = 1

        try:
            while True:
                print(f" page {page_no} ======")
                page_rows = []
                rows = list_page.locator("table#table tbody tr")

                for i in range(1, rows.count() -1):
                    row = rows.nth(i).locator("td")
                    detail_url= urljoin(list_page.url, row.nth(4).locator("a").get_attribute("href"))

                    page_rows.append({
                        "gid": gepnic_id(row.nth(4).inner_text()),
                        "serial_numder": row.nth(0).inner_text(),
                        "e_pubshed_date": row.nth(1).inner_text(),
                        "bid_submition_closing_date": row.nth(2).inner_text(),
                        "tender_opening_date": row.nth(3).inner_text(),
                        "tender_id": row.nth(4).inner_text(),
                        "organisation_chain": row.nth(5).inner_text(),
                        "tander_value": row.nth(6).inner_text(),
                        "detail_url": detail_url,
                    })


                todo = [
                    r for r in page_rows
                    if r["gid"] not in done                             # not done this run
                    and (r["gid"] not in known                          # never seen before
                         or parse_data(r["e_pubshed_date"]) >= cutoff)  # recent -> refresh
                ]

                if not todo:
                    empty_pages += 1
                    print(f"  nothing new (empty page {empty_pages})")
                    if empty_pages >= 2:
                        print("caught up - stopping")
                        break
                else:
                    empty_pages = 0


                page_records = []
                for r in todo:
                    done.add(r["gid"])
                    try:
                        detail_page.goto(r["detail_url"])
                        detail_page.wait_for_selector("table.tablebg")



                        basic = extract_pairs(block_with_caption(detail_page, "Organisation Chain"))
                        online_bankers     = payment_block_process(detail_page)
                        covers_information = extract_cover_table(detail_page)
                        emd_fee_details = extract_pairs(block_with_caption(detail_page,"EMD Amount in ₹"))
                        # print(block_with_caption_check(detail_page,"Title"))
                        work_item_details = extract_pairs(block_with_caption(detail_page,"Title"))
                        # print(work_item_details)

                        critical_dates = extract_pairs(block_with_caption(detail_page,"Published Date"))

                        tender_inviting_authority = extract_pairs(block_with_caption(detail_page,"Name"))



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
                        emd_amount_in           = emd_fee_details.get("emd_amount_in","")
                        emd_exemption_allowed   = emd_fee_details.get("emd_exemption_allowed","")
                        emd_fee_type            = emd_fee_details.get("emd_fee_type","")
                        emd_percentage          = emd_fee_details.get("emd_percentage","")
                        emd_payable_to          = emd_fee_details.get("emd_payable_to","")
                        emd_payable_at          = emd_fee_details.get("emd_payable_at","")
                        work_item_title         = work_item_details.get("title","")
                        work_description        = work_item_details.get("work_description","")
                        nda_pre_qualification   = work_item_details.get("nda_pre_qualification","")
                        independent_external_monitor_remarks = work_item_details.get("independent_external_monitor_remarks","")
                        tender_value_in         = work_item_details.get("tender_value_in","")
                        product_category        = work_item_details.get("product_category","")
                        sub_category            = work_item_details.get("sub_category","")
                        contract_type           = work_item_details.get("contract_type","")
                        bid_validity_days       = work_item_details.get("bid_validity_days","")
                        period_of_work_days     = work_item_details.get("period_of_work_days","")
                        location                = work_item_details.get("location","")
                        pincode                 = work_item_details.get("pincode","")
                        pre_bid_meeting_place   = work_item_details.get("pre_bid_meeting_place","")
                        pre_bid_meeting_address = work_item_details.get("pre_bid_meeting_address","")
                        pre_bid_meeting_date    = work_item_details.get("pre_bid_meeting_date","")
                        bid_opening_place       = work_item_details.get("bid_opening_place","")
                        should_allow_nda_tender = work_item_details.get("should_allow_nda_tender","")
                        allow_preferential_bidder = work_item_details.get("allow_preferential_bidder","")
                        published_date          = critical_dates.get("published_date","")
                        bid_opening_date        = critical_dates.get("bid_opening_date","")
                        document_download_sale_start_date = critical_dates.get("document_download_sale_start_date","")
                        document_download_sale_end_date = critical_dates.get("document_download_sale_end_date","")
                        clarification_start_date = critical_dates.get("clarification_start_date","")
                        clarification_end_date = critical_dates.get("clarification_end_date","")
                        bid_submission_start_date = critical_dates.get("bid_submission_start_date","")
                        bid_submission_end_date = critical_dates.get("bid_submission_end_date","")
                        name = tender_inviting_authority.get("name","")
                        address = tender_inviting_authority.get("address","")




                        data = {
                            **r,
                            "organisation_chain": organisation_chain,
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
                            "emd_amount_in":emd_amount_in,
                            "emd_exemption_allowed":emd_exemption_allowed,
                            "emd_fee_type":emd_fee_type,
                            "emd_percentage":emd_percentage,
                            "emd_payable_to":emd_payable_to,
                            "emd_payable_at":emd_payable_at,
                            "work_item_title":work_item_title,
                            "work_description":work_description,
                            "nda_pre_qualification":nda_pre_qualification,
                            "independent_external_monitor_remarks":independent_external_monitor_remarks,
                            "tender_value_in":tender_value_in,
                            "product_category":product_category,
                            "sub_category":sub_category,
                            "contract_type":contract_type,
                            "bid_validity_days":bid_validity_days,
                            "period_of_work_days":period_of_work_days,
                            "location":location,
                            "pincode":pincode,
                            "pre_bid_meeting_place":pre_bid_meeting_place,
                            "pre_bid_meeting_address":pre_bid_meeting_address,
                            "pre_bid_meeting_date":pre_bid_meeting_date,
                            "bid_opening_place":bid_opening_place,
                            "should_allow_nda_tender":should_allow_nda_tender,
                            "allow_preferential_bidder":allow_preferential_bidder,
                            "published_date":published_date,
                            "bid_opening_date":bid_opening_date,
                            "document_download_sale_start_date":document_download_sale_start_date,
                            "document_download_sale_end_date": document_download_sale_end_date,
                            "clarification_start_date":clarification_start_date,
                            "clarification_end_date":clarification_end_date,
                            "bid_submission_start_date":bid_submission_start_date,
                            "bid_submission_end_date":bid_submission_end_date,
                            "name":name,
                            "address":address
                        }

                        page_records.append(data)

                    except Exception as e:
                        tag = f"failures/p{page_no}_{r['tender_id'][:20].replace('/', '_')}"
                        detail_page.screenshot(path=f"{tag}.png", full_page=True)
                        with open(f"{tag}.html", "w", encoding="utf-8") as fh:
                            fh.write(detail_page.content())
                        print(f"  FAIL {type(e).__name__}: {e}  -> saved {tag}.png")
                        continue                     # lose one tender, not the run




                with open("tenders.jsonl", "a", encoding="utf-8") as f:
                    for data in page_records:
                        f.write(json.dumps(data,ensure_ascii=False) + "\n")
                print(f"  saved {len(page_records)} of {len(todo)} to do ({len(page_rows)} on page)")




                next_link = list_page.locator("#loadNext")
                if next_link.count() == 0:
                    print("no Next link - last page")
                    break

                first_before = rows.nth(1).locator("td").first.inner_text().strip()

                try:
                    next_link.click()
                    list_page.wait_for_function(
                        """old =>{
                            const c = document.querySelector('#table tbody tr:nth-child(2) td');
                            return c && c.innerText.trim() !== old;
                        }""",
                        arg=first_before
                    )
                except Exception:
                    print(f"PAGINATION FAILED on page {page_no}")
                    try:
                        tag = f"failures/pagination_p{page_no}"
                        list_page.screenshot(path=f"{tag}.png", full_page=True)
                        with open(f"{tag}.html", "w", encoding="utf-8") as fh:
                            fh.write(list_page.content())
                        print(f"  -> saved {tag}.png / .html")
                    except Exception:
                        print("  -> could not save failure evidence")
                    traceback.print_exc()
                    break


                list_page.wait_for_timeout(500)

                page_no += 1
        except Exception:
            print("UNEXPECTED CRASH")
            traceback.print_exc()
    finally:
        if TRACE:
            context.tracing.stop(path="trace.zip")