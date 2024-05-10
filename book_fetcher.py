import requests
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY')

def search_books(query, max_results=10):
    GOOGLE_BOOKS_API_URL = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}&key={GOOGLE_API_KEY}"
    try:
        response = requests.get(GOOGLE_BOOKS_API_URL)
        response.raise_for_status()  # Raises an HTTPError for bad responses
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return []
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        return []
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        return []
    except requests.exceptions.RequestException as req_err:
        print(f"Unexpected error occurred: {req_err}")
        return []
    else:
        try:
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
        except KeyError as e:  # In case the JSON structure is different than expected
            print(f"KeyError occurred: Missing key in JSON response - {e}")
            return []
        except TypeError as e:  # In case of issues with data types (e.g., NoneType operations)
            print(f"TypeError occurred: {e}")
            return []
        except Exception as e:  # Catch-all for any other exceptions not specifically caught
            print(f"An unexpected error occurred when processing results: {e}")
            return []

if __name__ == "__main__":
    query = "Python programming"
    books = search_books(query)
    for book in books:
        print(f"Title: {book['title']}")
        print(f"Authors: {book['authors']}")
        print(f"Published Year: {book['publishedYear']}")
        print(f"Summary: {book['summary']}\n")