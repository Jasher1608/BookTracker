import sys, os
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication
from ui import BookTracker

def main():
    # Determine where to look for .env
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        bundle_dir = sys._MEIPASS
    else:
        # Running in normal Python
        bundle_dir = os.path.dirname(__file__)

    dotenv_path = os.path.join(bundle_dir, '.env')
    load_dotenv(dotenv_path)

    app = QApplication(sys.argv)
    win = BookTracker(app)
    win.show()

    # Apply saved theme & font after show
    from config import save_config
    win.apply_saved_theme()
    font, size = win.config["font"], win.config["font_size"]
    win.set_font(font, size)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()