# -*- coding: utf-8 -*-
"""
toast_widget.py — Overlay Toast Bildirim Sistemi
E-STOP gibi kritik uyarılar ekranın ortasında, normal mesajlar sağ altta.
"""

from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QGraphicsDropShadowEffect, QGraphicsOpacityEffect
)


class ToastWidget(QWidget):
    """Tek bir toast bildirimi."""

    def __init__(self, parent, message, toast_type="info", duration=3000,
                 persistent=False, center=False):
        super().__init__(parent)
        self.persistent = persistent
        self.center = center
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedWidth(420 if not center else 500)

        # Renk şeması
        colors = {
            "success": ("#052e16", "#16a34a", "#4ade80", "✓"),
            "error":   ("#450a0a", "#dc2626", "#f87171", "⛔"),
            "warning": ("#451a03", "#d97706", "#fbbf24", "⚠"),
            "info":    ("#082f49", "#0891b2", "#67e8f9", "ℹ"),
        }
        bg, border, text_color, icon = colors.get(toast_type, colors["info"])

        # Ana container
        container = QWidget(self)
        container.setStyleSheet(f"""
            background-color: {bg};
            border: 2px solid {border};
            border-radius: 12px;
            padding: 0px;
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(container)

        inner = QHBoxLayout(container)
        inner.setContentsMargins(16, 12, 16, 12)
        inner.setSpacing(12)

        # İkon
        lbl_icon = QLabel(icon)
        font_size = 22 if center else 18
        lbl_icon.setFont(QFont("Segoe UI", font_size))
        lbl_icon.setStyleSheet(f"color: {text_color}; background: transparent;")
        inner.addWidget(lbl_icon)

        # Mesaj
        lbl_msg = QLabel(message)
        msg_font_size = 15 if center else 13
        lbl_msg.setFont(QFont("Segoe UI", msg_font_size, QFont.Bold))
        lbl_msg.setStyleSheet(f"color: {text_color}; background: transparent;")
        lbl_msg.setWordWrap(True)
        inner.addWidget(lbl_msg, 1)

        # Kapatma butonu (persistent toast'lar için)
        if persistent:
            btn_close = QPushButton("✕")
            btn_close.setFont(QFont("Segoe UI", 12, QFont.Bold))
            btn_close.setFixedSize(28, 28)
            btn_close.setCursor(Qt.PointingHandCursor)
            btn_close.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color};
                    border: 1px solid {border};
                    border-radius: 14px;
                }}
                QPushButton:hover {{
                    background-color: {border};
                    color: white;
                }}
            """)
            btn_close.clicked.connect(self._close_toast)
            inner.addWidget(btn_close)

        # Glow efekti
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(border))
        shadow.setOffset(0, 4)
        container.setGraphicsEffect(shadow)

        self.adjustSize()

        # Otomatik kapanma (persistent değilse)
        if not persistent:
            QTimer.singleShot(duration, self._close_toast)

    def _close_toast(self):
        """Toast'ı kapat ve parent'ın listesinden kaldır."""
        parent = self.parent()
        if parent and hasattr(parent, '_toast_list'):
            if self in parent._toast_list:
                parent._toast_list.remove(self)
            # Kalan toast'ları yeniden pozisyonla
            if hasattr(parent, '_reposition_toasts'):
                parent._reposition_toasts()
        self.deleteLater()


class ToastManager:
    """Toast yöneticisi — parent widget üzerinde toast'ları konumlar."""

    @staticmethod
    def show_toast(parent, message, toast_type="info", duration=3000,
                   persistent=False, center=False):
        """Yeni bir toast göster."""
        if not hasattr(parent, '_toast_list'):
            parent._toast_list = []
            parent._reposition_toasts = lambda: ToastManager._reposition(parent)

        toast = ToastWidget(parent, message, toast_type, duration,
                            persistent, center)

        parent._toast_list.append(toast)
        ToastManager._reposition(parent)
        toast.show()
        toast.raise_()
        return toast

    @staticmethod
    def _reposition(parent):
        """Tüm toast'ları yeniden konumla."""
        if not hasattr(parent, '_toast_list'):
            return

        # Merkez toast'lar
        center_toasts = [t for t in parent._toast_list if t.center]
        corner_toasts = [t for t in parent._toast_list if not t.center]

        pw = parent.width()
        ph = parent.height()

        # Merkez toast'ları ortala
        center_y = ph // 3
        for toast in center_toasts:
            x = (pw - toast.width()) // 2
            toast.move(x, center_y)
            center_y += toast.height() + 8

        # Köşe toast'ları sağ alta yerleştir
        y_offset = ph - 60  # statusbar üstü
        for toast in reversed(corner_toasts):
            x = pw - toast.width() - 20
            y_offset -= toast.height() + 8
            toast.move(x, y_offset)
