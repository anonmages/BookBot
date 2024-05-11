import requests
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY')

def fetch_books_by_query(search_query, max_results=10):
    GOOGLE_BOOKS_QUERY_URL = f"https://www.googleapis.com/books/v1/volumes?q={search_query}&maxResults={max_results}&key={GOOGLE_API_KEY}"
    try:
        response = requests.get(GOOGLE_BOOKS_QUERY_URL)
        response.raise_for_status()  # Raises an error for bad responses
    except requests.exceptions.HTTPError as http_error:
        print(f"HTTP error occurred: {http_error}")
        return []
    except requests.exceptions.ConnectionError as connection_error:
        print(f"Connection error occurred: {connection_error}")
        return []
    except requests.exceptions.Timeout as timeout_error:
        print(f"Timeout error occurred: {timeout_error}")
        return []
    except requests.exceptions.RequestException as request_error:
        print(f"Unexpected error occurred: {request_error}")
        return []
    else:
        return parse_books_response(response)

def parse_books_response(response):
    try:
        results = response.json()
        books = []
        for item in results.get('items', []):
            book_details = {
                'title': '',
                'authors': '',
                'published_year': '',
                'summary': ''
            }
            volume_information = item.get('volumeInfo', {})
            book_details['title'] = volume_information.get('title', 'No Title')
            book_details['authors'] = ', '.join(volume_information.get('authors', ['No Authors']))
            book_details['published_year'] = volume_information.get('publishedDate', 'No Publication Date')[:4]
            book_details['summary'] = volume_information.get('description', 'No Summary')
            books.append(book_details)
        return books
    except KeyError as key_error:
        print(f"KeyError occurred: Missing key in JSON response - {key_error}")
        return []
    except TypeError as type_error:
        print(f"TypeError occurred: {type_error}")
        return []
    except Exception as general_error:
        print(f"An unexpected error occurred when processing results: {general_error}")
        return []

if __name__ == "__main__":
    search_query = "Python programming"
    found_books = fetch_books_by_query(search_query)
    for book in found_books:
        print(f"Title: {book['title']}")
        print(f"Authors: {book['authors']}")
        print(f"Published Year: {book['published_year']}")
        print(f"Summary: {book['summary']}\n")