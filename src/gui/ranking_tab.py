from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QScrollArea, QGridLayout, QFrame, QDoubleSpinBox,
    QSizePolicy, QDialog, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QColor

from analyzer.database import get_posts, toggle_favorite
from analyzer.engagement import er_color


THUMB_SIZE = 180


class PostCard(QFrame):
    clicked = pyqtSignal(dict)

    def __init__(self, post: dict):
        super().__init__()
        self.post = post
        self.setObjectName("post_card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(THUMB_SIZE + 16, THUMB_SIZE + 70)
        self.setStyleSheet("""
            QFrame#post_card {
                background-color: #1A1A1A;
                border: 1px solid #333333;
                border-radius: 8px;
            }
            QFrame#post_card:hover {
                border: 1px solid #C13584;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # 썸네일
        thumb_label = QLabel()
        thumb_label.setFixedSize(THUMB_SIZE, THUMB_SIZE)
        thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb_label.setStyleSheet("background:#111; border-radius:4px;")

        thumb_path = post.get("thumbnail_path", "")
        if thumb_path and Path(thumb_path).exists():
            pix = QPixmap(thumb_path).scaled(
                THUMB_SIZE, THUMB_SIZE,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            thumb_label.setPixmap(pix)
        else:
            thumb_label.setText("📷\n이미지 없음")
            thumb_label.setStyleSheet("background:#111; color:#555; border-radius:4px; font-size:11px;")

        layout.addWidget(thumb_label)

        # 참여율 뱃지
        er = post.get("engagement_rate", 0.0)
        color = er_color(er)
        er_label = QLabel(f"ER {er:.2f}%")
        er_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        er_label.setStyleSheet(f"""
            background-color: {color}22;
            color: {color};
            border: 1px solid {color};
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 11px;
            font-weight: bold;
        """)
        layout.addWidget(er_label)

        # 계정명 + 좋아요
        info = QLabel(f"@{post.get('username','')}  ❤ {post.get('likes',0):,}  💬 {post.get('comments',0):,}")
        info.setObjectName("label_sub")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(False)
        info.setStyleSheet("font-size:10px; color:#888;")
        layout.addWidget(info)

    def mousePressEvent(self, event):
        self.clicked.emit(self.post)


class PostDetailDialog(QDialog):
    def __init__(self, post: dict, parent=None, on_caption_tab=None):
        super().__init__(parent)
        self.post = post
        self.on_caption_tab = on_caption_tab
        self.setWindowTitle(f"@{post.get('username','')}")
        self.setMinimumSize(700, 600)
        self.setStyleSheet("background:#0F0F0F; color:#FFF;")
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 왼쪽: 이미지
        img_label = QLabel()
        img_label.setFixedSize(320, 320)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_label.setStyleSheet("background:#111; border-radius:8px;")
        path = self.post.get("thumbnail_path", "")
        if path and Path(path).exists():
            pix = QPixmap(path).scaled(320, 320, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            img_label.setPixmap(pix)
        else:
            img_label.setText("이미지 없음")
        layout.addWidget(img_label)

        # 오른쪽: 정보
        right = QVBoxLayout()
        er = self.post.get("engagement_rate", 0.0)
        color = er_color(er)

        title = QLabel(f"@{self.post.get('username','')}")
        title.setStyleSheet("font-size:16px; font-weight:bold;")
        right.addWidget(title)

        stats = QLabel(
            f"참여율: <span style='color:{color};font-weight:bold;'>ER {er:.2f}%</span>  |  "
            f"❤ {self.post.get('likes',0):,}  |  "
            f"💬 {self.post.get('comments',0):,}"
        )
        stats.setTextFormat(Qt.TextFormat.RichText)
        right.addWidget(stats)

        sep = QFrame()
        sep.setObjectName("separator")
        right.addWidget(sep)

        right.addWidget(QLabel("원본 캡션"))
        caption_box = QTextEdit()
        caption_box.setPlainText(self.post.get("caption", ""))
        caption_box.setReadOnly(True)
        caption_box.setStyleSheet("background:#1A1A1A; border:1px solid #333; border-radius:6px; color:#CCC; font-size:11px;")
        right.addWidget(caption_box, stretch=1)

        btn_row = QHBoxLayout()

        btn_fav = QPushButton("⭐ 즐겨찾기")
        btn_fav.setObjectName("btn_secondary")
        btn_fav.clicked.connect(self._toggle_fav)
        btn_row.addWidget(btn_fav)

        if self.on_caption_tab:
            btn_caption = QPushButton("✏️ 캡션 재작성")
            btn_caption.clicked.connect(self._go_caption)
            btn_row.addWidget(btn_caption)

        right.addLayout(btn_row)
        layout.addLayout(right)

    def _toggle_fav(self):
        toggle_favorite(self.post["id"])

    def _go_caption(self):
        self.accept()
        if self.on_caption_tab:
            self.on_caption_tab(self.post)


class RankingTab(QWidget):
    request_caption = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._build_ui()
        self.load_posts()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # 왼쪽 필터 패널
        filter_panel = QWidget()
        filter_panel.setFixedWidth(200)
        filter_panel.setStyleSheet("background:#111111; border-right:1px solid #222;")
        fp_layout = QVBoxLayout(filter_panel)
        fp_layout.setContentsMargins(16, 16, 16, 16)
        fp_layout.setSpacing(12)
        fp_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("필터")
        title.setObjectName("label_section")
        fp_layout.addWidget(title)

        fp_layout.addWidget(QLabel("계정 유형"))
        self.combo_type = QComboBox()
        self.combo_type.addItems(["전체", "overseas", "domestic"])
        fp_layout.addWidget(self.combo_type)

        fp_layout.addWidget(QLabel("정렬 기준"))
        self.combo_sort = QComboBox()
        self.combo_sort.addItems(["engagement_rate", "likes", "comments", "collected_at"])
        fp_layout.addWidget(self.combo_sort)

        fp_layout.addWidget(QLabel("최소 참여율 (%)"))
        self.spin_min_er = QDoubleSpinBox()
        self.spin_min_er.setRange(0.0, 20.0)
        self.spin_min_er.setSingleStep(0.5)
        self.spin_min_er.setValue(0.0)
        fp_layout.addWidget(self.spin_min_er)

        fp_layout.addSpacing(8)

        btn_filter = QPushButton("필터 적용")
        btn_filter.clicked.connect(self.load_posts)
        fp_layout.addWidget(btn_filter)

        fp_layout.addStretch()

        self.count_label = QLabel("0개")
        self.count_label.setObjectName("label_sub")
        fp_layout.addWidget(self.count_label)

        root.addWidget(filter_panel)

        # 오른쪽 그리드 영역
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(16, 16, 16, 16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        scroll.setWidget(self.grid_container)
        right_layout.addWidget(scroll)
        root.addWidget(right_widget)

    def load_posts(self):
        # 기존 카드 제거
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        acc_type = self.combo_type.currentText()
        sort_by = self.combo_sort.currentText()
        min_er = self.spin_min_er.value()

        posts = get_posts(acc_type_filter=acc_type, min_er=min_er, sort_by=sort_by, limit=200)
        self.count_label.setText(f"{len(posts)}개")

        cols = 4
        for idx, post in enumerate(posts):
            card = PostCard(post)
            card.clicked.connect(self._show_detail)
            self.grid_layout.addWidget(card, idx // cols, idx % cols)

    def _show_detail(self, post: dict):
        dlg = PostDetailDialog(
            post, self,
            on_caption_tab=lambda p: self.request_caption.emit(p)
        )
        dlg.exec()
