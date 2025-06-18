def parse_book_item(item_text):
    parts = item_text.split(" - ")
    title = parts[0].strip()
    author = parts[1].strip() if len(parts)>1 else ""
    return title, author

def format_reading_time(words):
    mins = words // 250
    h, m = divmod(mins, 60)
    return f"{h}h {m}m" if h else f"{m}m"