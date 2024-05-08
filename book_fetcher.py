import requests
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY')


def search_books(query, max_results=10):
    GOOGLE_BOOKS_API_URL = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}&key={GOOGLE_API_KEY}"
    response = requests.get(GOOGLE_BOOKS_API_URL)
    if response.status_code == 200:
        result = response.json()
        books = []
        for item in result.get('items', []):
            book_info = {
                'title': '',
                'authors': '',
                'publishedYear': '',
                'summary': ''
            }
            volume_info = item.get('volumeInfo', {})
            book_info['title'] = volume_info.get('title', 'No Title')
            book_info['authors'] = ', '.join(volume_info.get('authors', ['No Authors']))
            book_info['publishedYear'] = volume_info.get('publishedDate', 'No Publication Date')[:4]
            book_info['summary'] = volume_info.get('description', 'No Summary')
            books.append(book_info)
        return books
    else:
        print("Failed to retrieve data from Google Books API")
        return []


if __name__ == "__main__":
    query = "Python programming"
    books = search_books(query)
    for book in books:
        print(f"Title: {book['title']}")
        print(f"Authors: {book['authors']}")
        print(f"Published Year: {book['publishedYear']}")
        print(f"Summary: {book['summary']}\n")