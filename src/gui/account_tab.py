from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from analyzer.database import get_all_accounts, add_account, delete_account


class AccountTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh_list()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(20)

        # ---------- 왼쪽: 계정 목록 ----------
        left = QVBoxLayout()

        title = QLabel("등록된 계정")
        title.setObjectName("label_section")
        left.addWidget(title)

        self.list_widget = QListWidget()
        self.list_widget.setMinimumWidth(340)
        left.addWidget(self.list_widget)

        btn_delete = QPushButton("선택 계정 삭제")
        btn_delete.setObjectName("btn_danger")
        btn_delete.clicked.connect(self._delete_selected)
        left.addWidget(btn_delete)

        root.addLayout(left, stretch=1)

        # ---------- 오른쪽: 계정 추가 ----------
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignmentFlag.AlignTop)

        title2 = QLabel("계정 추가")
        title2.setObjectName("label_section")
        right.addWidget(title2)
        right.addSpacing(10)

        right.addWidget(QLabel("인스타그램 유저네임"))
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("@ 없이 입력 (예: healthyliving)")
        right.addWidget(self.input_username)
        right.addSpacing(10)

        right.addWidget(QLabel("계정 유형"))
        self.combo_type = QComboBox()
        self.combo_type.addItems(["overseas", "domestic"])
        right.addWidget(self.combo_type)
        right.addSpacing(10)

        right.addWidget(QLabel("장르"))
        self.combo_genre = QComboBox()
        self.combo_genre.addItems(["헬스", "다이어트", "라이프스타일", "식단", "운동", "기타"])
        right.addWidget(self.combo_genre)
        right.addSpacing(20)

        btn_add = QPushButton("계정 추가")
        btn_add.clicked.connect(self._add_account)
        right.addWidget(btn_add)

        right.addStretch()

        # 안내 박스
        note = QLabel(
            "💡 해외 계정: overseas\n"
            "    국내 계정: domestic\n\n"
            "수집 탭에서 계정별로\n"
            "게시물을 크롤링합니다."
        )
        note.setObjectName("label_sub")
        note.setStyleSheet("background:#1A1A1A; border:1px solid #333; border-radius:6px; padding:12px;")
        note.setWordWrap(True)
        right.addWidget(note)

        root.addLayout(right, stretch=0)

    def refresh_list(self):
        self.list_widget.clear()
        accounts = get_all_accounts()
        for acc in accounts:
            label = (
                f"@{acc['username']}  |  "
                f"{'해외' if acc['type'] == 'overseas' else '국내'}  |  "
                f"{acc['genre']}  |  "
                f"팔로워 {acc['followers']:,}"
            )
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, acc["id"])
            self.list_widget.addItem(item)

    def _add_account(self):
        username = self.input_username.text().strip().lstrip("@")
        if not username:
            QMessageBox.warning(self, "입력 오류", "유저네임을 입력해주세요.")
            return
        add_account(username, self.combo_type.currentText(), self.combo_genre.currentText())
        self.input_username.clear()
        self.refresh_list()

    def _delete_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "선택 없음", "삭제할 계정을 선택해주세요.")
            return
        acc_id = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, "삭제 확인",
            f"정말 삭제하시겠습니까?\n(수집된 게시물도 함께 삭제됩니다)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_account(acc_id)
            self.refresh_list()
