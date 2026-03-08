# -*- coding: utf-8 -*-
"""
main.py — USV Ground Control Station
Teknofest — PyQt5 + pyqtgraph

Çalıştırmak için:
    pip install PyQt5 pyqtgraph numpy
    python main.py
"""

import sys
import os
import math
import random
import time
import csv
import re
from datetime import datetime, timezone

import numpy as np

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QVBoxLayout, QFileDialog
)

# pyqtgraph grafik kütüphanesi
import pyqtgraph as pg

# UI ve özel widget'lar
from ui_mainwindow import Ui_MainWindow
from custom_widgets import NavigationMapWidget, ObstacleMapWidget
from toast_widget import ToastManager


# ═══════════════════════════════════════════════════════════
# pyqtgraph Genel Ayarlar (koyu tema uyumlu)
# ═══════════════════════════════════════════════════════════
pg.setConfigOptions(antialias=True, background="#0c1224", foreground="#a5b4fc")


class GCSMainWindow(QMainWindow):
    """USV Ground Control Station ana penceresi."""

    def __init__(self):
        super().__init__()

        # ── UI Kurulumu (pyuic5 çıktısı gibi) ──────────
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # ── Stylesheet Yükle ────────────────────────────
        qss_path = os.path.join(os.path.dirname(__file__), "dark_theme.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

        # ── Grafikleri Oluştur (pyqtgraph) ──────────────
        self._init_graphs()

        # ── State Değişkenleri ──────────────────────────
        self.mission_started = False
        self.is_powered = True
        self.active_waypoint = 0
        self.mission_state = "BEKLEMEDE"
        self.competition_time = 20 * 60  # 20 dakika (saniye)
        self.failsafe_active = False
        self.no_data_counter = 0
        self.csv_file = None
        self.csv_writer = None

        # Waypoint varsayılanları
        default_wp = [
            ("37.8043514", "-122.4101440"),
            ("37.8045123", "-122.4098234"),
            ("37.8047890", "-122.4095678"),
            ("37.8049234", "-122.4093456"),
        ]
        for i, (lat, lon) in enumerate(default_wp):
            self.ui.wp_entries[i][0].setText(lat)
            self.ui.wp_entries[i][1].setText(lon)

        # Araç durumu
        self.vehicle = {
            "lat": 37.8043514,
            "lon": -122.4101440,
            "heading": 45.0,
            "ground_speed": 0.0,
            "roll": 0.0,
            "pitch": 0.0,
            "speed_setpoint": 1.5,
            "heading_setpoint": 90.0,
            "thruster_left": 0.0,
            "thruster_right": 0.0,
            "battery_voltage": 12.4,
            "battery_pct": 78,
            "cpu_temp": 62,
            "gps_fix": "RTK Fixed",
            "hdop": 0.8,
            "telem_link": 98,
            "rc_link": "Bağlı",
            "rssi": -65,
            "packet_loss": 0.3,
            "mode": "MANUEL",
            "power_cut": False,
        }

        self.track_history = []
        self.graph_data = {
            "time": [],
            "speed": [],
            "speed_target": [],
            "heading": [],
            "heading_target": [],
            "thruster_left": [],
            "thruster_right": [],
        }
        self.graph_tick = 0

        # ── Sinyaller Bağla ─────────────────────────────
        self._connect_signals()

        # ── Timers ──────────────────────────────────────
        # Ana simülasyon döngüsü (500ms)
        self.sim_timer = QTimer(self)
        self.sim_timer.timeout.connect(self._simulation_tick)
        self.sim_timer.start(500)

        # Saat & timer (1s)
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._clock_tick)
        self.clock_timer.start(1000)

        # Engel haritası güncelleme (5s)
        self.obstacle_timer = QTimer(self)
        self.obstacle_timer.timeout.connect(self._generate_obstacles)
        self.obstacle_timer.start(5000)
        self._generate_obstacles()  # İlk oluştur

        # ── İlk UI Güncellemesi ─────────────────────────
        self._update_telemetry_display()
        self._update_map()
        self._update_mission_state_display()

        # ── Konsol log sistemi ──────────────────────────
        self._log_to_console("Sistem başlatıldı — Waypoint'leri girin ve görevi yükleyin")

        self.statusBar().showMessage("Sistem hazır — Waypoint'leri girin ve görevi yükleyin")

    # ═══════════════════════════════════════════════════════
    # GRAFİK İNİTALİZASYON (pyqtgraph)
    # ═══════════════════════════════════════════════════════
    def _init_graphs(self):
        """pyqtgraph PlotWidget'larını oluşturur ve placeholder'ların yerine koyar."""

        # Speed Graph
        self.plot_speed = pg.PlotWidget()
        self.plot_speed.setLabel("left", "m/s", **{"font-size": "12pt", "color": "#a5b4fc"})
        self.plot_speed.setLabel("bottom", "t", **{"font-size": "12pt", "color": "#a5b4fc"})
        self.plot_speed.setYRange(0, 3)
        self.plot_speed.showGrid(x=True, y=True, alpha=0.08)
        self.plot_speed.addLegend(offset=(5, 5), labelTextSize="12pt")
        self.plot_speed.getAxis("left").setPen(pg.mkPen("#6366f1", width=1))
        self.plot_speed.getAxis("bottom").setPen(pg.mkPen("#6366f1", width=1))
        self.curve_speed = self.plot_speed.plot(
            pen=pg.mkPen("#818cf8", width=2.5), name="Hız"
        )
        self.curve_speed_target = self.plot_speed.plot(
            pen=pg.mkPen("#34d399", width=2.5, style=Qt.DashLine), name="Hedef"
        )
        self._replace_placeholder(
            self.ui.frame_graph_speed, self.ui.graph_speed_placeholder, self.plot_speed
        )

        # Heading Graph
        self.plot_heading = pg.PlotWidget()
        self.plot_heading.setLabel("left", "°", **{"font-size": "12pt", "color": "#a5b4fc"})
        self.plot_heading.setLabel("bottom", "t", **{"font-size": "12pt", "color": "#a5b4fc"})
        self.plot_heading.setYRange(0, 360)
        self.plot_heading.showGrid(x=True, y=True, alpha=0.08)
        self.plot_heading.addLegend(offset=(5, 5), labelTextSize="12pt")
        self.plot_heading.getAxis("left").setPen(pg.mkPen("#6366f1", width=1))
        self.plot_heading.getAxis("bottom").setPen(pg.mkPen("#6366f1", width=1))
        self.curve_heading = self.plot_heading.plot(
            pen=pg.mkPen("#fbbf24", width=2.5), name="Yön"
        )
        self.curve_heading_target = self.plot_heading.plot(
            pen=pg.mkPen("#34d399", width=2.5, style=Qt.DashLine), name="Hedef"
        )
        self._replace_placeholder(
            self.ui.frame_graph_heading, self.ui.graph_heading_placeholder, self.plot_heading
        )

        # Thruster Graph
        self.plot_thruster = pg.PlotWidget()
        self.plot_thruster.setLabel("left", "%", **{"font-size": "12pt", "color": "#a5b4fc"})
        self.plot_thruster.setLabel("bottom", "t", **{"font-size": "12pt", "color": "#a5b4fc"})
        self.plot_thruster.setYRange(-100, 100)
        self.plot_thruster.showGrid(x=True, y=True, alpha=0.08)
        self.plot_thruster.addLegend(offset=(5, 5), labelTextSize="12pt")
        self.plot_thruster.getAxis("left").setPen(pg.mkPen("#6366f1", width=1))
        self.plot_thruster.getAxis("bottom").setPen(pg.mkPen("#6366f1", width=1))
        self.curve_thruster_l = self.plot_thruster.plot(
            pen=pg.mkPen("#a78bfa", width=2.5), name="Sol"
        )
        self.curve_thruster_r = self.plot_thruster.plot(
            pen=pg.mkPen("#f472b6", width=2.5), name="Sağ"
        )
        self._replace_placeholder(
            self.ui.frame_graph_thruster, self.ui.graph_thruster_placeholder, self.plot_thruster
        )

    @staticmethod
    def _replace_placeholder(parent_frame, placeholder, new_widget):
        """Placeholder widget'ı gerçek pyqtgraph widget ile değiştirir."""
        layout = parent_frame.layout()
        idx = layout.indexOf(placeholder)
        if idx >= 0:
            layout.removeWidget(placeholder)
            placeholder.deleteLater()
        layout.insertWidget(max(idx, 1), new_widget, 1)

    def _reattach_graphs(self):
        """Layout değişikliği sonrası grafikleri yeniden yerleştir."""
        for frame, plot_widget in [
            (self.ui.frame_graph_speed, self.plot_speed),
            (self.ui.frame_graph_heading, self.plot_heading),
            (self.ui.frame_graph_thruster, self.plot_thruster),
        ]:
            layout = frame.layout()
            if layout.indexOf(plot_widget) < 0:
                layout.addWidget(plot_widget, 1)
                plot_widget.show()

    # ═══════════════════════════════════════════════════════
    # SİNYAL BAĞLANTILARI
    # ═══════════════════════════════════════════════════════
    def _connect_signals(self):
        self.ui.btn_start_mission.clicked.connect(self._on_start_mission)
        self.ui.btn_upload_mission.clicked.connect(self._on_upload_mission)
        self.ui.btn_import_wp.clicked.connect(self._on_import_wp)
        self.ui.btn_clear_waypoints.clicked.connect(self._on_clear_waypoints)
        self.ui.btn_estop.clicked.connect(self._on_emergency_stop)
        self.ui.btn_mode_switch.clicked.connect(self._on_mode_switch)

        # Video layout toggle
        self.ui.btn_single_screen.clicked.connect(
            lambda: self._set_video_layout("single")
        )
        self.ui.btn_3screen.clicked.connect(
            lambda: self._set_video_layout("split-3")
        )

        # Console toggle
        self.ui.btn_console_toggle.toggled.connect(self._on_console_toggle)
        self.ui.btn_clear_console.clicked.connect(self._on_clear_console)

        # Waypoint değişince haritayı güncelle
        for edit_lat, edit_lon in self.ui.wp_entries:
            edit_lat.textChanged.connect(self._on_wp_changed)
            edit_lon.textChanged.connect(self._on_wp_changed)

    # ═══════════════════════════════════════════════════════
    # KONSOL / LOG SİSTEMİ
    # ═══════════════════════════════════════════════════════
    def _log_to_console(self, message, level="INFO"):
        """Konsol paneline log mesajı ekler."""
        ts = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "INFO": "#67e8f9",
            "WARN": "#fbbf24",
            "ERROR": "#f87171",
            "SUCCESS": "#4ade80",
        }
        color = color_map.get(level, "#a5b4fc")
        html = f'<span style="color: #475569;">[{ts}]</span> <span style="color: {color}; font-weight: bold;">[{level}]</span> <span style="color: #e0e7ff;">{message}</span>'
        self.ui.console_text.append(html)
        # Auto-scroll to bottom
        scrollbar = self.ui.console_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_console_toggle(self, checked):
        """Konsol panelini aç/kapa."""
        if checked:
            self.ui.frame_console.show()
            self.ui.btn_console_toggle.setText("🖥  Konsol ▼")
        else:
            self.ui.frame_console.hide()
            self.ui.btn_console_toggle.setText("🖥  Konsol ▲")

    def _on_clear_console(self):
        """Konsol içeriğini temizle."""
        self.ui.console_text.clear()
        self._log_to_console("Konsol temizlendi", "INFO")

    # ═══════════════════════════════════════════════════════
    # BUTON İŞLEYİCİLER (SLOT'lar)
    # ═══════════════════════════════════════════════════════
    def _on_wp_changed(self):
        """Waypoint değiştiğinde haritayı güncelle."""
        if not self.mission_started:
            self._update_map()

    def _on_start_mission(self):
        if self.mission_started:
            return
            
        if not self.ui.check_wifi.isChecked() or not self.ui.check_race_mode.isChecked():
            ToastManager.show_toast(self, "Sefer öncesi kontrol panelindeki tüm onayları verin!", "warning", 4000)
            self._log_to_console("Görev başlatılamadı: Sefer öncesi kontrol eksik", "WARN")
            return
            
        wp = self._get_waypoints()
        if not wp:
            ToastManager.show_toast(self, "Geçerli waypoint yüklenmedi!\nFormat: 37.8043514", "error", 5000)
            self._log_to_console("Görev başlatılamadı: Geçerli waypoint bulunamadı", "ERROR")
            return

        # Araç başlangıç konumunu ilk waypoint'e ayarla
        self.vehicle["lat"] = wp[0][0]
        self.vehicle["lon"] = wp[0][1]

        self.mission_started = True
        self.vehicle["mode"] = "GÖREV"
        # Araç WP1'de başlıyor, hedef WP2 olacak
        if len(wp) > 1:
            self.active_waypoint = 1
            self.mission_state = "WP1 → WP2"
        else:
            self.active_waypoint = 0
            self.mission_state = "WP1'e gidiliyor"
        self._update_mission_state_display()
        self._update_mission_progress()
        self._set_mission_lock(True)
        self.ui.btn_start_mission.setEnabled(False)
        self._start_csv_logging()
        ToastManager.show_toast(self, f"Görev başlatıldı — {len(wp)} waypoint yüklendi", "success", 3000)
        self._log_to_console(f"Görev başlatıldı — {len(wp)} waypoint yüklendi", "SUCCESS")
        self._log_to_console(f"Araç konumu WP1'e taşındı: ({wp[0][0]:.7f}, {wp[0][1]:.7f})", "INFO")
        self.statusBar().showMessage("✓ Görev başlatıldı — Araç otonom çalışıyor")

    def _on_import_wp(self):
        if self.mission_started:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Görev Dosyası Seç", "", "Text/CSV Dosyaları (*.txt *.csv);;Tüm Dosyalar (*)"
        )
        if not file_path:
            return
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            idx = 0
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Virgül, sekme veya boşlukla ayrılmış
                parts = re.split(r'[;,\t\s]+', line)
                if len(parts) >= 2 and idx < len(self.ui.wp_entries):
                    self.ui.wp_entries[idx][0].setText(parts[0].strip())
                    self.ui.wp_entries[idx][1].setText(parts[1].strip())
                    idx += 1
            
            self._log_to_console(f"Dosyadan {idx} waypoint okundu: {os.path.basename(file_path)}", "SUCCESS")
            self.statusBar().showMessage(f"✓ Dosyadan {idx} waypoint okundu")
            if idx == 0:
                ToastManager.show_toast(self, "Dosyadan geçerli koordinat okunamadı", "warning", 4000)
                self._log_to_console("Dosyada geçerli koordinat bulunamadı", "WARN")
        except Exception as e:
            ToastManager.show_toast(self, f"Dosya okuma hatası: {e}", "error", 5000)
            self._log_to_console(f"Dosya okuma hatası: {e}", "ERROR")

    def _on_upload_mission(self):
        if self.mission_started:
            return
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        wp = self._get_waypoints()
        self.ui.lbl_upload_status.setText(f"✓ {ts} UTC'de yüklendi ({len(wp)} WP)")
        self.ui.lbl_upload_status.show()
        ToastManager.show_toast(self, f"Görev yüklendi — {len(wp)} waypoint", "success", 3000)
        self._log_to_console(f"Görev yüklendi — {len(wp)} waypoint, {ts} UTC", "SUCCESS")
        self.statusBar().showMessage("✓ Görev waypoint'leri başarıyla yüklendi")

    def _on_clear_waypoints(self):
        if self.mission_started:
            return
        for edit_lat, edit_lon in self.ui.wp_entries:
            edit_lat.clear()
            edit_lon.clear()
        self.ui.lbl_upload_status.hide()
        self._log_to_console("Waypoint'ler temizlendi", "INFO")
        self.statusBar().showMessage("Waypoint'ler temizlendi")

    def _on_emergency_stop(self):
        self.mission_started = False
        self.is_powered = False
        self.vehicle["mode"] = "GÜVENLİK"
        self.vehicle["power_cut"] = True
        self.vehicle["ground_speed"] = 0
        self.vehicle["thruster_left"] = 0
        self.vehicle["thruster_right"] = 0
        self.mission_state = "ACİL DURDURMA AKTİF"
        self._update_mission_state_display()
        self.ui.frame_power_cut.show()
        self.ui.lbl_power_status.setText("● GÜÇ KESİMİ")
        self.ui.lbl_power_status.setStyleSheet("color: #ef4444; padding: 0 8px;")
        self.ui.btn_start_mission.setEnabled(False)
        self._log_to_console("ACİL DURDURMA aktif edildi — Güç kesildi!", "ERROR")
        self.statusBar().showMessage("⚠ ACİL DURDURMA AKTİF — Güç kesildi!")
        ToastManager.show_toast(
            self, "ACİL DURDURMA AKTİF!\nAraç güç kesimi durumunda.",
            "error", persistent=True, center=True
        )

    def _on_mode_switch(self):
        """Manuel ↔ Otonom mod geçişi."""
        current = self.vehicle["mode"]
        if current == "MANUEL":
            new_mode = "GÖREV"
            msg = "Otonom moda geçilsin mi?\nAraç waypoint rotasını izleyecek."
        else:
            new_mode = "MANUEL"
            msg = "Manuel moda geçilsin mi?\nAraç kontrolü operatöre geçecek."

        reply = QMessageBox.question(
            self, f"{new_mode} Moduna Geç",
            msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.vehicle["mode"] = new_mode
            self._update_telemetry_display()
            if new_mode == "GÖREV":
                self.ui.btn_mode_switch.setText("⇄  Manuel Moda Geç")
                self.ui.btn_mode_switch.setStyleSheet(
                    "background-color: #1e3a5f; color: #60a5fa;"
                )
            else:
                self.ui.btn_mode_switch.setText("⇄  Otonom Moda Geç")
                self.ui.btn_mode_switch.setStyleSheet(
                    "background-color: #1a2e1a; color: #4ade80;"
                )
            self._log_to_console(f"Mod değiştirildi: {new_mode}", "SUCCESS")
            self.statusBar().showMessage(f"✓ Mod değiştirildi: {new_mode}")

    def _set_video_layout(self, layout):
        self.ui.btn_single_screen.setChecked(layout == "single")
        self.ui.btn_3screen.setChecked(layout == "split-3")

        if layout == "single":
            self.ui.apply_single_layout()
        else:
            self.ui.apply_3screen_layout()

        # Grafikleri yeniden bağla (re-parent sonrası gerekli)
        self._reattach_graphs()

    def _set_mission_lock(self, locked):
        """Görev başlayınca giriş alanlarını kilitle."""
        for edit_lat, edit_lon in self.ui.wp_entries:
            edit_lat.setEnabled(not locked)
            edit_lon.setEnabled(not locked)
        self.ui.combo_target_color.setEnabled(not locked)
        self.ui.btn_upload_mission.setEnabled(not locked)
        self.ui.btn_clear_waypoints.setEnabled(not locked)
        self.ui.btn_import_wp.setEnabled(not locked)
        self.ui.combo_frequency.setEnabled(not locked)
        self.ui.check_wifi.setEnabled(not locked)
        self.ui.check_race_mode.setEnabled(not locked)
        self.ui.btn_mode_switch.setEnabled(not locked)

    # ═══════════════════════════════════════════════════════
    # SİMÜLASYON DÖNGÜSÜ (500ms)
    # ═══════════════════════════════════════════════════════
    def _simulation_tick(self):
        if not self.mission_started or not self.is_powered:
            return

        # Görev tamamlandıysa simülasyonu durdur
        if self.mission_state == "GÖREV TAMAMLANDI":
            return

        # Waypoint'leri oku
        waypoints = self._get_waypoints()
        if not waypoints or self.active_waypoint >= len(waypoints):
            return

        target_lat, target_lon = waypoints[self.active_waypoint]
        v = self.vehicle

        delta_lat = target_lat - v["lat"]
        delta_lon = target_lon - v["lon"]
        distance = math.sqrt(delta_lat ** 2 + delta_lon ** 2)

        target_heading = math.degrees(math.atan2(delta_lon, delta_lat)) % 360

        speed = 0.00002
        if distance > 0.00005:
            v["lat"] += (delta_lat / distance) * speed
            v["lon"] += (delta_lon / distance) * speed
        else:
            # Waypoint'e ulaşıldı
            if self.active_waypoint < len(waypoints) - 1:
                old_wp = self.active_waypoint + 1
                self.active_waypoint += 1
                new_wp = self.active_waypoint + 1
                self.mission_state = f"WP{old_wp} → WP{new_wp}"
                self._log_to_console(f"Waypoint {old_wp} ulaşıldı → WP{new_wp}'e yönleniyor", "SUCCESS")
                ToastManager.show_toast(self, f"Waypoint {old_wp}'e ulaşıldı → WP{new_wp}", "info", 2500)
            else:
                self.mission_state = "GÖREV TAMAMLANDI"
                v["ground_speed"] = 0.0
                v["thruster_left"] = 0.0
                v["thruster_right"] = 0.0
                self._update_telemetry_display()
                self._update_mission_progress()
                self._log_to_console("Görev tamamlandı! Tüm waypoint'lere ulaşıldı.", "SUCCESS")
                ToastManager.show_toast(self, "Görev tamamlandı! Tüm waypoint'lere ulaşıldı.", "success", 5000)
            self._update_mission_state_display()
            return

        # Gerçekçi varyasyonlar
        v["ground_speed"] = 1.2 + random.random() * 0.6
        v["roll"] = (random.random() - 0.5) * 4
        v["pitch"] = (random.random() - 0.5) * 3
        v["heading"] = target_heading + (random.random() - 0.5) * 5
        v["heading_setpoint"] = target_heading

        heading_error = target_heading - v["heading"]
        thruster_diff = max(-30, min(30, heading_error * 2))
        v["thruster_left"] = 60 + thruster_diff
        v["thruster_right"] = 60 - thruster_diff

        v["battery_voltage"] = max(10.5, v["battery_voltage"] - 0.001)
        v["battery_pct"] = max(0, round((v["battery_voltage"] - 10.5) / 2.5 * 100))
        v["cpu_temp"] = 60 + random.random() * 8
        v["telem_link"] = 95 + random.random() * 5
        v["rssi"] = -70 + random.random() * 10
        v["packet_loss"] = random.random() * 2

        # Track history
        self.track_history.append((v["lat"], v["lon"]))
        if len(self.track_history) > 100:
            self.track_history = self.track_history[-100:]

        # Grafik verisi
        self.graph_tick += 1
        gd = self.graph_data
        gd["time"].append(self.graph_tick)
        gd["speed"].append(v["ground_speed"])
        gd["speed_target"].append(v["speed_setpoint"])
        gd["heading"].append(v["heading"])
        gd["heading_target"].append(v["heading_setpoint"])
        gd["thruster_left"].append(v["thruster_left"])
        gd["thruster_right"].append(v["thruster_right"])
        # Son 60 veriyi tut
        for key in gd:
            if len(gd[key]) > 60:
                gd[key] = gd[key][-60:]

        # UI Güncelle
        self._update_telemetry_display()
        self._update_map()
        self._update_graphs()
        self._update_mission_progress()
        self._check_failsafe()
        self._log_csv_row()

    # ═══════════════════════════════════════════════════════
    # SAAT & TIMER (1s)
    # ═══════════════════════════════════════════════════════
    def _clock_tick(self):
        utc_now = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        self.ui.lbl_utc_time.setText(utc_now)

        if self.mission_started and self.competition_time > 0:
            self.competition_time -= 1
        minutes = self.competition_time // 60
        seconds = self.competition_time % 60
        timer_text = f"{minutes:02d}:{seconds:02d}"
        self.ui.lbl_competition_timer.setText(timer_text)

        # Timer renk uyarıları
        total_secs = self.competition_time
        if total_secs <= 0 and self.mission_started:
            self.ui.lbl_competition_timer.setStyleSheet("color: #ef4444; font-weight: bold;")
            if not hasattr(self, '_time_expired_shown'):
                self._time_expired_shown = True
                ToastManager.show_toast(
                    self, "SÜRE DOLDU!", "error", persistent=True, center=True
                )
                self._log_to_console("SÜRE DOLDU!", "ERROR")
        elif total_secs <= 120:
            self.ui.lbl_competition_timer.setStyleSheet("color: #ef4444; font-weight: bold;")
        elif total_secs <= 300:
            self.ui.lbl_competition_timer.setStyleSheet("color: #f97316; font-weight: bold;")
        else:
            self.ui.lbl_competition_timer.setStyleSheet("color: #fbbf24;")

        # Recording göstergeleri
        if self.mission_started:
            for lbl in [self.ui.lbl_rec_logging, self.ui.lbl_rec_csv,
                        self.ui.lbl_rec_autonomy, self.ui.lbl_rec_map]:
                lbl.setObjectName("rec_active")
                lbl.setStyleSheet("color: #22c55e;")
        else:
            for lbl in [self.ui.lbl_rec_logging, self.ui.lbl_rec_csv,
                        self.ui.lbl_rec_autonomy, self.ui.lbl_rec_map]:
                lbl.setObjectName("rec_inactive")
                lbl.setStyleSheet("color: #475569;")

        # Bağlantı sağlık göstergeleri güncelle
        self._update_connection_indicators()

    # ═══════════════════════════════════════════════════════
    # ENGEL HARİTASI GÜNCELLEME (5s)
    # ═══════════════════════════════════════════════════════
    def _generate_obstacles(self):
        obstacles = []
        for _ in range(150):
            angle = random.random() * math.pi * 2
            dist = random.random() * 8 + 1
            obstacles.append((
                math.cos(angle) * dist,
                math.sin(angle) * dist,
                random.random(),
            ))
        self.ui.obstacle_map.set_obstacles(obstacles)
        self.ui.obstacle_map.set_vehicle_heading(self.vehicle["heading"])

    # ═══════════════════════════════════════════════════════
    # UI GÜNCELLEME YARDIMCILARI
    # ═══════════════════════════════════════════════════════
    def _update_telemetry_display(self):
        v = self.vehicle
        tl = self.ui.telem_labels

        tl["latitude"].setText(f"{v['lat']:.7f}°")
        tl["longitude"].setText(f"{v['lon']:.7f}°")
        tl["ground_speed"].setText(f"{v['ground_speed']:.2f} m/s")
        tl["roll"].setText(f"{v['roll']:.1f}°")
        tl["pitch"].setText(f"{v['pitch']:.1f}°")
        tl["heading"].setText(f"{v['heading']:.1f}°")

        tl["speed_setpoint"].setText(f"{v['speed_setpoint']:.2f} m/s")
        tl["heading_setpoint"].setText(f"{v['heading_setpoint']:.1f}°")
        tl["thruster_left"].setText(f"{v['thruster_left']:.1f}%")
        tl["thruster_right"].setText(f"{v['thruster_right']:.1f}%")

        tl["telem_link"].setText(f"{v['telem_link']:.0f}%")
        if v["telem_link"] < 70:
            tl["telem_link"].setStyleSheet("color: #f87171;")
        elif v["telem_link"] < 90:
            tl["telem_link"].setStyleSheet("color: #fbbf24;")
        else:
            tl["telem_link"].setStyleSheet("color: #f1f5f9;")

        tl["rc_link"].setText(v["rc_link"])
        if self.failsafe_active:
            tl["rc_link"].setText("KOPTU")
            tl["rc_link"].setStyleSheet("color: #f87171;")
        else:
            tl["rc_link"].setStyleSheet("color: #f1f5f9;")

        tl["rssi"].setText(f"{v['rssi']:.0f} dBm")
        if v["rssi"] < -85:
            tl["rssi"].setStyleSheet("color: #f87171;")
        elif v["rssi"] < -75:
            tl["rssi"].setStyleSheet("color: #fbbf24;")
        else:
            tl["rssi"].setStyleSheet("color: #f1f5f9;")

        tl["packet_loss"].setText(f"{v['packet_loss']:.2f}%")
        if v["packet_loss"] > 5:
            tl["packet_loss"].setStyleSheet("color: #f87171;")
        else:
            tl["packet_loss"].setStyleSheet("color: #f1f5f9;")

        tl["battery_voltage"].setText(f"{v['battery_voltage']:.2f} V")
        if v["battery_voltage"] < 11.0:
            tl["battery_voltage"].setStyleSheet("color: #f87171;")
        else:
            tl["battery_voltage"].setStyleSheet("color: #f1f5f9;")

        tl["battery_pct"].setText(f"{v['battery_pct']}%")
        if v["battery_pct"] < 20:
            tl["battery_pct"].setStyleSheet("color: #f87171;")
        else:
            tl["battery_pct"].setStyleSheet("color: #f1f5f9;")

        tl["cpu_temp"].setText(f"{v['cpu_temp']:.0f}°C")
        if v["cpu_temp"] > 75:
            tl["cpu_temp"].setStyleSheet("color: #f87171;")
        else:
            tl["cpu_temp"].setStyleSheet("color: #f1f5f9;")

        tl["gps_fix"].setText(v["gps_fix"])
        tl["hdop"].setText(f"{v['hdop']:.2f}")
        if v["hdop"] > 2.0:
            tl["hdop"].setStyleSheet("color: #f87171;")
        else:
            tl["hdop"].setStyleSheet("color: #f1f5f9;")

        # Vehicle Mode rengi
        mode = v["mode"]
        mode_colors = {
            "GÖREV": "#4ade80",
            "MANUEL": "#60a5fa",
            "GÜVENLİK": "#f87171",
        }
        self.ui.lbl_vehicle_mode.setText(mode)
        self.ui.lbl_vehicle_mode.setStyleSheet(
            f"color: {mode_colors.get(mode, '#94a3b8')};"
        )

        # Target Detection (simülasyon)
        tl["target_status"].setText(
            "TESPİT EDİLDİ" if self.mission_started else "BEKLENİYOR"
        )
        if self.mission_started:
            tl["target_status"].setStyleSheet("color: #4ade80;")
            tl["target_color"].setText(self.ui.combo_target_color.currentText())
            tl["target_color"].setStyleSheet("color: #f1f5f9;")
            tl["target_confidence"].setText(f"{85 + random.random()*15:.1f}%")
            tl["target_distance"].setText(f"{2 + random.random()*8:.1f} m")
        else:
            tl["target_status"].setStyleSheet("color: #475569;")
            tl["target_color"].setText("—")
            tl["target_confidence"].setText("—")
            tl["target_distance"].setText("—")

    def _update_map(self):
        v = self.vehicle
        waypoints = self._get_waypoints()

        self.ui.navigation_map.set_vehicle_state(v["lat"], v["lon"], v["heading"])
        self.ui.navigation_map.set_waypoints(waypoints, self.active_waypoint)
        self.ui.navigation_map.set_track_history(self.track_history)
        self.ui.navigation_map.set_mission_state(self.mission_state)

        # Obstacle harita heading'i de güncelle
        self.ui.obstacle_map.set_vehicle_heading(v["heading"])

    def _update_graphs(self):
        gd = self.graph_data
        t = gd["time"][-20:] if len(gd["time"]) > 20 else gd["time"]
        n = len(t)

        self.curve_speed.setData(t, gd["speed"][-n:])
        self.curve_speed_target.setData(t, gd["speed_target"][-n:])

        self.curve_heading.setData(t, gd["heading"][-n:])
        self.curve_heading_target.setData(t, gd["heading_target"][-n:])

        self.curve_thruster_l.setData(t, gd["thruster_left"][-n:])
        self.curve_thruster_r.setData(t, gd["thruster_right"][-n:])

    def _update_mission_state_display(self):
        state = self.mission_state
        lbl = self.ui.lbl_mission_state
        frame = self.ui.frame_mission_state

        lbl.setText(state)

        # Pulse/blink timer'larını durdur
        if hasattr(self, '_state_blink_timer'):
            self._state_blink_timer.stop()

        if state == "BEKLEMEDE":
            lbl.setStyleSheet("color: #94a3b8;")
            frame.setStyleSheet(
                "background-color: #0f172a; border: 2px solid #475569; border-radius: 12px;"
            )
        elif "ACİL" in state or "E-STOP" in state:
            lbl.setStyleSheet("color: #f87171;")
            frame.setStyleSheet(
                "background-color: #450a0a; border: 2px solid #dc2626; border-radius: 12px;"
            )
            # Yanıp sönme (yavaş)
            if not hasattr(self, '_state_blink_timer'):
                self._state_blink_timer = QTimer(self)
                self._state_blink_visible = True
            self._state_blink_timer.timeout.connect(self._toggle_state_blink)
            self._state_blink_timer.start(800)
        elif "TAMAMLANDI" in state or "COMPLETE" in state:
            lbl.setStyleSheet("color: #4ade80;")
            frame.setStyleSheet(
                "background-color: #052e16; border: 2px solid #16a34a; border-radius: 12px;"
            )
        elif self.vehicle.get("mode") == "GÖREV":
            lbl.setStyleSheet("color: #4ade80;")
            frame.setStyleSheet(
                "background-color: #052e16; border: 2px solid #22c55e; border-radius: 12px;"
            )
            # Yavaş pulse (GÖREV modu)
            if not hasattr(self, '_state_blink_timer'):
                self._state_blink_timer = QTimer(self)
                self._state_blink_visible = True
            self._state_blink_timer.timeout.connect(self._toggle_state_pulse)
            self._state_blink_timer.start(1500)
        elif self.vehicle.get("mode") == "MANUEL":
            lbl.setStyleSheet("color: #60a5fa;")
            frame.setStyleSheet(
                "background-color: #0c1e3d; border: 2px solid #3b82f6; border-radius: 12px;"
            )
        else:
            lbl.setStyleSheet("color: #22d3ee;")
            frame.setStyleSheet(
                "background-color: #083344; border: 2px solid #0891b2; border-radius: 12px;"
            )

    def _toggle_state_blink(self):
        """ACİL DURDUR yanıp sönme."""
        self._state_blink_visible = not self._state_blink_visible
        if self._state_blink_visible:
            self.ui.frame_mission_state.setStyleSheet(
                "background-color: #450a0a; border: 2px solid #dc2626; border-radius: 12px;"
            )
        else:
            self.ui.frame_mission_state.setStyleSheet(
                "background-color: #1c0505; border: 2px solid #7f1d1d; border-radius: 12px;"
            )

    def _toggle_state_pulse(self):
        """GÖREV modu yavaş pulse."""
        self._state_blink_visible = not self._state_blink_visible
        if self._state_blink_visible:
            self.ui.frame_mission_state.setStyleSheet(
                "background-color: #052e16; border: 2px solid #22c55e; border-radius: 12px;"
            )
        else:
            self.ui.frame_mission_state.setStyleSheet(
                "background-color: #041f10; border: 2px solid #166534; border-radius: 12px;"
            )

    def _update_connection_indicators(self):
        """Header'daki bağlantı sağlık göstergelerini güncelle."""
        v = self.vehicle

        # RC bağlantı
        rc_ok = not self.failsafe_active and v.get("rc_link") == "Bağlı"
        self.ui.lbl_ind_rc.setText(f"● RC {'Bağlı' if rc_ok else 'KOPTU'}")
        self.ui.lbl_ind_rc.setStyleSheet(f"color: {'#4ade80' if rc_ok else '#f87171'}; font-weight: bold;")

        # Telemetri
        telem_ok = v.get("telem_link", 0) > 60
        self.ui.lbl_ind_telem.setText(f"● Telem {'OK' if telem_ok else 'DÜŞÜK'}")
        self.ui.lbl_ind_telem.setStyleSheet(f"color: {'#4ade80' if telem_ok else '#f87171'}; font-weight: bold;")

        # GPS
        gps_fix = v.get("gps_fix", "")
        gps_ok = "Fixed" in str(gps_fix) or "3D" in str(gps_fix)
        self.ui.lbl_ind_gps.setText(f"● GPS {gps_fix}")
        self.ui.lbl_ind_gps.setStyleSheet(f"color: {'#4ade80' if gps_ok else '#fbbf24'}; font-weight: bold;")

        # Header border: kopukluk varsa kırmızı
        any_bad = not rc_ok or not telem_ok
        if any_bad:
            self.ui.header_frame.setStyleSheet(
                self.ui.header_frame.styleSheet().replace(
                    "border-color: rgba(99, 102, 241",
                    "border-color: rgba(220, 38, 38"
                ) if "border-color" in self.ui.header_frame.styleSheet()
                else ""
            )

    # ═══════════════════════════════════════════════════════
    # YARDIMCI FONKSİYONLAR
    # ═══════════════════════════════════════════════════════

    # ── CSV LOGLAMA (≥1Hz, şartname zorunlu) ─────────────
    def _start_csv_logging(self):
        """CSV dosyası oluştur ve header yaz."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True)
        filepath = os.path.join(log_dir, f"telemetry_{ts}.csv")
        self.csv_file = open(filepath, "w", newline="", encoding="utf-8")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow([
            "timestamp_utc", "lat", "lon", "ground_speed", "heading",
            "roll", "pitch", "speed_setpoint", "heading_setpoint",
            "thruster_left", "thruster_right", "battery_voltage",
            "battery_pct", "cpu_temp", "gps_fix", "hdop",
            "telem_link", "rssi", "packet_loss", "mode", "mission_state",
        ])
        self._log_to_console(f"CSV kayıt başladı: {os.path.basename(filepath)}", "INFO")
        self.statusBar().showMessage(f"📁 CSV kayıt başladı: {filepath}")

    def _log_csv_row(self):
        """Her tick'te telemetri satırı yaz (≥1Hz)."""
        if self.csv_writer is None:
            return
        v = self.vehicle
        self.csv_writer.writerow([
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            f"{v['lat']:.7f}", f"{v['lon']:.7f}",
            f"{v['ground_speed']:.2f}", f"{v['heading']:.1f}",
            f"{v['roll']:.1f}", f"{v['pitch']:.1f}",
            f"{v['speed_setpoint']:.2f}", f"{v['heading_setpoint']:.1f}",
            f"{v['thruster_left']:.1f}", f"{v['thruster_right']:.1f}",
            f"{v['battery_voltage']:.2f}", v['battery_pct'],
            f"{v['cpu_temp']:.0f}", v['gps_fix'], f"{v['hdop']:.2f}",
            f"{v['telem_link']:.0f}", f"{v['rssi']:.0f}",
            f"{v['packet_loss']:.2f}", v['mode'], self.mission_state,
        ])
        self.csv_file.flush()

    # ── FAİLSAFE KONTROL ─────────────────────────────────
    def _check_failsafe(self):
        """Telemetri link kontrolü — kopunca failsafe uyarısı."""
        v = self.vehicle
        # Simülasyonda: packet_loss > 10 veya telem_link < 50 → failsafe
        link_lost = v["telem_link"] < 50 or v["packet_loss"] > 10

        if link_lost and not self.failsafe_active:
            self.failsafe_active = True
            self.vehicle["mode"] = "GÜVENLİK"
            self.mission_state = "GÜVENLİK — BAĞLANTI KOPTU"
            self._update_mission_state_display()
            self.ui.frame_failsafe.show()
            self.ui.btn_mode_switch.setEnabled(False)
            self._log_to_console("FAILSAFE — İletişim koptu!", "ERROR")
            self.statusBar().showMessage("⚠ GÜVENLİK MODU — İletişim koptu!")
        elif not link_lost and self.failsafe_active:
            self.failsafe_active = False
            self.ui.frame_failsafe.hide()
            self.ui.btn_mode_switch.setEnabled(True)
            self._log_to_console("İletişim geri geldi", "SUCCESS")
            self.statusBar().showMessage("✓ İletişim geri geldi")

    # ── GÖREV İLERLEME ───────────────────────────────────
    def _update_mission_progress(self):
        """Header'daki progress bar ve label'ı güncelle."""
        waypoints = self._get_waypoints()
        total = len(waypoints)
        if total == 0:
            self.ui.lbl_mission_progress.setText("WP 0/0 — %0")
            self.ui.progress_mission.setValue(0)
            return

        current = min(self.active_waypoint + 1, total)
        pct = round((self.active_waypoint / total) * 100) if total > 0 else 0

        if self.mission_state == "GÖREV TAMAMLANDI":
            current = total
            pct = 100

        self.ui.lbl_mission_progress.setText(
            f"WP {current}/{total} — %{pct}"
        )
        self.ui.progress_mission.setValue(pct)

    def closeEvent(self, event):
        """Pencere kapanırken CSV dosyasını kapat."""
        if self.csv_file is not None:
            self.csv_file.close()
        event.accept()

    def _get_waypoints(self):
        """Waypoint giriş alanlarından geçerli (lat, lon) tuple listesi döner."""
        waypoints = []
        pattern = re.compile(r"^-?\d{1,3}\.\d{7}$")
        for edit_lat, edit_lon in self.ui.wp_entries:
            lat_str = edit_lat.text().strip()
            lon_str = edit_lon.text().strip()
            
            if not lat_str or not lon_str:
                continue
                
            if not pattern.match(lat_str) or not pattern.match(lon_str):
                continue
                
            try:
                lat = float(lat_str)
                lon = float(lon_str)
                waypoints.append((lat, lon))
            except ValueError:
                continue
        return waypoints


# ═══════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)

    # Uygulama geneli font — büyütülmüş
    font = QFont("Segoe UI", 12)
    app.setFont(font)

    window = GCSMainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
