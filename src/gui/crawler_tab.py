import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QComboBox, QPushButton, QProgressBar, QTextEdit, QCheckBox,
    QGroupBox, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

from analyzer.database import get_all_accounts
from crawler.instagram import crawl_account


class CrawlerSignals(QObject):
    log = pyqtSignal(str)
    progress = pyqtSignal(int, int)
    account_done = pyqtSignal(str, int)
    all_done = pyqtSignal()


class CrawlerTab(QWidget):
    def __init__(self, on_done_cb=None):
        super().__init__()
        self.on_done_cb = on_done_cb
        self._stop = False
        self.signals = CrawlerSignals()
        self.signals.log.connect(self._append_log)
        self.signals.progress.connect(self._update_progress)
        self.signals.all_done.connect(self._on_all_done)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        # 설정 영역
        settings_row = QHBoxLayout()

        grp_settings = QGroupBox("수집 설정")
        grp_layout = QHBoxLayout(grp_settings)

        grp_layout.addWidget(QLabel("최근 게시물 수:"))
        self.spin_count = QSpinBox()
        self.spin_count.setRange(5, 200)
        self.spin_count.setValue(30)
        self.spin_count.setFixedWidth(80)
        grp_layout.addWidget(self.spin_count)
        grp_layout.addSpacing(20)

        grp_layout.addWidget(QLabel("딜레이(초):"))
        self.spin_delay = QSpinBox()
        self.spin_delay.setRange(1, 10)
        self.spin_delay.setValue(3)
        self.spin_delay.setFixedWidth(70)
        grp_layout.addWidget(self.spin_delay)
        grp_layout.addStretch()

        settings_row.addWidget(grp_settings)
        root.addLayout(settings_row)

        # 계정 선택
        acct_label = QLabel("수집할 계정 선택")
        acct_label.setObjectName("label_section")
        root.addWidget(acct_label)

        acct_row = QHBoxLayout()

        self.acct_list = QListWidget()
        self.acct_list.setMaximumHeight(140)
        self.acct_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        acct_row.addWidget(self.acct_list, stretch=3)

        acct_btn_col = QVBoxLayout()
        acct_btn_col.setAlignment(Qt.AlignmentFlag.AlignTop)
        btn_refresh = QPushButton("목록 새로고침")
        btn_refresh.setObjectName("btn_secondary")
        btn_refresh.clicked.connect(self.refresh_accounts)
        acct_btn_col.addWidget(btn_refresh)
        btn_all = QPushButton("전체 선택")
        btn_all.setObjectName("btn_secondary")
        btn_all.clicked.connect(self.acct_list.selectAll)
        acct_btn_col.addWidget(btn_all)
        btn_none = QPushButton("선택 해제")
        btn_none.setObjectName("btn_secondary")
        btn_none.clicked.connect(self.acct_list.clearSelection)
        acct_btn_col.addWidget(btn_none)
        acct_row.addLayout(acct_btn_col, stretch=0)

        root.addLayout(acct_row)

        # 진행률
        self.progress_label = QLabel("대기 중")
        self.progress_label.setObjectName("label_sub")
        root.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        root.addWidget(self.progress_bar)

        # 버튼
        btn_row = QHBoxLayout()
        self.btn_start = QPushButton("수집 시작")
        self.btn_start.clicked.connect(self._start_crawl)
        btn_row.addWidget(self.btn_start)

        self.btn_stop = QPushButton("중단")
        self.btn_stop.setObjectName("btn_danger")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_crawl)
        btn_row.addWidget(self.btn_stop)
        root.addLayout(btn_row)

        # 로그
        log_label = QLabel("수집 로그")
        log_label.setObjectName("label_section")
        root.addWidget(log_label)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background:#111111; border:1px solid #2A2A2A; border-radius:6px; font-family: Consolas, monospace; font-size:11px;")
        root.addWidget(self.log_box, stretch=1)

        self.refresh_accounts()

    def refresh_accounts(self):
        self.acct_list.clear()
        for acc in get_all_accounts():
            label = f"@{acc['username']}  [{('해외' if acc['type'] == 'overseas' else '국내')}]  {acc['genre']}"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, acc)
            self.acct_list.addItem(item)

    def _start_crawl(self):
        selected = self.acct_list.selectedItems()
        if not selected:
            self._append_log("⚠️ 계정을 선택해주세요.")
            return

        self._stop = False
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.log_box.clear()
        self.progress_bar.setValue(0)

        accounts = [item.data(Qt.ItemDataRole.UserRole) for item in selected]
        count = self.spin_count.value()
        delay = float(self.spin_delay.value())

        def run():
            total_accounts = len(accounts)
            for idx, acc in enumerate(accounts):
                if self._stop:
                    break
                self.signals.log.emit(f"\n🔍 [{idx+1}/{total_accounts}] @{acc['username']} 수집 시작...")
                self.signals.progress.emit(0, count)

                crawl_account(
                    account_id=acc["id"],
                    username=acc["username"],
                    followers=acc["followers"],
                    post_count=count,
                    delay=delay,
                    progress_cb=lambda cur, total: self.signals.progress.emit(cur, total),
                    log_cb=lambda msg: self.signals.log.emit(msg),
                    stop_flag=lambda: self._stop,
                )
            self.signals.all_done.emit()

        threading.Thread(target=run, daemon=True).start()

    def _stop_crawl(self):
        self._stop = True
        self.btn_stop.setEnabled(False)
        self._append_log("⏹ 중단 요청됨...")

    def _append_log(self, msg: str):
        self.log_box.append(msg)

    def _update_progress(self, cur: int, total: int):
        pct = int(cur / max(total, 1) * 100)
        self.progress_bar.setValue(pct)
        self.progress_label.setText(f"수집 중... {cur}/{total} ({pct}%)")

    def _on_all_done(self):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress_bar.setValue(100)
        self.progress_label.setText("✅ 수집 완료")
        self._append_log("\n🎉 모든 계정 수집 완료!")
        if self.on_done_cb:
            self.on_done_cb()
