import requests
import pandas as pd
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"


def get_soup(url):
    """Download a webpage and return a BeautifulSoup object."""

    response = requests.get(url)

    response.raise_for_status()

    return BeautifulSoup(response.text, "html.parser")


def get_categories():
    """Get all book categories from the website."""

    soup = get_soup(BASE_URL)

    categories = []

    category_links = soup.select(".side_categories ul li ul li a")

    for link in category_links:

        category_name = link.text.strip()

        category_url = BASE_URL + link["href"]

        categories.append({
            "name": category_name,
            "url": category_url
        })

    return categories


def scrape_book(book, category):
    """Extract information from one book card."""

    title = book.h3.a["title"]

    price = book.select_one(".price_color").text.strip()

    star_rating = book.select_one(".star-rating")["class"][-1]

    availability = book.select_one(".availability").text.strip()

    return {
        "title": title,
        "price": price,
        "star_rating": star_rating,
        "availability": availability,
        "category": category
    }


def scrape_category(category_url, category_name):
    """Scrape all books from one category."""

    soup = get_soup(category_url)

    books = soup.select("article.product_pod")

    results = []

    for book in books:

        book_data = scrape_book(book, category_name)

        results.append(book_data)

    return results


if __name__ == "__main__":

    categories = get_categories()

    all_books = []

    selected_categories = []

    for category in categories:

        print("Scraping category:", category["name"])

        books = scrape_category(
            category["url"],
            category["name"]
        )

        all_books.extend(books)

        selected_categories.append(category["name"])

        print("Books found:", len(books))
        print("Total books:", len(all_books))

        if len(selected_categories) >= 3 and len(all_books) >= 60:
            break

    print("\n========================")
    print("Scraping completed")
    print("========================")

    print("Categories scraped:", len(selected_categories))
    print("Category names:", selected_categories)
    print("Total books:", len(all_books))


df = pd.DataFrame(all_books)

print("\nDataFrame shape:", df.shape)

print("\nFirst 5 rows:")
print(df.head())
df.to_csv("data_pipeline/raw_books.csv", index=False)
print("\nRaw data saved to data_pipeline/raw_books.csv")
assert len(df) >= 60, "We need at least 60 books."

assert df["category"].nunique() >= 3, \
    "We need at least 3 categories."

print("\nValidation passed!")
print("Books:", len(df))
print("Categories:", df["category"].nunique())