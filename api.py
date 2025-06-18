import os
import requests
from PyQt6.QtWidgets import QMessageBox
from isbnlib import meta

GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes?q="

def fetch_book_info(query):
    key = os.getenv("GOOGLE_BOOKS_API_KEY")
    if not key:
        QMessageBox.critical(None, "Config Error", "Please set GOOGLE_BOOKS_API_KEY in .env")
        return None
    url = f"{GOOGLE_BOOKS_API}{query}&maxResults=40&key={key}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        QMessageBox.warning(None, "API Error", "Failed to fetch results.")
    except requests.RequestException as e:
        QMessageBox.warning(None, "Network Error", f"{e}")
    return None

def lookup_by_isbn(isbn):
    try:
        info = meta(isbn, service="goob")
        return info.get("Title", "Unknown Title")
    except:
        return None