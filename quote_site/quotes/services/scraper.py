import requests
from bs4 import BeautifulSoup

from quotes.models import Author, Quote, Tag


BASE_URL = "http://quotes.toscrape.com"


def scrape_author(author_url):
    response = requests.get(author_url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    return {
        "born_date": soup.select_one(".author-born-date").get_text(strip=True),
        "born_location": soup.select_one(".author-born-location").get_text(strip=True),
        "description": soup.select_one(".author-description").get_text(strip=True),
    }


def scrape_quotes():
    page_url = "/"
    created_quotes = 0

    while page_url:
        response = requests.get(BASE_URL + page_url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for quote_block in soup.select(".quote"):
            quote_text = quote_block.select_one(".text").get_text(strip=True).strip("“”")
            author_name = quote_block.select_one(".author").get_text(strip=True)

            author_link = quote_block.select_one("a[href^='/author']")["href"]
            author_data = scrape_author(BASE_URL + author_link)

            author, _ = Author.objects.get_or_create(
                fullname=author_name,
                defaults=author_data,
            )

            quote, quote_created = Quote.objects.get_or_create(
                text=quote_text,
                defaults={"author": author},
            )

            if quote_created:
                created_quotes += 1

            for tag_element in quote_block.select(".tag"):
                tag_name = tag_element.get_text(strip=True)
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                quote.tags.add(tag)

        next_button = soup.select_one(".next a")
        page_url = next_button["href"] if next_button else None

    return created_quotes