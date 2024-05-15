import requests
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY')

def fetch_books_by_query(search_query, max_results=10):
    GOOGLE_BOOKS_QUERY_URL = (
        f"https://www.googleapis.com/books/v1/volumes?q="
        f"{search_query}&maxResults={max_results}&key={GOOGLE_API_KEY}"
    )
    response = make_request_to_google_books_api(GOOGLE_BOOKS_QUERY_URL)
    
    if response:
        return parse_books_response(response)
    else:
        return []

def make_request_to_google_books_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  
        return response
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.ConnectionError as err:
        print(f"Connection error occurred: {err}")
    except requests.exceptions.Timeout as err:
        print(f"Timeout error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Unexpected error occurred: {err}")
    return None

def parse_books_response(response):
    try:
        results = response.json()
        return [create_book_dict(item) for item in results.get('items', [])]
    except Exception as err:
        print(f"An error occurred when processing results: {err}")
        return []

def create_book_dict(item):
    volume_information = item.get('volumeInfo', {})
    return {
        'title': volume_information.get('title', 'No Title'),
        'authors': format_authors(volume_information.get('authors', ['No Authors'])),
        'published_year': extract_published_year(
            volume_information.get('publishedDate', 'No Publication Date')),
        'summary': volume_information.get('description', 'No Summary')
    }

def format_authors(authors_list):
    return ', '.join(authors_list)

def extract_published_year(publish_date):
    return publish_date[:4]

if __name__ == "__main__":
    search_query = "Python programming"
    found_books = fetch_books_by_query(search_query)
    
    for book in found_books:
        print(f"Title: {book['title']}")
        print(f"Authors: {book['authors']}")
        print(f"Published Year: {book['published_year']}")
        print(f"Summary: {book['summary']}\n")