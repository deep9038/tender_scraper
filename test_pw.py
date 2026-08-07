import json

from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=False)
#     page = browser.new_page()
#     page.goto("https://books.toscrape.com/")
#     page.wait_for_selector("article.product_pod")
#     books = page.locator("article.product_pod")

#     title = books.first.locator("h3 a").get_attribute("title")
#     price = books.first.locator("div.product_price p.price_color").inner_text()
#     print(title)
#     print(price)
#     input("Press Enter to close the browser...")
#     browser.close()



all_books = []

def scraping(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        while url:
            page.goto(url)
            page.wait_for_selector("article.product_pod")
            books = page.locator("article.product_pod")

            for i in range(books.count()):
                title =  books.nth(i).locator("h3 a").get_attribute("title")
                price = books.nth(i).locator("div.product_price p.price_color").inner_text()
                data = {
                    "title": title,
                    "price": price
                }
                all_books.append(data)

            next_button_link = page.locator("li.next a")

            if next_button_link.count() > 0:
                next_link = next_button_link.first.get_attribute("href")
                url = urljoin(url, next_link)
                print(url)
                # scraping(url)
            else:
                url = None



scraping("https://books.toscrape.com/")

with open("books.json","w") as file:
    json.dump(all_books,file,indent=4)