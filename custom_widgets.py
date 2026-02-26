# -*- coding: utf-8 -*-
"""
custom_widgets.py — Özel QPainter tabanlı widget'lar
Navigation Map ve Obstacle/Cost Map canvas widget'ları.
Qt Designer'da QWidget olarak yerleştirilip "Promote" edilir.
"""

import math
import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPolygonF, QPainterPath
)


class NavigationMapWidget(QWidget):
    """
    Merkezi navigasyon haritası — waypoint'ler, araç konumu,
    izleme geçmişi (track history) ve rota çizer.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)

        # Veri
        self.vehicle_lat = 37.8043514
        self.vehicle_lon = -122.4101440
        self.vehicle_heading = 45.0
        self.waypoints = []          # list of (lat, lon)
        self.active_waypoint = 0
        self.track_history = []      # list of (lat, lon)
        self.mission_state = "STANDBY"

    # ── Veri güncelleme slotları ────────────────────────
    def set_vehicle_state(self, lat, lon, heading):
        self.vehicle_lat = lat
        self.vehicle_lon = lon
        self.vehicle_heading = heading
        self.update()

    def set_waypoints(self, waypoints, active_index=0):
        self.waypoints = waypoints
        self.active_waypoint = active_index
        self.update()

    def set_track_history(self, history):
        self.track_history = history
        self.update()

    def set_mission_state(self, state):
        self.mission_state = state
        self.update()

    # ── Koordinat dönüşümü ──────────────────────────────
    def _latlon_to_canvas(self, lat, lon):
        w = self.width()
        h = self.height()
        center_lat = self.vehicle_lat
        center_lon = self.vehicle_lon
        scale = 100000
        x = w / 2 + (lon - center_lon) * scale
        y = h / 2 - (lat - center_lat) * scale
        return x, y

    # ── Çizim ───────────────────────────────────────────
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()

        # Arka plan
        p.fillRect(0, 0, w, h, QColor("#0f172a"))

        # Grid
        p.setPen(QPen(QColor("#1e293b"), 1))
        for i in range(0, w, 40):
            p.drawLine(i, 0, i, h)
        for i in range(0, h, 40):
            p.drawLine(0, i, w, i)

        # Rota çizgisi (waypoint'ler arası)
        if len(self.waypoints) > 1:
            pen = QPen(QColor("#3b82f6"), 2, Qt.DashLine)
            p.setPen(pen)
            for i in range(len(self.waypoints) - 1):
                x1, y1 = self._latlon_to_canvas(*self.waypoints[i])
                x2, y2 = self._latlon_to_canvas(*self.waypoints[i + 1])
                p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Waypoint'ler
        mono = QFont("Consolas", 9, QFont.Bold)
        mono_small = QFont("Consolas", 7)
        for idx, (lat, lon) in enumerate(self.waypoints):
            x, y = self._latlon_to_canvas(lat, lon)
            is_active = (idx == self.active_waypoint)
            fill = QColor("#10b981") if is_active else QColor("#475569")
            border = QColor("#34d399") if is_active else QColor("#64748b")

            p.setPen(QPen(border, 2))
            p.setBrush(QBrush(fill))
            p.drawEllipse(QPointF(x, y), 10, 10)

            # Numara
            p.setPen(QColor("#ffffff"))
            p.setFont(mono)
            p.drawText(QRectF(x - 10, y - 8, 20, 16),
                       Qt.AlignCenter, str(idx + 1))

            # Koordinatlar
            p.setFont(mono_small)
            p.setPen(QColor("#94a3b8"))
            p.drawText(QRectF(x - 40, y + 14, 80, 14),
                       Qt.AlignCenter, f"{lat:.6f}")
            p.drawText(QRectF(x - 40, y + 26, 80, 14),
                       Qt.AlignCenter, f"{lon:.6f}")

        # Track history
        if len(self.track_history) > 1:
            pen = QPen(QColor(6, 182, 212, 150), 2)
            p.setPen(pen)
            for i in range(len(self.track_history) - 1):
                x1, y1 = self._latlon_to_canvas(*self.track_history[i])
                x2, y2 = self._latlon_to_canvas(*self.track_history[i + 1])
                p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Araç (vehicle)
        vx, vy = self._latlon_to_canvas(self.vehicle_lat, self.vehicle_lon)
        p.save()
        p.translate(vx, vy)
        p.rotate(self.vehicle_heading)

        # Ok şekli
        arrow = QPolygonF([
            QPointF(0, -15),
            QPointF(-8, 10),
            QPointF(0, 5),
            QPointF(8, 10),
        ])
        p.setPen(QPen(QColor("#fbbf24"), 2))
        p.setBrush(QBrush(QColor("#f59e0b")))
        p.drawPolygon(arrow)
        p.restore()

        # Araç çevresi
        p.setPen(QPen(QColor("#f59e0b"), 2))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(vx, vy), 20, 20)

        # Sol üst overlay — araç konumu
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(15, 23, 42, 220))
        p.drawRoundedRect(8, 8, 170, 72, 4, 4)

        p.setFont(QFont("Consolas", 8))
        p.setPen(QColor("#94a3b8"))
        p.drawText(14, 22, "Vehicle Position")
        p.setPen(QColor("#22d3ee"))
        p.drawText(14, 36, f"{self.vehicle_lat:.7f}°N")
        p.drawText(14, 50, f"{self.vehicle_lon:.7f}°W")
        p.setPen(QColor("#fbbf24"))
        p.drawText(14, 66, f"HDG: {self.vehicle_heading:.1f}°")

        # Sağ üst — mission state
        state_text = self.mission_state
        p.setFont(QFont("Consolas", 9, QFont.Bold))
        fm = p.fontMetrics()
        tw = fm.horizontalAdvance(state_text)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(15, 23, 42, 220))
        p.drawRoundedRect(w - tw - 24, 8, tw + 16, 24, 4, 4)
        p.setPen(QColor("#4ade80"))
        p.drawText(w - tw - 16, 24, state_text)

        p.end()


class ObstacleMapWidget(QWidget):
    """
    Engel / Maliyet Haritası — yerel sensör verilerini gösterir.
    2m, 5m, 10m menzil çemberleri ile.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(250, 250)

        self.vehicle_heading = 0.0
        self.obstacles = []  # list of (x, y, cost)

    def set_vehicle_heading(self, heading):
        self.vehicle_heading = heading
        self.update()

    def set_obstacles(self, obstacles):
        self.obstacles = obstacles
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        cx = w / 2
        cy = h / 2
        scale = min(w, h) / 22.0  # ~20 px/m, adaptive

        # Arka plan
        p.fillRect(0, 0, w, h, QColor("#0a0f1a"))

        # Grid
        p.setPen(QPen(QColor("#1e293b"), 1))
        for i in range(-10, 11):
            p.drawLine(int(cx + i * scale), 0, int(cx + i * scale), h)
            p.drawLine(0, int(cy + i * scale), w, int(cy + i * scale))

        # Merkez referans çizgileri
        pen = QPen(QColor("#334155"), 2, Qt.DashLine)
        p.setPen(pen)
        p.drawLine(int(cx), 0, int(cx), h)
        p.drawLine(0, int(cy), w, int(cy))

        # Engeller
        for ox, oy, cost in self.obstacles:
            sx = cx + ox * scale
            sy = cy - oy * scale
            cost = max(0.0, min(1.0, cost))
            if cost < 0.3:
                color = QColor(34, 197, 94, int((0.3 + cost) * 255))
            elif cost < 0.6:
                color = QColor(251, 191, 36, int((0.5 + cost * 0.5) * 255))
            else:
                color = QColor(239, 68, 68, int((0.6 + cost * 0.4) * 255))
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(color))
            p.drawEllipse(QPointF(sx, sy), 4, 4)

        # Araç
        p.save()
        p.translate(cx, cy)
        p.rotate(self.vehicle_heading)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor("#06b6d4")))
        p.drawRect(-8, -12, 16, 24)
        # Heading göstergesi
        tri = QPolygonF([QPointF(0, -15), QPointF(-6, -8), QPointF(6, -8)])
        p.setBrush(QBrush(QColor("#f59e0b")))
        p.drawPolygon(tri)
        p.restore()

        # Menzil çemberleri
        p.setBrush(Qt.NoBrush)
        for radius in [2, 5, 10]:
            p.setPen(QPen(QColor("#1e293b"), 1))
            r = radius * scale
            p.drawEllipse(QPointF(cx, cy), r, r)
            p.setPen(QColor("#475569"))
            p.setFont(QFont("Consolas", 8))
            p.drawText(int(cx + r + 3), int(cy + 4), f"{radius}m")

        # Legend
        p.setFont(QFont("Consolas", 9))
        p.setPen(QColor("#cbd5e1"))
        p.drawText(10, 18, "Cost Map")

        legend_items = [
            (QColor("#22c55e"), "Low"),
            (QColor("#fbbf24"), "Medium"),
            (QColor("#ef4444"), "High"),
        ]
        for i, (color, label) in enumerate(legend_items):
            y = 30 + i * 18
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(color))
            p.drawRect(10, y, 12, 12)
            p.setPen(QColor("#94a3b8"))
            p.drawText(26, y + 10, label)

        p.end()
