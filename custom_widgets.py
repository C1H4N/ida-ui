# -*- coding: utf-8 -*-
"""
custom_widgets.py — Premium QPainter Widget'ları
Navigation Map ve Obstacle/Cost Map — tamamen yenilenmiş tasarım.
"""

import math
import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPolygonF, QPainterPath,
    QRadialGradient, QLinearGradient, QConicalGradient
)


class NavigationMapWidget(QWidget):
    """
    Premium navigasyon haritası — neon glow waypoint'ler, araç konumu,
    izleme geçmişi ve rota çizer. Glassmorphism overlay'ler.
    Tüm waypoint'ler + araç merkezli auto-fit görünüm.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)

        self.vehicle_lat = 37.8043514
        self.vehicle_lon = -122.4101440
        self.vehicle_heading = 45.0
        self.waypoints = []
        self.active_waypoint = 0
        self.track_history = []
        self.mission_state = "STANDBY"

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

    def _compute_view(self):
        """Sadece waypoint'lere göre viewport hesapla — araç konumunu dahil ETME.
        Böylece waypoint'ler sabit kalır ve araç gerçek hareketi görünür."""
        if len(self.waypoints) > 0:
            all_points = list(self.waypoints)
        else:
            # Waypoint yoksa araç konumunu fallback olarak kullan
            all_points = [(self.vehicle_lat, self.vehicle_lon)]

        lats = [p[0] for p in all_points]
        lons = [p[1] for p in all_points]

        center_lat = (min(lats) + max(lats)) / 2
        center_lon = (min(lons) + max(lons)) / 2

        lat_range = max(lats) - min(lats)
        lon_range = max(lons) - min(lons)

        # Minimum range to prevent extreme zoom
        lat_range = max(lat_range, 0.0002)
        lon_range = max(lon_range, 0.0002)

        w = self.width()
        h = self.height()

        # 15% padding on each side
        usable_w = w * 0.70
        usable_h = h * 0.70

        scale_x = usable_w / lon_range if lon_range > 0 else 100000
        scale_y = usable_h / lat_range if lat_range > 0 else 100000
        scale = min(scale_x, scale_y)

        return center_lat, center_lon, scale

    def _latlon_to_canvas(self, lat, lon):
        center_lat, center_lon, scale = self._view_params
        w = self.width()
        h = self.height()
        x = w / 2 + (lon - center_lon) * scale
        y = h / 2 - (lat - center_lat) * scale
        return x, y

    def paintEvent(self, event):
        # Pre-compute view parameters for this frame
        self._view_params = self._compute_view()

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        w = self.width()
        h = self.height()

        # ── Deep space background with radial gradient ──
        bg_gradient = QRadialGradient(w / 2, h / 2, max(w, h) * 0.7)
        bg_gradient.setColorAt(0, QColor("#111b33"))
        bg_gradient.setColorAt(0.6, QColor("#0c1224"))
        bg_gradient.setColorAt(1, QColor("#080e1e"))
        p.fillRect(0, 0, w, h, QBrush(bg_gradient))

        # ── Subtle dot grid ──
        p.setPen(QPen(QColor(99, 102, 241, 20), 1))
        for i in range(0, w, 50):
            for j in range(0, h, 50):
                p.drawEllipse(QPointF(i, j), 1.5, 1.5)

        # ── Rota çizgisi (neon glow) ──
        if len(self.waypoints) > 1:
            # Glow layer
            pen_glow = QPen(QColor(99, 102, 241, 40), 8)
            pen_glow.setCapStyle(Qt.RoundCap)
            p.setPen(pen_glow)
            for i in range(len(self.waypoints) - 1):
                x1, y1 = self._latlon_to_canvas(*self.waypoints[i])
                x2, y2 = self._latlon_to_canvas(*self.waypoints[i + 1])
                p.drawLine(int(x1), int(y1), int(x2), int(y2))

            # Core line
            pen = QPen(QColor(129, 140, 248, 180), 2, Qt.DashLine)
            pen.setDashPattern([8, 4])
            p.setPen(pen)
            for i in range(len(self.waypoints) - 1):
                x1, y1 = self._latlon_to_canvas(*self.waypoints[i])
                x2, y2 = self._latlon_to_canvas(*self.waypoints[i + 1])
                p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # ── Waypoint'ler — neon glow circles ──
        font_wp = QFont("Segoe UI", 13, QFont.Bold)
        font_coord = QFont("JetBrains Mono", 9)
        for idx, (lat, lon) in enumerate(self.waypoints):
            x, y = self._latlon_to_canvas(lat, lon)
            is_active = (idx == self.active_waypoint)

            # Glow aura
            if is_active:
                glow = QRadialGradient(x, y, 32)
                glow.setColorAt(0, QColor(52, 211, 153, 100))
                glow.setColorAt(0.5, QColor(52, 211, 153, 30))
                glow.setColorAt(1, QColor(52, 211, 153, 0))
                p.setPen(Qt.NoPen)
                p.setBrush(QBrush(glow))
                p.drawEllipse(QPointF(x, y), 32, 32)

            # Outer ring
            fill = QColor("#10b981") if is_active else QColor(99, 102, 241, 120)
            border = QColor("#6ee7b7") if is_active else QColor("#818cf8")

            p.setPen(QPen(border, 2.5))
            p.setBrush(QBrush(fill))
            p.drawEllipse(QPointF(x, y), 16, 16)

            # Numara
            p.setPen(QColor("#ffffff"))
            p.setFont(font_wp)
            p.drawText(QRectF(x - 14, y - 12, 28, 24),
                       Qt.AlignCenter, str(idx + 1))

            # Koordinatlar
            p.setFont(font_coord)
            p.setPen(QColor(165, 180, 252, 200))
            p.drawText(QRectF(x - 55, y + 20, 110, 16),
                       Qt.AlignCenter, f"{lat:.6f}")
            p.drawText(QRectF(x - 55, y + 34, 110, 16),
                       Qt.AlignCenter, f"{lon:.6f}")

        # ── Track history — gradient trail ──
        if len(self.track_history) > 1:
            total = len(self.track_history)
            for i in range(total - 1):
                alpha = int(40 + (i / total) * 180)
                pen = QPen(QColor(99, 102, 241, alpha), 2.5)
                pen.setCapStyle(Qt.RoundCap)
                p.setPen(pen)
                x1, y1 = self._latlon_to_canvas(*self.track_history[i])
                x2, y2 = self._latlon_to_canvas(*self.track_history[i + 1])
                p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # ── Araç — premium design ──
        vx, vy = self._latlon_to_canvas(self.vehicle_lat, self.vehicle_lon)

        # Outer glow ring
        glow = QRadialGradient(vx, vy, 35)
        glow.setColorAt(0, QColor(245, 158, 11, 60))
        glow.setColorAt(0.6, QColor(245, 158, 11, 15))
        glow.setColorAt(1, QColor(245, 158, 11, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(glow))
        p.drawEllipse(QPointF(vx, vy), 35, 35)

        # Pulsing range circle
        p.setPen(QPen(QColor(245, 158, 11, 40), 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(vx, vy), 26, 26)

        p.save()
        p.translate(vx, vy)
        p.rotate(self.vehicle_heading)

        # Arrow shape — sleek design
        arrow = QPolygonF([
            QPointF(0, -18),
            QPointF(-9, 12),
            QPointF(0, 6),
            QPointF(9, 12),
        ])

        # Arrow gradient
        arrow_grad = QLinearGradient(0, -18, 0, 12)
        arrow_grad.setColorAt(0, QColor("#fbbf24"))
        arrow_grad.setColorAt(1, QColor("#f59e0b"))
        p.setPen(QPen(QColor("#fde68a"), 2))
        p.setBrush(QBrush(arrow_grad))
        p.drawPolygon(arrow)
        p.restore()

        # ── Glassmorphism Overlay — Vehicle Position ──
        overlay_w, overlay_h = 220, 96
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(8, 12, 24, 210))
        p.drawRoundedRect(10, 10, overlay_w, overlay_h, 12, 12)
        # Border
        p.setPen(QPen(QColor(99, 102, 241, 50), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(10, 10, overlay_w, overlay_h, 12, 12)

        p.setFont(QFont("Segoe UI", 11, QFont.Bold))
        p.setPen(QColor(165, 180, 252, 180))
        p.drawText(18, 30, "ARAÇ KONUMU")

        p.setFont(QFont("JetBrains Mono", 12, QFont.Bold))
        p.setPen(QColor("#6ee7b7"))
        p.drawText(18, 52, f"{self.vehicle_lat:.7f}°N")
        p.drawText(18, 72, f"{self.vehicle_lon:.7f}°W")
        p.setPen(QColor("#fbbf24"))
        p.drawText(18, 92, f"YÖN: {self.vehicle_heading:.1f}°")

        # ── Glassmorphism Overlay — Mission State (sağ üst) ──
        state_text = self.mission_state
        p.setFont(QFont("Segoe UI", 13, QFont.Bold))
        fm = p.fontMetrics()
        tw = fm.horizontalAdvance(state_text)
        box_w = tw + 28
        box_h = 36
        box_x = w - box_w - 10
        box_y = 10

        p.setPen(Qt.NoPen)
        p.setBrush(QColor(8, 12, 24, 210))
        p.drawRoundedRect(box_x, box_y, box_w, box_h, 10, 10)
        p.setPen(QPen(QColor(99, 102, 241, 50), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(box_x, box_y, box_w, box_h, 10, 10)

        # State text color based on state
        if "COMPLETE" in state_text:
            state_color = QColor("#6ee7b7")
        elif "E-STOP" in state_text or "FAILSAFE" in state_text:
            state_color = QColor("#fca5a5")
        elif state_text == "STANDBY":
            state_color = QColor("#a5b4fc")
        else:
            state_color = QColor("#67e8f9")

        p.setPen(state_color)
        p.drawText(box_x + 14, box_y + 24, state_text)

        p.end()


class ObstacleMapWidget(QWidget):
    """
    Premium Engel / Maliyet Haritası — neon glow engeller,
    radar sweep efekti ve menzil çemberleri.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(280, 280)

        self.vehicle_heading = 0.0
        self.obstacles = []

    def set_vehicle_heading(self, heading):
        self.vehicle_heading = heading
        self.update()

    def set_obstacles(self, obstacles):
        self.obstacles = obstacles
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        w = self.width()
        h = self.height()
        cx = w / 2
        cy = h / 2
        scale = min(w, h) / 22.0

        # ── Deep space background ──
        bg = QRadialGradient(cx, cy, max(w, h) * 0.6)
        bg.setColorAt(0, QColor("#0f172a"))
        bg.setColorAt(0.5, QColor("#0a0f1e"))
        bg.setColorAt(1, QColor("#050810"))
        p.fillRect(0, 0, w, h, QBrush(bg))

        # ── Subtle radial grid lines ──
        p.setPen(QPen(QColor(99, 102, 241, 12), 1))
        for i in range(-10, 11):
            p.drawLine(int(cx + i * scale), 0, int(cx + i * scale), h)
            p.drawLine(0, int(cy + i * scale), w, int(cy + i * scale))

        # ── Cross hairs ──
        pen = QPen(QColor(99, 102, 241, 30), 1.5, Qt.DashLine)
        pen.setDashPattern([6, 4])
        p.setPen(pen)
        p.drawLine(int(cx), 0, int(cx), h)
        p.drawLine(0, int(cy), w, int(cy))

        # ── Menzil çemberleri — neon glow ──
        p.setBrush(Qt.NoBrush)
        for radius in [2, 5, 10]:
            r = radius * scale
            # Glow
            p.setPen(QPen(QColor(99, 102, 241, 15), 4))
            p.drawEllipse(QPointF(cx, cy), r, r)
            # Core
            p.setPen(QPen(QColor(99, 102, 241, 40), 1))
            p.drawEllipse(QPointF(cx, cy), r, r)
            # Label
            p.setPen(QColor(129, 140, 248, 160))
            p.setFont(QFont("Segoe UI", 11, QFont.Bold))
            p.drawText(int(cx + r + 5), int(cy - 3), f"{radius}m")

        # ── Engeller — neon dots ──
        for ox, oy, cost in self.obstacles:
            sx = cx + ox * scale
            sy = cy - oy * scale
            cost = max(0.0, min(1.0, cost))

            if cost < 0.3:
                base_color = QColor(52, 211, 153)
                alpha = int(80 + cost * 400)
            elif cost < 0.6:
                base_color = QColor(251, 191, 36)
                alpha = int(100 + cost * 250)
            else:
                base_color = QColor(248, 113, 113)
                alpha = int(150 + cost * 105)

            # Glow
            glow = QRadialGradient(sx, sy, 8)
            glow_color = QColor(base_color)
            glow_color.setAlpha(int(alpha * 0.3))
            glow.setColorAt(0, glow_color)
            glow_color2 = QColor(base_color)
            glow_color2.setAlpha(0)
            glow.setColorAt(1, glow_color2)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(glow))
            p.drawEllipse(QPointF(sx, sy), 8, 8)

            # Core dot
            core = QColor(base_color)
            core.setAlpha(alpha)
            p.setBrush(QBrush(core))
            p.drawEllipse(QPointF(sx, sy), 3.5, 3.5)

        # ── Araç — premium design ──
        p.save()
        p.translate(cx, cy)
        p.rotate(self.vehicle_heading)

        # Body glow
        body_glow = QRadialGradient(0, 0, 20)
        body_glow.setColorAt(0, QColor(99, 102, 241, 50))
        body_glow.setColorAt(1, QColor(99, 102, 241, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(body_glow))
        p.drawEllipse(QPointF(0, 0), 20, 20)

        # Body
        body_grad = QLinearGradient(0, -14, 0, 14)
        body_grad.setColorAt(0, QColor("#6366f1"))
        body_grad.setColorAt(1, QColor("#4f46e5"))
        p.setBrush(QBrush(body_grad))
        p.setPen(QPen(QColor("#818cf8"), 1.5))
        p.drawRoundedRect(-9, -14, 18, 28, 4, 4)

        # Heading triangle
        tri = QPolygonF([QPointF(0, -18), QPointF(-7, -10), QPointF(7, -10)])
        tri_grad = QLinearGradient(0, -18, 0, -10)
        tri_grad.setColorAt(0, QColor("#fbbf24"))
        tri_grad.setColorAt(1, QColor("#f59e0b"))
        p.setBrush(QBrush(tri_grad))
        p.setPen(QPen(QColor("#fde68a"), 1))
        p.drawPolygon(tri)
        p.restore()

        # ── Glassmorphism Legend ──
        legend_w, legend_h = 120, 100
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(8, 12, 24, 200))
        p.drawRoundedRect(10, 10, legend_w, legend_h, 10, 10)
        p.setPen(QPen(QColor(99, 102, 241, 40), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(10, 10, legend_w, legend_h, 10, 10)

        p.setFont(QFont("Segoe UI", 12, QFont.Bold))
        p.setPen(QColor("#c7d2fe"))
        p.drawText(18, 30, "Maliyet Haritası")

        legend_items = [
            (QColor("#34d399"), "Düşük"),
            (QColor("#fbbf24"), "Orta"),
            (QColor("#f87171"), "Yüksek"),
        ]
        for i, (color, label) in enumerate(legend_items):
            y = 40 + i * 20
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(color))
            p.drawRoundedRect(18, y, 16, 16, 3, 3)
            p.setPen(QColor(165, 180, 252, 160))
            p.setFont(QFont("Segoe UI", 11))
            p.drawText(40, y + 13, label)

        p.end()
