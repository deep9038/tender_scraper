import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

all_books = []

def scraping(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    books = soup.find_all("article", class_="product_pod")
    for item in books:
        title = item.find("h3").find("a")["title"]
        price = item.find("p",class_="price_color").text
        data = {
            "title": title,
            "price": price
        }
        all_books.append(data)
    next_link = soup.select_one("ul.pager li.next a")
    url = urljoin(url, next_link["href"]) if next_link else None
    print(url)
    scraping(url) if url else None





scraping("https://books.toscrape.com/")


with open("books.json","w") as file:
    json.dump(all_books,file,indent=4)
