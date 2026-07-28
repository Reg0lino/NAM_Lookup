import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.styles import DARK_THEME_QSS


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("NAM Hardware Finder")

    # Apply Dark Theme
    app.setStyleSheet(DARK_THEME_QSS)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
