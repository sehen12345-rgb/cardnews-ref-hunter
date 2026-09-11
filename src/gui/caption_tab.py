import threading
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QFrame, QScrollArea, QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QPixmap

from analyzer.database import get_post_by_id, update_post_captions
from analyzer.similarity import calc_similarity
from analyzer.engagement import er_color
from ai.caption import translate_caption, rewrite_caption, suggest_hooks


class CaptionSignals(QObject):
    translated = pyqtSignal(str)
    rewritten = pyqtSignal(str, float)
    hooks = pyqtSignal(list)
    error = pyqtSignal(str)
    busy = pyqtSignal(bool)


class CaptionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_post = None
        self.signals = CaptionSignals()
        self.signals.translated.connect(self._on_translated)
        self.signals.rewritten.connect(self._on_rewritten)
        self.signals.hooks.connect(self._on_hooks)
        self.signals.error.connect(self._on_error)
        self.signals.busy.connect(self._set_busy)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        # 선택된 게시물 정보
        self.info_label = QLabel("랭킹뷰에서 게시물을 선택하면 여기에 표시됩니다.")
        self.info_label.setObjectName("label_sub")
        self.info_label.setStyleSheet("background:#1A1A1A; border-radius:6px; padding:10px; border:1px solid #333;")
        root.addWidget(self.info_label)

        # 메인 영역 (이미지 + 캡션들)
        main_row = QHBoxLayout()
        main_row.setSpacing(16)

        # 썸네일
        self.thumb_label = QLabel("이미지\n없음")
        self.thumb_label.setFixedSize(200, 200)
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_label.setStyleSheet("background:#111; border-radius:8px; color:#555; border:1px solid #2A2A2A;")
        main_row.addWidget(self.thumb_label, stretch=0)

        # 캡션 영역
        captions_layout = QVBoxLayout()
        captions_layout.setSpacing(10)

        # 원본 캡션
        captions_layout.addWidget(self._section_label("원본 캡션"))
        self.txt_original = QTextEdit()
        self.txt_original.setPlaceholderText("원본 캡션 (선택 후 자동 표시)")
        self.txt_original.setMaximumHeight(120)
        captions_layout.addWidget(self.txt_original)

        # 번역 캡션
        row1 = QHBoxLayout()
        row1.addWidget(self._section_label("번역 (한국어)"))
        row1.addStretch()
        self.btn_translate = QPushButton("번역하기")
        self.btn_translate.setFixedWidth(100)
        self.btn_translate.clicked.connect(self._do_translate)
        row1.addWidget(self.btn_translate)
        captions_layout.addLayout(row1)

        self.txt_translated = QTextEdit()
        self.txt_translated.setPlaceholderText("번역 결과가 여기에 표시됩니다")
        self.txt_translated.setMaximumHeight(120)
        captions_layout.addWidget(self.txt_translated)

        main_row.addLayout(captions_layout, stretch=1)
        root.addLayout(main_row)

        sep = QFrame()
        sep.setObjectName("separator")
        root.addWidget(sep)

        # 재작성 캡션
        rewrite_row = QHBoxLayout()
        rewrite_row.addWidget(self._section_label("재작성 캡션"))
        rewrite_row.addStretch()
        self.similarity_label = QLabel("")
        self.similarity_label.setStyleSheet("font-size:13px; font-weight:bold;")
        rewrite_row.addWidget(self.similarity_label)

        self.btn_rewrite = QPushButton("재작성하기")
        self.btn_rewrite.setFixedWidth(110)
        self.btn_rewrite.clicked.connect(self._do_rewrite)
        rewrite_row.addWidget(self.btn_rewrite)

        self.btn_retry = QPushButton("다시 쓰기")
        self.btn_retry.setObjectName("btn_secondary")
        self.btn_retry.setFixedWidth(100)
        self.btn_retry.clicked.connect(self._do_rewrite)
        rewrite_row.addWidget(self.btn_retry)

        root.addLayout(rewrite_row)

        self.txt_rewritten = QTextEdit()
        self.txt_rewritten.setPlaceholderText("재작성 결과가 여기에 표시됩니다 (직접 편집 가능)")
        self.txt_rewritten.setMinimumHeight(130)
        root.addWidget(self.txt_rewritten, stretch=1)

        sep2 = QFrame()
        sep2.setObjectName("separator")
        root.addWidget(sep2)

        # 훅 카피 제안
        hook_row = QHBoxLayout()
        hook_row.addWidget(self._section_label("썸네일 훅 카피 제안"))
        hook_row.addStretch()
        self.btn_hooks = QPushButton("제안받기")
        self.btn_hooks.setFixedWidth(100)
        self.btn_hooks.clicked.connect(self._do_hooks)
        hook_row.addWidget(self.btn_hooks)
        root.addLayout(hook_row)

        self.hooks_layout = QVBoxLayout()
        self.hooks_layout.setSpacing(6)
        root.addLayout(self.hooks_layout)

        sep3 = QFrame()
        sep3.setObjectName("separator")
        root.addWidget(sep3)

        # 저장 버튼
        save_row = QHBoxLayout()
        save_row.addStretch()
        btn_copy = QPushButton("재작성본 복사")
        btn_copy.setObjectName("btn_secondary")
        btn_copy.clicked.connect(self._copy_rewritten)
        save_row.addWidget(btn_copy)

        btn_save = QPushButton("DB 저장")
        btn_save.setObjectName("btn_success")
        btn_save.clicked.connect(self._save_to_db)
        save_row.addWidget(btn_save)
        root.addLayout(save_row)

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size:12px; font-weight:bold; color:#CCCCCC;")
        return lbl

    def load_post(self, post: dict):
        self.current_post = post
        username = post.get("username", "")
        er = post.get("engagement_rate", 0.0)
        color = er_color(er)

        self.info_label.setText(
            f"@{username}  |  ER <span style='color:{color};font-weight:bold;'>{er:.2f}%</span>"
            f"  |  ❤ {post.get('likes',0):,}  |  💬 {post.get('comments',0):,}"
        )
        self.info_label.setTextFormat(Qt.TextFormat.RichText)

        # 썸네일
        path = post.get("thumbnail_path", "")
        if path and Path(path).exists():
            pix = QPixmap(path).scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.thumb_label.setPixmap(pix)
            self.thumb_label.setText("")
        else:
            self.thumb_label.setPixmap(QPixmap())
            self.thumb_label.setText("이미지\n없음")

        self.txt_original.setPlainText(post.get("caption", ""))
        self.txt_translated.setPlainText(post.get("translated_caption", ""))
        self.txt_rewritten.setPlainText(post.get("rewritten_caption", ""))

        sim = post.get("similarity_score")
        if sim is not None:
            self._update_similarity_label(sim)
        else:
            self.similarity_label.setText("")

        self._clear_hooks()

    def _do_translate(self):
        caption = self.txt_original.toPlainText().strip()
        if not caption:
            return
        self._set_busy(True)

        def run():
            try:
                result = translate_caption(caption)
                self.signals.translated.emit(result)
            except Exception as e:
                self.signals.error.emit(f"번역 오류: {e}")
            finally:
                self.signals.busy.emit(False)

        threading.Thread(target=run, daemon=True).start()

    def _do_rewrite(self):
        caption = self.txt_translated.toPlainText().strip() or self.txt_original.toPlainText().strip()
        if not caption:
            return
        self._set_busy(True)

        def run():
            try:
                rewritten, sim = rewrite_caption(caption)
                self.signals.rewritten.emit(rewritten, sim)
            except Exception as e:
                self.signals.error.emit(f"재작성 오류: {e}")
            finally:
                self.signals.busy.emit(False)

        threading.Thread(target=run, daemon=True).start()

    def _do_hooks(self):
        caption = self.txt_translated.toPlainText().strip() or self.txt_original.toPlainText().strip()
        if not caption:
            return
        self._set_busy(True)

        def run():
            try:
                hooks = suggest_hooks(caption)
                self.signals.hooks.emit(hooks)
            except Exception as e:
                self.signals.error.emit(f"훅 제안 오류: {e}")
            finally:
                self.signals.busy.emit(False)

        threading.Thread(target=run, daemon=True).start()

    def _on_translated(self, text: str):
        self.txt_translated.setPlainText(text)

    def _on_rewritten(self, text: str, sim: float):
        self.txt_rewritten.setPlainText(text)
        self._update_similarity_label(sim)

    def _update_similarity_label(self, sim: float):
        if sim <= 75:
            color = "#00C896"
            icon = "✅"
        elif sim <= 80:
            color = "#FFA500"
            icon = "⚠️"
        else:
            color = "#FF4444"
            icon = "❌"
        self.similarity_label.setText(f"유사도: {sim:.1f}% {icon}")
        self.similarity_label.setStyleSheet(f"font-size:13px; font-weight:bold; color:{color};")

    def _on_hooks(self, hooks: list):
        self._clear_hooks()
        for i, hook in enumerate(hooks, 1):
            row = QHBoxLayout()
            lbl = QLabel(f"{i}. {hook}")
            lbl.setStyleSheet("background:#1A1A1A; border:1px solid #333; border-radius:4px; padding:6px 10px; font-size:12px;")
            lbl.setWordWrap(True)
            row.addWidget(lbl, stretch=1)
            btn_copy = QPushButton("복사")
            btn_copy.setObjectName("btn_secondary")
            btn_copy.setFixedWidth(60)
            btn_copy.clicked.connect(lambda _, h=hook: QApplication.clipboard().setText(h))
            row.addWidget(btn_copy)
            self.hooks_layout.addLayout(row)

    def _clear_hooks(self):
        while self.hooks_layout.count():
            item = self.hooks_layout.takeAt(0)
            if item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()

    def _on_error(self, msg: str):
        self.info_label.setText(f"⚠️ {msg}")

    def _set_busy(self, busy: bool):
        for btn in [self.btn_translate, self.btn_rewrite, self.btn_retry, self.btn_hooks]:
            btn.setEnabled(not busy)

    def _copy_rewritten(self):
        text = self.txt_rewritten.toPlainText()
        QApplication.clipboard().setText(text)

    def _save_to_db(self):
        if not self.current_post:
            return
        translated = self.txt_translated.toPlainText()
        rewritten = self.txt_rewritten.toPlainText()
        sim = calc_similarity(
            self.txt_original.toPlainText(),
            rewritten
        ) if rewritten else None
        update_post_captions(self.current_post["id"], translated, rewritten, sim)
        self.info_label.setText("✅ 저장 완료!")
