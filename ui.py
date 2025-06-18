import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QMenuBar,
    QLabel, QLineEdit, QPushButton, QListWidget,
    QMessageBox, QHBoxLayout, QTextEdit, QComboBox
)
from PyQt6.QtGui import QAction, QPixmap, QFont
from PyQt6.QtCore import Qt

from config import load_books, save_books, load_config
from api import fetch_book_info, lookup_by_isbn
from utils import parse_book_item, format_reading_time
from dialogs import PreferencesDialog

class BookTracker(QWidget):
    """Main UI for the Book Tracker application."""

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("📚 Book Reading Tracker")
        self.setGeometry(100, 100, 1400, 1000)

        # Load persistent data
        self.books = load_books()
        self.config = load_config()

        # For search sorting/filtering
        self.search_results = []
        self.original_search_results = []

        # Create tabs
        self.tabs = QTabWidget()
        self.search_tab = QWidget()
        self.read_later_tab = QWidget()
        self.read_books_tab = QWidget()

        self.tabs.addTab(self.search_tab, "🔎 Search Books")
        self.tabs.addTab(self.read_later_tab, "📖 Read Later")
        self.tabs.addTab(self.read_books_tab, "✅ Read Books")

        # Build each tab
        self.setup_search_tab()
        self.setup_read_later_tab()
        self.setup_read_books_tab()

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        # Menu bar
        menu_bar = QMenuBar(self)
        self._create_menu(menu_bar)
        main_layout.setMenuBar(menu_bar)

    def _create_menu(self, menu_bar):
        """Build the Preferences and About menus."""
        # Preferences
        pref_menu = menu_bar.addMenu("Preferences")
        pref_action = QAction("Settings", self)
        pref_action.triggered.connect(self._show_preferences)
        pref_menu.addAction(pref_action)

        # About
        about_menu = menu_bar.addMenu("About")
        about_action = QAction("About BookTracker", self)
        about_action.triggered.connect(self._show_about)
        about_menu.addAction(about_action)

    def _show_preferences(self):
        """Display the preferences dialog."""
        PreferencesDialog(self).exec()

    def _show_about(self):
        """Display the About dialog."""
        QMessageBox.about(
            self,
            "About BookTracker",
            "BookTracker v1.0\nDeveloped by Jacob Asher"
        )

    # Search Tab
    def setup_search_tab(self):
        layout = QVBoxLayout()

        # Search input & button
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter title, author, or ISBN")
        self.search_input.returnPressed.connect(self.search_books)

        self.search_button = QPushButton("🔍 Search")
        self.search_button.clicked.connect(self.search_books)

        # Sort & filter controls
        self.sorting_combo = QComboBox()
        self.sorting_combo.addItems([
            "Sort by Relevance",
            "Sort by Title A-Z",
            "Sort by Title Z-A",
            "Sort by Rating Ascending",
            "Sort by Rating Descending"
        ])
        self.sorting_combo.currentIndexChanged.connect(self.sort_search_results)

        self.genre_combo = QComboBox()
        self.genre_combo.addItem("All Genres")
        self.genre_combo.currentIndexChanged.connect(self.filter_by_genre)

        # Results list
        self.search_results_list = QListWidget()
        self.search_results_list.itemClicked.connect(self.show_book_details)

        # Detail view
        self.book_details = QTextEdit()
        self.book_details.setReadOnly(True)

        self.cover_image_label = QLabel()
        self.cover_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_image_label.setFixedSize(200, 300)
        self.cover_image_label.setStyleSheet("border:1px solid #444;")

        # Add buttons
        btn_layout = QHBoxLayout()
        self.add_read_later_btn = QPushButton("📌 Add to Read Later")
        self.add_read_later_btn.clicked.connect(self.add_to_read_later)
        self.add_read_btn = QPushButton("✅ Add to Read")
        self.add_read_btn.clicked.connect(self.add_to_read)
        btn_layout.addWidget(self.add_read_later_btn)
        btn_layout.addWidget(self.add_read_btn)

        # Assemble layout
        layout.addWidget(QLabel("🔎 Search for a Book:"))
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_button)
        layout.addWidget(QLabel("Sort Results:"))
        layout.addWidget(self.sorting_combo)
        layout.addWidget(QLabel("Filter by Genre:"))
        layout.addWidget(self.genre_combo)
        layout.addWidget(QLabel("📚 Search Results:"))
        layout.addWidget(self.search_results_list)
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("📖 Book Details:"))

        detail_layout = QHBoxLayout()
        detail_layout.addWidget(self.book_details)
        detail_layout.addWidget(self.cover_image_label)
        layout.addLayout(detail_layout)

        self.search_tab.setLayout(layout)

    def search_books(self):
        """Perform a search via Google Books API or ISBN lookup."""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Input Error", "Please enter a search term.")
            return

        self.search_results_list.clear()

        # If ISBN, use isbnlib
        if lookup_by_isbn(query):
            title = lookup_by_isbn(query)
            self.search_results_list.addItem(title)
            return

        # Otherwise use API
        data = fetch_book_info(query)
        if not data or "items" not in data:
            return

        self.search_results.clear()
        self.original_search_results.clear()
        genres = set()

        for item in data["items"]:
            info = item["volumeInfo"]
            title = info.get("title", "Unknown Title")
            author = ", ".join(info.get("authors", ["Unknown Author"]))
            rating = info.get("averageRating", "No Rating")
            genre = ", ".join(info.get("categories", ["No Genre Available"]))
            self.search_results.append((title, author, rating, genre))
            self.original_search_results.append((title, author, rating, genre))
            genres.update(info.get("categories", []))

        # Update genre filter and display
        self.genre_combo.blockSignals(True)
        self.genre_combo.clear()
        self.genre_combo.addItem("All Genres")
        self.genre_combo.addItems(sorted(genres))
        self.genre_combo.blockSignals(False)

        self.sort_search_results()

    def sort_search_results(self):
        """Sort the in-memory search_results then filter."""
        if not self.search_results:
            return

        method = self.sorting_combo.currentText()
        if method == "Sort by Relevance":
            self.search_results = self.original_search_results.copy()
        else:
            key_map = {
                "Sort by Title A-Z": lambda x: x[0].lower(),
                "Sort by Title Z-A": lambda x: x[0].lower(),
                "Sort by Rating Ascending": lambda x: float(x[2]) if x[2] != "No Rating" else float("inf"),
                "Sort by Rating Descending": lambda x: float(x[2]) if x[2] != "No Rating" else float("-inf")
            }
            reverse = method in ("Sort by Title Z-A", "Sort by Rating Descending")
            if method in key_map:
                self.search_results = sorted(self.search_results, key=key_map[method], reverse=reverse)

        self.filter_by_genre()

    def filter_by_genre(self):
        """Filter sorted results by the selected genre and display."""
        genre = self.genre_combo.currentText()
        self.search_results_list.clear()
        for title, author, rating, g in self.search_results:
            if genre == "All Genres" or genre in g:
                self.search_results_list.addItem(f"{title} - {author} - Rating: {rating}")

    def show_book_details(self):
        """Fetch and display HTML‐formatted book details and cover."""
        item = self.search_results_list.currentItem()
        if not item:
            return
        title, _ = parse_book_item(item.text())
        data = fetch_book_info(title)
        if not data or "items" not in data:
            return

        info = data["items"][0]["volumeInfo"]
        authors = ", ".join(info.get("authors", []))
        categories = ", ".join(info.get("categories", []))
        rating = info.get("averageRating", "No Rating")
        pub_date = info.get("publishedDate", "Unknown")
        pages = info.get("pageCount", "N/A")
        desc = info.get("description", "")

        html = (
            f"<b>Title:</b> {info.get('title','')}<br>"
            f"<b>Author:</b> {authors}<br>"
            f"<b>Genre:</b> {categories}<br>"
            f"<b>Rating:</b> {rating}<br>"
            f"<b>Published:</b> {pub_date}<br>"
            f"<b>Pages:</b> {pages}<br><br>"
            f"<b>Blurb:</b><br>{desc}"
        )
        self.book_details.setHtml(html)

        # Cover image
        thumb = info.get("imageLinks", {}).get("thumbnail", "")
        if thumb:
            try:
                resp = fetch_book_info(thumb)
                pix = QPixmap()
                pix.loadFromData(req := __import__('requests').get(thumb).content)
                self.cover_image_label.setPixmap(pix.scaled(
                    self.cover_image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
            except Exception:
                self.cover_image_label.clear()
        else:
            self.cover_image_label.clear()

    # Read Later Tab
    def setup_read_later_tab(self):
        layout = QVBoxLayout()
        self.read_later_list = QListWidget()
        for b in self.books.get("read_later", []):
            rt = format_reading_time(b["word_count"])
            self.read_later_list.addItem(f"{b['title']} - {b['author']} - ETA: {rt}")

        btns = QHBoxLayout()
        mv = QPushButton("➡ Move to Read")
        mv.clicked.connect(self.move_to_read)
        rm = QPushButton("❌ Remove")
        rm.clicked.connect(self.remove_from_read_later)
        btns.addWidget(mv); btns.addWidget(rm)

        layout.addWidget(QLabel("📌 Read Later"))
        layout.addWidget(self.read_later_list)
        layout.addLayout(btns)
        self.read_later_tab.setLayout(layout)

    # Read Books Tab
    def setup_read_books_tab(self):
        layout = QVBoxLayout()
        self.read_books_list = QListWidget()
        for b in self.books.get("read_books", []):
            self.read_books_list.addItem(f"{b['title']} - {b['author']}")

        self.read_books_list.itemClicked.connect(self.load_notes)
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Your notes...")
        save = QPushButton("💾 Save Notes")
        save.clicked.connect(self.save_notes)
        rm = QPushButton("❌ Remove from Read")
        rm.clicked.connect(self.remove_from_read)

        layout.addWidget(QLabel("✅ Read Books"))
        layout.addWidget(self.read_books_list)
        layout.addWidget(QLabel("📝 Notes"))
        layout.addWidget(self.notes_edit)
        layout.addWidget(save)
        layout.addWidget(rm)
        self.read_books_tab.setLayout(layout)

    # Add / Move / Remove
    def add_to_read_later(self):
        self._add_book_to_list("read_later", self.read_later_list)

    def add_to_read(self):
        self._add_book_to_list("read_books", self.read_books_list)

    def _add_book_to_list(self, key, widget):
        item = self.search_results_list.currentItem()
        if not item:
            return
        title, _ = parse_book_item(item.text())
        data = fetch_book_info(title)
        if not data or "items" not in data:
            return

        info = data["items"][0]["volumeInfo"]
        page_count = info.get("pageCount", 0)
        wc = page_count * 275
        book = {"title": info.get("title",""), "author": ", ".join(info.get("authors",[])), "word_count": wc}
        if book not in self.books[key]:
            self.books[key].append(book)
            widget.addItem(f"{book['title']} - {book['author']} - ETA: {format_reading_time(wc)}")
            save_books(self.books)

    def move_to_read(self):
        self._move_book(self.read_later_list, "read_later", self.read_books_list, "read_books")

    def remove_from_read_later(self):
        self._remove_book(self.read_later_list, "read_later")

    def remove_from_read(self):
        self._remove_book(self.read_books_list, "read_books")

    def _move_book(self, src, src_key, dst, dst_key):
        item = src.currentItem()
        if not item:
            return
        title, author = parse_book_item(item.text())
        for b in self.books[src_key]:
            if b["title"] == title and b["author"] == author:
                self.books[src_key].remove(b)
                self.books[dst_key].append(b)
                dst.addItem(f"{b['title']} - {b['author']} - ETA: {format_reading_time(b['word_count'])}")
                src.takeItem(src.row(item))
                save_books(self.books)
                break

    def _remove_book(self, widget, key):
        item = widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Selection Error", "Please select a book.")
            return
        title, author = parse_book_item(item.text())
        for b in self.books[key]:
            if b["title"] == title and b["author"] == author:
                self.books[key].remove(b)
                widget.takeItem(widget.row(item))
                save_books(self.books)
                break

    # Notes
    def save_notes(self):
        item = self.read_books_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Selection Error", "Select a book first.")
            return
        title, author = parse_book_item(item.text())
        for b in self.books["read_books"]:
            if b["title"] == title and b["author"] == author:
                b["notes"] = self.notes_edit.toPlainText()
                save_books(self.books)
                QMessageBox.information(self, "Saved", "Notes updated.")
                break

    def load_notes(self):
        item = self.read_books_list.currentItem()
        if not item:
            return
        title, author = parse_book_item(item.text())
        for b in self.books["read_books"]:
            if b["title"] == title and b["author"] == author:
                self.notes_edit.setPlainText(b.get("notes",""))
                break

    # Appearance
    def apply_saved_theme(self):
        from qt_material import apply_stylesheet
        apply_stylesheet(self.app, theme=self.config["theme"])

    def set_font(self, family, size):
        font = QFont(family, size)
        self.setFont(font)
        self.app.setFont(font)
        self._update_fonts(self)

    def _update_fonts(self, widget):
        widget.setFont(self.font())
        for c in widget.findChildren(QWidget):
            c.setFont(self.font())
            self._update_fonts(c)

    def change_theme(self, theme):
        self.config["theme"] = theme
        from config import save_config
        save_config(self.config)
        self.apply_saved_theme()