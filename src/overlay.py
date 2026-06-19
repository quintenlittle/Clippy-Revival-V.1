"""
The overlay window, styled after the classic Office Assistant: a big
draggable Clippy floating on the desktop. Right-click for actions
(Read / Ask / Terminate). Replies pop up in a fixed-size speech bubble
above his head and type out like a typewriter. The bubble is always the
same height -- a scrollbar appears automatically for longer replies.
Clippy's position is locked by anchoring the window's bottom-right corner
whenever the bubble shows or hides.
"""
import random
import sys
import threading
from pathlib import Path

import keyboard
from PySide6.QtCore import Qt, QObject, Signal, QRectF, QTimer, QSize
from PySide6.QtGui import QPixmap, QIcon, QAction, QPainter, QPainterPath, QPen, QColor, QMovie
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QSystemTrayIcon, QMenu, QLayout, QGraphicsDropShadowEffect,
    QScrollArea, QFrame,
)

from config import load_config, get_active_backend
import capture
from paths import resource_path

ASSETS_DIR = Path(resource_path("assets"))
ANIM_DIR = ASSETS_DIR / "animations"
AVATAR_DISPLAY_SIZE = 170

# Bubble inner content area -- fixed, never changes.
# Total bubble height will be INNER_H + top/bottom padding + tail.
INNER_W = 150
INNER_H = 160   # tune this if you want a taller/shorter bubble


class HotkeySignals(QObject):
    toggle = Signal()


class AskSignals(QObject):
    finished = Signal(str)


class AskInput(QLineEdit):
    escape_pressed = Signal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.escape_pressed.emit()
        else:
            super().keyPressEvent(event)


class SpeechBubble(QWidget):
    """Fixed-size speech bubble. The scroll area is always INNER_H tall;
    Qt shows the scrollbar automatically when content is taller than that."""

    TAIL_H = 12
    TAIL_W = 18

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.text_label = QLabel("")
        self.text_label.setWordWrap(True)
        self.text_label.setFixedWidth(INNER_W)
        self.text_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.text_label.setStyleSheet(
            "background: transparent; color: #1a1a1a; "
            "font-family: 'Comic Sans MS'; font-size: 12px;"
        )

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.text_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # Fixed dimensions -- the bubble NEVER resizes.
        self.scroll_area.setFixedWidth(INNER_W + 14)   # +14 for scrollbar room
        self.scroll_area.setFixedHeight(INNER_H)
        self.scroll_area.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            "QScrollBar:vertical { background: rgba(0,0,0,30); width: 7px; margin: 0; border-radius: 3px; }"
            "QScrollBar::handle:vertical { background: rgba(0,0,0,110); border-radius: 3px; min-height: 18px; }"
            "QScrollBar::add-line, QScrollBar::sub-line { height: 0; }"
        )
        self.scroll_area.viewport().setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(11, 8, 11, 8 + self.TAIL_H)
        layout.addWidget(self.scroll_area)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 140))
        self.setGraphicsEffect(shadow)

        # Fix the bubble's own size so it never participates in layout sizing.
        self.setFixedSize(self.sizeHint())

    def setText(self, text):
        self.text_label.setText(text)
        self.scroll_area.verticalScrollBar().setValue(0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        body = QRectF(2, 2, self.width() - 4, self.height() - self.TAIL_H - 4)
        path = QPainterPath()
        path.addRoundedRect(body, 14, 14)
        tail_cx = body.left() + 24
        tail = QPainterPath()
        tail.moveTo(tail_cx - self.TAIL_W / 2, body.bottom())
        tail.lineTo(tail_cx, body.bottom() + self.TAIL_H)
        tail.lineTo(tail_cx + self.TAIL_W / 2, body.bottom())
        tail.closeSubpath()
        painter.setBrush(QColor(255, 255, 250))
        painter.setPen(QPen(QColor(30, 30, 30), 1.5))
        painter.drawPath(path.united(tail))


class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.backend = None
        self.backend_error = None
        self._last_context = ""
        self._last_reply = ""
        self._tw_timer = None
        self._tw_text = ""
        self._tw_index = 0
        self._tw_step = 1

        self._load_backend()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_pos = None

        self.ask_signals = AskSignals()
        self.ask_signals.finished.connect(self._on_reply_ready)

        self._build_ui()
        self._build_tray()
        self._register_hotkeys()

        if self.backend_error:
            self._show_bubble(f"Backend not ready: {self.backend_error} — edit config.json and restart.")

    # ---------- setup ----------

    def _load_backend(self):
        try:
            self.backend = get_active_backend(self.cfg)
            self.backend_error = None
        except Exception as e:
            self.backend = None
            self.backend_error = str(e)

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 16, 20, 16)
        outer.setSpacing(4)
        outer.setSizeConstraint(QLayout.SetFixedSize)

        # Speech bubble -- hidden at start, fixed size when shown.
        self.bubble = SpeechBubble()
        self.bubble.setVisible(False)
        outer.addWidget(self.bubble, alignment=Qt.AlignLeft)

        # Big Clippy avatar.
        self.avatar_label = QLabel()
        self.avatar_label.setStyleSheet("background: transparent;")
        pix = QPixmap(str(ASSETS_DIR / "avatar.png"))
        self._static_pixmap = (
            pix.scaled(AVATAR_DISPLAY_SIZE, AVATAR_DISPLAY_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if not pix.isNull() else QPixmap()
        )
        self.avatar_label.setPixmap(self._static_pixmap)
        self.avatar_label.setFixedSize(AVATAR_DISPLAY_SIZE, AVATAR_DISPLAY_SIZE)
        self.avatar_label.setToolTip(
            f"Clippy — {self.cfg.get('active_backend')} (right-click for options)"
        )
        self.avatar_label.setAlignment(Qt.AlignCenter)
        outer.addWidget(self.avatar_label, alignment=Qt.AlignHCenter)
        self._movie = None

        # Ask input -- hidden until "Ask" is chosen.
        self.ask_input = AskInput()
        self.ask_input.setPlaceholderText("Ask Clippy...")
        self.ask_input.returnPressed.connect(self.on_ask_submit)
        self.ask_input.escape_pressed.connect(self.hide_ask_box)
        self.ask_input.setStyleSheet(
            "background-color: rgba(15,15,15,210); color: #fff; "
            "border: 1px solid rgba(255,255,255,70); border-radius: 8px; padding: 6px;"
        )
        self.ask_input.setVisible(False)
        outer.addWidget(self.ask_input)

    def _build_tray(self):
        icon_path = ASSETS_DIR / "icon.ico"
        icon = QIcon(str(icon_path)) if icon_path.exists() else QIcon(str(ASSETS_DIR / "avatar.png"))
        self.tray = QSystemTrayIcon(icon)
        self.tray.setToolTip("Clippy")
        menu = QMenu()
        menu.addAction("Show / Hide", self.toggle_visible)
        menu.addAction("Terminate", QApplication.instance().quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda _: self.toggle_visible())
        self.tray.show()

    def _register_hotkeys(self):
        self.signals = HotkeySignals()
        self.signals.toggle.connect(self.toggle_visible)

        def run():
            try:
                keyboard.add_hotkey(self.cfg["hotkey_toggle"], self.signals.toggle.emit)
                keyboard.wait()
            except Exception as e:
                print(f"[clippy] hotkey failed: {e}")

        threading.Thread(target=run, daemon=True).start()

    # ---------- positioning ----------

    def _anchor_bottom_right(self):
        """Resize to fit content, then slide the window so its bottom-right
        corner stays exactly where it was. Clippy doesn't move on screen."""
        old_br = self.geometry().bottomRight()
        self.adjustSize()
        geo = self.geometry()
        screen = QApplication.primaryScreen().availableGeometry()
        x = max(screen.left(), old_br.x() - geo.width())
        y = max(screen.top(), old_br.y() - geo.height())
        self.move(x, y)

    def position_bottom_right(self):
        """Initial placement — bottom-right of the screen."""
        self.adjustSize()
        geo = self.geometry()
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            screen.right() - geo.width() - 30,
            screen.bottom() - geo.height() - 30,
        )

    # ---------- animation ----------

    def play_random_animation(self):
        if self._movie is not None:
            return  # one already playing -- let it finish
        choices = sorted(ANIM_DIR.glob("clippy-white-*.gif"))
        if not choices:
            self._show_bubble("No animations found in assets/animations.")
            return

        path = random.choice(choices)
        movie = QMovie(str(path))
        movie.setScaledSize(QSize(AVATAR_DISPLAY_SIZE, AVATAR_DISPLAY_SIZE))
        if not movie.isValid():
            return

        self._movie = movie
        self.avatar_label.setMovie(movie)
        movie.frameChanged.connect(lambda _frame, m=movie: self._on_anim_frame(m))
        movie.start()

    def _on_anim_frame(self, movie):
        # Once the last frame of a single pass has been reached, let it sit
        # on screen for its own duration, then revert to the static avatar.
        if movie.frameCount() > 0 and movie.currentFrameNumber() == movie.frameCount() - 1:
            delay = movie.nextFrameDelay() or 100
            QTimer.singleShot(delay, lambda m=movie: self._finish_animation(m))

    def _finish_animation(self, movie):
        if movie is not self._movie:
            return  # a newer animation already replaced this one
        movie.stop()
        self.avatar_label.setMovie(None)
        self.avatar_label.setPixmap(self._static_pixmap)
        self._movie = None

    # ---------- right-click menu ----------

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction("Read", self.on_capture)
        menu.addAction("Ask", self.show_ask_box)
        menu.addAction("Animate", self.play_random_animation)
        menu.addSeparator()
        menu.addAction("Terminate", QApplication.instance().quit)
        menu.exec(event.globalPos())

    # ---------- bubble helpers ----------

    def _show_bubble(self, text):
        """Instant text (status messages). Shows bubble and anchors bottom."""
        if self._tw_timer:
            self._tw_timer.stop()
        was_hidden = not self.bubble.isVisible()
        self.bubble.setText(text)
        self.bubble.setVisible(True)
        if was_hidden:
            self._anchor_bottom_right()

    def _type_out_bubble(self, reply):
        """Show reply with typewriter animation.
        Bubble is fixed size so no resizing happens mid-animation."""
        if self._tw_timer:
            self._tw_timer.stop()
        was_hidden = not self.bubble.isVisible()
        self.bubble.setText(reply)
        self.bubble.text_label.setText("")   # blank -- typewriter fills it in
        self.bubble.setVisible(True)
        if was_hidden:
            self._anchor_bottom_right()

        self._tw_text = reply
        self._tw_index = 0
        self._tw_step = max(1, len(reply) // 120)
        self._tw_timer = QTimer(self)
        self._tw_timer.timeout.connect(self._typewriter_tick)
        self._tw_timer.start(50)   # 50 ms per tick (~half speed vs original 25 ms)

    def _typewriter_tick(self):
        self._tw_index += self._tw_step
        if self._tw_index >= len(self._tw_text):
            self.bubble.text_label.setText(self._tw_text)
            self._tw_timer.stop()
        else:
            self.bubble.text_label.setText(self._tw_text[: self._tw_index])

    # ---------- actions ----------

    def toggle_visible(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def on_capture(self):
        text = capture.capture_context()
        self._last_context = text
        if text.strip():
            self._show_bubble(
                f"Got it — read {len(text)} chars from the active window.\n"
                f"Right-click > Ask to ask about it."
            )
        else:
            self._show_bubble(
                "Couldn't read any text from that window.\n"
                "Try copying the text first, then Read again."
            )
        if not self.isVisible():
            self.show()
            self.raise_()
            self.activateWindow()

    def show_ask_box(self):
        if not self.isVisible():
            self.show()
            self.raise_()
        was_hidden = not self.ask_input.isVisible()
        self.ask_input.setVisible(True)
        if was_hidden:
            self._anchor_bottom_right()
        self.ask_input.setFocus()
        self.activateWindow()

    def hide_ask_box(self):
        self.ask_input.clear()
        self.ask_input.setVisible(False)
        self._anchor_bottom_right()

    def on_ask_submit(self):
        question = self.ask_input.text().strip()
        if not question:
            self.hide_ask_box()
            return
        self.hide_ask_box()

        if self.backend is None:
            self._load_backend()
        if self.backend is None:
            self._show_bubble(f"No working backend ({self.backend_error}). Check config.json.")
            return

        self._show_bubble("Thinking...")

        def worker():
            try:
                reply = self.backend.generate(question, context=self._last_context)
            except Exception as e:
                reply = f"Error talking to {self.cfg.get('active_backend')}: {e}"
            self.ask_signals.finished.emit(reply)

        threading.Thread(target=worker, daemon=True).start()

    def _on_reply_ready(self, reply):
        self._last_reply = reply
        self._type_out_bubble(reply)

    # ---------- drag support ----------

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    # Explicit QToolTip styling -- without this, tooltip popups can render
    # with broken/black backgrounds in a frameless translucent window like
    # this one, since they're separate top-level windows that don't
    # automatically inherit per-widget stylesheets.
    app.setStyleSheet(
        "QToolTip { background-color: rgba(20, 20, 20, 235); color: #ffffff; "
        "border: 1px solid rgba(255,255,255,80); border-radius: 6px; padding: 4px 8px; }"
    )
    win = OverlayWindow()
    win.show()
    QTimer.singleShot(50, win.position_bottom_right)
    sys.exit(app.exec())
