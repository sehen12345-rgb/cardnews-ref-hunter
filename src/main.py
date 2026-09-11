import sys
from pathlib import Path

# src 폴더를 모듈 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from analyzer.database import init_db
from gui.main_window import MainWindow


def main():
    init_db()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
