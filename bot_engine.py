import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from functools import lru_cache

for package in ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']:
    nltk.download(package, quiet=True)

books_database = [
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Novel", "summary": "Set in the Jazz Age on Long Island, the novel depicts narrator Nick Carraway's interactions with mysterious millionaire Jay Gatsby and Gatsby's obsession to reunite with his former lover, Daisy Buchanan."},
    {"title": "1984", "author": "George Orwell", "genre": "Dystopian", "summary": "A dystopian social science fiction novel and cautionary tale. It centers on the consequences of government over-reach, totalitarianism, mass surveillance, and repressive regimentation of all persons and behaviors within society."},
    {"title": "Pride and Prejudice", "author": "Jane Austen", "genre": "Classic Regency Novel", "summary": "The novel follows the character development of Elizabeth Bennet, the dynamic protagonist, who learns about the repercussions of hasty judgments and comes to appreciate the difference between superficial goodness and actual goodness."}
]

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

@lru_cache(maxsize=128)
def preprocess_text_for_query(text):
    tokens = word_tokenize(text.lower())
    filtered_tokens = [lemmatizer.lemmatize(word) for word in tokens if word.isalnum() and word not in stop_words]
    return filtered_tokens

@lru_cache(maxsize=32)
def search_books_by_genre(genre):
    genre_lowercase = genre.lower()
    return [book for book in books_database if genre_lowercase in book["genre"].lower()]

@lru_cache(maxsize=32)
def search_books_by_author(author):
    author_lowercase = author.lower()
    return [book for book in books_database if author_lowercase in book["author"].lower()]

@lru_cache(maxsize=32)
def get_book_details_by_title(title):
    title_lowercase = title.lower()
    for book in books_database:
        if title_lowercase == book["title"].lower():
            return book
    return None

def process_user_query(query):
    processed_query = preprocess_text_for_query(query)
    tagged_query = nltk.pos_tag(processed_query)
    
    nouns = [word for word, tag in tagged_query if tag.startswith('NN')]
    verbs = [word for word, tag in tagged_query if tag.startswith('VB')]
    
    unique_verbs = set(verbs)  

    if 'recommend' in unique_verbs or 'suggest' in unique_verbs:
        for noun in nouns:
            books_in_genre = search_books_by_genre(noun)
            if books_in_genre:
                return f"Books in {noun} genre: " + ', '.join([book['title'] for book in books_in_genre])
    elif 'author' in nouns:
        for noun in nouns:
            books_by_author = search_books_by_author(noun)
            if books_by_author:
                return f"Books by {noun}: " + ', '.join([book['title'] for book in books_by_author])
    elif 'detail' in nouns or 'summary' in nouns:
        for noun in nouns:
            specific_book_details = get_book_details_by_title(noun)
            if specific_book_details:
                return f"Title: {specific_book_details['title']} Author: {specific_book_details['author']} Summary: {specific_book_details['summary']}"
    
    return "I'm sorry, I couldn't find anything matching your query."

if __name__ == "__main__":
    user_query = input("Hello! How can I assist you with books today?\n")
    print(process_user_query(user_query))