from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QFontComboBox, QPushButton
from PyQt6.QtGui import QFont
from qt_material import apply_stylesheet

THEMES = [
    "dark_teal.xml","light_blue.xml","dark_amber.xml","dark_purple.xml",
    "light_purple.xml","dark_cyan.xml","light_cyan.xml","dark_red.xml","light_red.xml"
]

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Preferences")
        layout = QVBoxLayout()

        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES)
        self.theme_combo.setCurrentText(parent.config["theme"])

        # Font
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont(parent.config["font"]))
        self.font_combo.currentFontChanged.connect(self._update_preview)

        # Size
        self.size_combo = QComboBox()
        self.size_combo.addItems([str(i) for i in range(8,25)])
        self.size_combo.setCurrentText(str(parent.config["font_size"]))

        # Preview
        self.preview = QLabel("Preview Text")
        self.preview.setFont(self.font_combo.currentFont())

        # Save
        save = QPushButton("Save")
        save.clicked.connect(self._save)

        for w in (
            QLabel("Select Theme:"), self.theme_combo,
            QLabel("Select Font:"), self.font_combo,
            QLabel("Font Size:"), self.size_combo,
            self.preview, save
        ):
            layout.addWidget(w)

        self.setLayout(layout)

    def _update_preview(self, font):
        font.setPointSize(int(self.size_combo.currentText()))
        self.preview.setFont(font)

    def _save(self):
        p = self.parent
        p.config["theme"] = self.theme_combo.currentText()
        p.config["font"] = self.font_combo.currentFont().family()
        p.config["font_size"] = int(self.size_combo.currentText())
        from config import save_config
        save_config(p.config)
        apply_stylesheet(p.app, theme=p.config["theme"])
        p.set_font(p.config["font"], p.config["font_size"])
        self.accept()