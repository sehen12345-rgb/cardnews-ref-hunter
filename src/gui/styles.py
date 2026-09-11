DARK_STYLE = """
QMainWindow, QDialog, QWidget {
    background-color: #0F0F0F;
    color: #FFFFFF;
    font-family: '맑은 고딕', 'Malgun Gothic', sans-serif;
    font-size: 12px;
}

QTabWidget::pane {
    border: 1px solid #333333;
    background-color: #0F0F0F;
}

QTabBar::tab {
    background-color: #1A1A1A;
    color: #AAAAAA;
    padding: 10px 22px;
    border: none;
    font-size: 13px;
}

QTabBar::tab:selected {
    background-color: #222222;
    color: #FFFFFF;
    border-bottom: 2px solid #C13584;
}

QTabBar::tab:hover:!selected {
    background-color: #222222;
    color: #FFFFFF;
}

QPushButton {
    background-color: #C13584;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #E1306C;
}

QPushButton:disabled {
    background-color: #333333;
    color: #666666;
}

QPushButton#btn_secondary {
    background-color: #2A2A2A;
    color: #CCCCCC;
    border: 1px solid #444444;
}

QPushButton#btn_secondary:hover {
    background-color: #333333;
    color: #FFFFFF;
}

QPushButton#btn_danger {
    background-color: #3A1A1A;
    color: #FF4444;
    border: 1px solid #FF4444;
}

QPushButton#btn_danger:hover {
    background-color: #FF4444;
    color: #FFFFFF;
}

QPushButton#btn_success {
    background-color: #00C896;
    color: #000000;
}

QPushButton#btn_success:hover {
    background-color: #00DFA9;
}

QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox {
    background-color: #222222;
    border: 1px solid #444444;
    border-radius: 6px;
    color: #FFFFFF;
    padding: 6px 10px;
    selection-background-color: #C13584;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #C13584;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    width: 0;
}

QComboBox QAbstractItemView {
    background-color: #222222;
    border: 1px solid #444444;
    color: #FFFFFF;
    selection-background-color: #C13584;
}

QListWidget {
    background-color: #1A1A1A;
    border: 1px solid #333333;
    border-radius: 6px;
    color: #FFFFFF;
    outline: none;
}

QListWidget::item {
    padding: 8px 10px;
    border-bottom: 1px solid #2A2A2A;
}

QListWidget::item:selected {
    background-color: #2C1A28;
    color: #FFFFFF;
}

QListWidget::item:hover {
    background-color: #222222;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #1A1A1A;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #444444;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #C13584;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QProgressBar {
    background-color: #222222;
    border: 1px solid #333333;
    border-radius: 4px;
    text-align: center;
    color: #FFFFFF;
    font-size: 11px;
    height: 18px;
}

QProgressBar::chunk {
    background-color: #C13584;
    border-radius: 3px;
}

QLabel {
    color: #FFFFFF;
}

QLabel#label_sub {
    color: #AAAAAA;
    font-size: 11px;
}

QLabel#label_section {
    color: #FFFFFF;
    font-size: 13px;
    font-weight: bold;
    padding: 4px 0;
    border-bottom: 1px solid #333333;
}

QFrame#separator {
    background-color: #333333;
    max-height: 1px;
}

QSplitter::handle {
    background-color: #333333;
    width: 1px;
}

QGroupBox {
    border: 1px solid #333333;
    border-radius: 6px;
    margin-top: 8px;
    padding-top: 8px;
    color: #AAAAAA;
    font-size: 11px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 4px;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #333333;
    border: none;
    width: 18px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #C13584;
}

QCheckBox {
    color: #CCCCCC;
    spacing: 6px;
}

QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #555555;
    border-radius: 3px;
    background-color: #222222;
}

QCheckBox::indicator:checked {
    background-color: #C13584;
    border-color: #C13584;
}
"""
