from PyQt6.QtWidgets import QMainWindow, QTabWidget, QStatusBar, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from gui.account_tab import AccountTab
from gui.crawler_tab import CrawlerTab
from gui.ranking_tab import RankingTab
from gui.caption_tab import CaptionTab
from gui.styles import DARK_STYLE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CardNews Reference Hunter")
        self.setMinimumSize(1280, 800)
        self.setStyleSheet(DARK_STYLE)

        self._build_tabs()
        self._build_status_bar()

    def _build_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)

        # 탭 1: 계정 관리
        self.account_tab = AccountTab()
        self.tabs.addTab(self.account_tab, "📋  계정 관리")

        # 탭 2: 수집
        self.crawler_tab = CrawlerTab(on_done_cb=self._on_crawl_done)
        self.tabs.addTab(self.crawler_tab, "🔍  수집")

        # 탭 3: 랭킹 뷰
        self.ranking_tab = RankingTab()
        self.ranking_tab.request_caption.connect(self._go_to_caption)
        self.tabs.addTab(self.ranking_tab, "📊  랭킹 뷰")

        # 탭 4: 캡션 재작성
        self.caption_tab = CaptionTab()
        self.tabs.addTab(self.caption_tab, "✏️  캡션 재작성")

        self.setCentralWidget(self.tabs)

    def _build_status_bar(self):
        bar = QStatusBar()
        bar.setStyleSheet("background:#111111; color:#666; font-size:11px; border-top:1px solid #222;")
        self.status_label = QLabel("준비됨")
        bar.addWidget(self.status_label)
        self.setStatusBar(bar)

    def _on_crawl_done(self):
        self.ranking_tab.load_posts()
        self.status_label.setText("✅ 수집 완료 — 랭킹 뷰 업데이트됨")

    def _go_to_caption(self, post: dict):
        self.caption_tab.load_post(post)
        self.tabs.setCurrentIndex(3)
