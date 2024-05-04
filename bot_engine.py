import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

for package in ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']:
    nltk.download(package, quiet=True)

books_db = [
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Novel", "summary": "Set in the Jazz Age on Long Island, the novel depicts narrator Nick Carraway's interactions with mysterious millionaire Jay Gatsby and Gatsby's obsession to reunite with his former lover, Daisy Buchanan."},
    {"title": "1984", "author": "George Orwell", "genre": "Dystopian", "summary": "A dystopian social science fiction novel and cautionary tale. It centers on the consequences of government over-reach, totalitarianism, mass surveillance, and repressive regimentation of all persons and behaviours within society."},
    {"title": "Pride and Prejudice", "author": "Jane Austen", "genre": "Classic Regency Novel", "summary": "The novel follows the character development of Elizabeth Bennet, the dynamic protagonist, who learns about the repercussions of hasty judgments and comes to appreciate the difference between superficial goodness and actual goodness."}
]

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    filtered_tokens = [lemmatizer.lemmatize(word) for word in tokens if word.isalnum() and word not in stop_words]
    return filtered_tokens

def find_books_by_genre(genre):
    genre_lower = genre.lower()
    return [book for book in books_db if genre_lower in book["genre"].lower()]

def find_books_by_author(author):
    author_lower = author.lower()
    return [book for book in books_db if author_lower in book["author"].lower()]

def book_details(title):
    title_lower = title.lower()
    for book in books_db:
        if title_lower == book["title"].lower():
            return book
    return None

def handle_query(query):
    processed_query = preprocess_text(query)
    tagged_query = nltk.pos_tag(processed_query)
    
    nouns = [word for word, tag in tagged_query if tag.startswith('NN')]
    verbs = [word for word, tag in tagged_query if tag.startswith('VB')]
    
    verbs_set = set(verbs)  

    if 'recommend' in verbs_set or 'suggest' in verbs_set:
        for noun in nouns:
            genre_books = find_books_by_genre(noun)
            if genre_books:
                return f"Books in {noun} genre: " + ', '.join([book['title'] for book in genre_books])
    elif 'author' in nouns:
        for noun in nouns:
            author_books = find_books_by_author(noun)
            if author_books:
                return f"Books by {noun}: " + ', '.join([book['title'] for book in author_books])
    elif 'detail' in nouns or 'summary' in nouns:
        for noun in nouns:
            book_detail = book_details(noun)
            if book_detail:
                return f"Title: {book_detail['title']} Author: {book_detail['author']} Summary: {book_detail['summary']}"
    
    return "I'm sorry, I couldn't find anything matching your query."

if __name__ == "__main__":
    user_query = input("Hello! How can I assist you with books today?\n")
    print(handle_query(user_query))