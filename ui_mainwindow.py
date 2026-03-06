# -*- coding: utf-8 -*-
"""
ui_mainwindow.py — USV GCS Premium UI Layout
Tamamen yenilenmiş, büyük ve premium tasarım.
"""

from PyQt5.QtCore import QMetaObject, Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QGroupBox,
    QFrame, QSplitter, QSizePolicy, QSpacerItem, QScrollArea,
    QStatusBar, QFileDialog, QCheckBox, QProgressBar, QGraphicsDropShadowEffect
)

# Özel widget import'ları
from custom_widgets import NavigationMapWidget, ObstacleMapWidget


# ═══════════════════════════════════════════════════════════
# YARDIMCI: Glow efekti
# ═══════════════════════════════════════════════════════════
def _add_glow(widget, color="#6366f1", radius=20, offset_y=2):
    """Widget'a hafif bir glow efekti ekler."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(radius)
    shadow.setColor(QColor(color))
    shadow.setOffset(0, offset_y)
    widget.setGraphicsEffect(shadow)


class Ui_MainWindow(object):
    """
    Premium UI layout — glassmorphism + neon accents.
    setupUi() tüm widget'ları oluşturur ve yerleştirir.
    """

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1700, 1000)
        MainWindow.setMinimumSize(QSize(1280, 768))
        MainWindow.setWindowTitle("USV Ground Control Station — Teknofest")

        # ═══════════════════════════════════════════════════
        # Central Widget
        # ═══════════════════════════════════════════════════
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background-color: #080c18;")
        MainWindow.setCentralWidget(self.centralwidget)

        self.main_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(12, 10, 12, 6)
        self.main_layout.setSpacing(8)

        # ═══════════════════════════════════════════════════
        # HEADER BAR
        # ═══════════════════════════════════════════════════
        self._build_header()
        self.main_layout.addWidget(self.header_frame)

        # ═══════════════════════════════════════════════════
        # FAILSAFE ALERT BANNER
        # ═══════════════════════════════════════════════════
        self.frame_failsafe = QFrame()
        self.frame_failsafe.setObjectName("frame_failsafe")
        self.frame_failsafe.setFixedHeight(48)
        fs_layout = QHBoxLayout(self.frame_failsafe)
        fs_layout.setContentsMargins(16, 6, 16, 6)
        self.lbl_failsafe = QLabel("⚠  LINK LOST — FAILSAFE ACTIVE  ⚠")
        self.lbl_failsafe.setFont(QFont("JetBrains Mono", 14, QFont.Bold))
        self.lbl_failsafe.setAlignment(Qt.AlignCenter)
        fs_layout.addWidget(self.lbl_failsafe)
        self.frame_failsafe.hide()
        self.main_layout.addWidget(self.frame_failsafe)

        # ═══════════════════════════════════════════════════
        # VIDEO LAYOUT SELECTOR
        # ═══════════════════════════════════════════════════
        self._build_video_layout_bar()
        self.main_layout.addWidget(self.frame_video_layout)

        # ═══════════════════════════════════════════════════
        # TÜM iç WIDGET'LARI OLUŞTUR
        # ═══════════════════════════════════════════════════
        self._create_all_inner_widgets()

        # ═══════════════════════════════════════════════════
        # CONTENT AREA
        # ═══════════════════════════════════════════════════
        self.content_container = QWidget()
        self.content_container.setObjectName("content_container")
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        self.main_layout.addWidget(self.content_container, 1)

        self._active_content = None

        # Varsayılan: Single Screen
        self.apply_single_layout()

        # ═══════════════════════════════════════════════════
        # STATUS BAR
        # ═══════════════════════════════════════════════════
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    # ═══════════════════════════════════════════════════════
    # HEADER — Premium Design
    # ═══════════════════════════════════════════════════════
    def _build_header(self):
        self.header_frame = QFrame()
        self.header_frame.setObjectName("header_frame")
        self.header_frame.setFrameShape(QFrame.StyledPanel)
        self.header_frame.setFixedHeight(72)
        _add_glow(self.header_frame, "#6366f1", 30, 3)
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(20, 6, 20, 6)
        header_layout.setSpacing(16)

        # Logo / Başlık
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        self.lbl_title = QLabel("⛵  USV Ground Control Station")
        self.lbl_title.setObjectName("lbl_title")
        self.lbl_title.setFont(QFont("Segoe UI", 17, QFont.Bold))
        self.lbl_subtitle = QLabel("Autonomous Navigation Monitor  ●  Teknofest 2025")
        self.lbl_subtitle.setObjectName("lbl_subtitle")
        self.lbl_subtitle.setFont(QFont("JetBrains Mono", 10))
        title_layout.addWidget(self.lbl_title)
        title_layout.addWidget(self.lbl_subtitle)
        header_layout.addLayout(title_layout)

        header_layout.addStretch()

        # Mission Progress
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(2)
        self.lbl_mission_progress = QLabel("WP 0/0 — %0")
        self.lbl_mission_progress.setObjectName("lbl_mission_progress")
        self.lbl_mission_progress.setFont(QFont("JetBrains Mono", 11, QFont.Bold))
        self.lbl_mission_progress.setAlignment(Qt.AlignCenter)
        self.progress_mission = QProgressBar()
        self.progress_mission.setObjectName("progress_mission")
        self.progress_mission.setFixedSize(200, 14)
        self.progress_mission.setTextVisible(False)
        self.progress_mission.setRange(0, 100)
        self.progress_mission.setValue(0)
        progress_layout.addWidget(self.lbl_mission_progress)
        progress_layout.addWidget(self.progress_mission)
        header_layout.addLayout(progress_layout)

        header_layout.addSpacing(8)

        # Mission State Badge
        self.frame_mission_state = QFrame()
        self.frame_mission_state.setObjectName("frame_mission_state")
        self.frame_mission_state.setFixedSize(200, 56)
        ms_layout = QVBoxLayout(self.frame_mission_state)
        ms_layout.setContentsMargins(14, 4, 14, 4)
        ms_layout.setSpacing(2)
        self.lbl_mission_state_label = QLabel("MISSION STATE")
        self.lbl_mission_state_label.setFont(QFont("JetBrains Mono", 8, QFont.Bold))
        self.lbl_mission_state_label.setObjectName("lbl_mission_state_label")
        self.lbl_mission_state = QLabel("STANDBY")
        self.lbl_mission_state.setObjectName("lbl_mission_state")
        self.lbl_mission_state.setFont(QFont("Segoe UI", 14, QFont.Bold))
        ms_layout.addWidget(self.lbl_mission_state_label)
        ms_layout.addWidget(self.lbl_mission_state)
        header_layout.addWidget(self.frame_mission_state)

        header_layout.addSpacing(8)

        # Start Mission
        self.btn_start_mission = QPushButton("▶  Start Mission")
        self.btn_start_mission.setObjectName("btn_start_mission")
        self.btn_start_mission.setFixedSize(170, 44)
        self.btn_start_mission.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_start_mission.setCursor(Qt.PointingHandCursor)
        self.btn_start_mission.setToolTip("Otonom görevi başlatır")
        header_layout.addWidget(self.btn_start_mission)

        # E-STOP
        self.btn_estop = QPushButton("⛔  E-STOP")
        self.btn_estop.setObjectName("btn_estop")
        self.btn_estop.setFixedSize(140, 44)
        self.btn_estop.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.btn_estop.setCursor(Qt.PointingHandCursor)
        self.btn_estop.setToolTip("ACİL DURDURMA: Motor gücünü anında keser")
        _add_glow(self.btn_estop, "#dc2626", 25, 2)
        header_layout.addWidget(self.btn_estop)

        # Power Status
        self.lbl_power_status = QLabel("⏻ ACTIVE")
        self.lbl_power_status.setObjectName("lbl_power_status")
        self.lbl_power_status.setFont(QFont("JetBrains Mono", 12, QFont.Bold))
        header_layout.addWidget(self.lbl_power_status)

    # ═══════════════════════════════════════════════════════
    # VIDEO LAYOUT SELECTOR BAR
    # ═══════════════════════════════════════════════════════
    def _build_video_layout_bar(self):
        self.frame_video_layout = QFrame()
        self.frame_video_layout.setObjectName("frame_video_layout")
        self.frame_video_layout.setFixedHeight(42)
        vl_layout = QHBoxLayout(self.frame_video_layout)
        vl_layout.setContentsMargins(16, 6, 16, 6)
        vl_layout.setSpacing(10)

        self.lbl_video_icon = QLabel("🖥")
        self.lbl_video_icon.setFont(QFont("Segoe UI", 14))
        self.lbl_video_layout_title = QLabel("Display Layout")
        self.lbl_video_layout_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        vl_layout.addWidget(self.lbl_video_icon)
        vl_layout.addWidget(self.lbl_video_layout_title)

        self.lbl_video_subtitle = QLabel("")
        self.lbl_video_subtitle.setObjectName("lbl_video_subtitle")
        self.lbl_video_subtitle.setFont(QFont("JetBrains Mono", 9))
        vl_layout.addWidget(self.lbl_video_subtitle)

        vl_layout.addStretch()

        self.btn_single_screen = QPushButton("⬜  Single Screen")
        self.btn_single_screen.setObjectName("btn_single_screen")
        self.btn_single_screen.setCheckable(True)
        self.btn_single_screen.setChecked(True)
        self.btn_single_screen.setFixedSize(150, 30)
        self.btn_single_screen.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.btn_single_screen.setCursor(Qt.PointingHandCursor)

        self.btn_3screen = QPushButton("☰  3-Screen Split")
        self.btn_3screen.setObjectName("btn_3screen")
        self.btn_3screen.setCheckable(True)
        self.btn_3screen.setFixedSize(150, 30)
        self.btn_3screen.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.btn_3screen.setCursor(Qt.PointingHandCursor)

        vl_layout.addWidget(self.btn_single_screen)
        vl_layout.addWidget(self.btn_3screen)

    # ═══════════════════════════════════════════════════════
    # TÜM İÇ WIDGET'LARI OLUŞTUR
    # ═══════════════════════════════════════════════════════
    def _create_all_inner_widgets(self):
        """Tüm iç widget'ları oluştur (layout-bağımsız)."""

        # ── MISSION SETUP ────────────────────────────────
        self.mission_content = QWidget()
        mission_lay = QVBoxLayout(self.mission_content)
        mission_lay.setContentsMargins(12, 8, 12, 8)
        mission_lay.setSpacing(6)

        # Section header with icon
        mission_header = QHBoxLayout()
        lbl_mission_icon = QLabel("🎯")
        lbl_mission_icon.setFont(QFont("Segoe UI", 14))
        lbl_mission = QLabel("MISSION SETUP")
        lbl_mission.setObjectName("section_header")
        lbl_mission.setFont(QFont("Segoe UI", 13, QFont.Bold))
        mission_header.addWidget(lbl_mission_icon)
        mission_header.addWidget(lbl_mission)
        mission_header.addStretch()
        mission_lay.addLayout(mission_header)

        # Waypoint giriş alanları
        self.wp_entries = []
        for i in range(4):
            wp_frame = QFrame()
            wp_frame.setObjectName("wp_group")
            wp_grid = QGridLayout(wp_frame)
            wp_grid.setContentsMargins(10, 10, 10, 10)
            wp_grid.setSpacing(6)
            wp_grid.setColumnStretch(1, 1)

            lbl_wp = QLabel(f"📍 WP{i+1}")
            lbl_wp.setFont(QFont("Segoe UI", 11, QFont.Bold))
            lbl_wp.setStyleSheet("color: #818cf8;")
            wp_grid.addWidget(lbl_wp, 0, 0, 1, 2)

            lbl_lat = QLabel("Latitude")
            lbl_lat.setFont(QFont("JetBrains Mono", 9))
            lbl_lat.setStyleSheet("color: rgba(148, 163, 184, 0.7);")
            edit_lat = QLineEdit()
            edit_lat.setObjectName(f"edit_wp{i+1}_lat")
            edit_lat.setFont(QFont("JetBrains Mono", 11))
            edit_lat.setPlaceholderText("00.0000000")
            edit_lat.setFixedHeight(34)

            lbl_lon = QLabel("Longitude")
            lbl_lon.setFont(QFont("JetBrains Mono", 9))
            lbl_lon.setStyleSheet("color: rgba(148, 163, 184, 0.7);")
            edit_lon = QLineEdit()
            edit_lon.setObjectName(f"edit_wp{i+1}_lon")
            edit_lon.setFont(QFont("JetBrains Mono", 11))
            edit_lon.setPlaceholderText("00.0000000")
            edit_lon.setFixedHeight(34)

            wp_grid.addWidget(lbl_lat, 1, 0)
            wp_grid.addWidget(edit_lat, 1, 1)
            wp_grid.addWidget(lbl_lon, 2, 0)
            wp_grid.addWidget(edit_lon, 2, 1)

            self.wp_entries.append((edit_lat, edit_lon))
            mission_lay.addWidget(wp_frame)

        # Target Color
        sep1 = QFrame()
        sep1.setObjectName("panel_separator")
        sep1.setFrameShape(QFrame.HLine)
        sep1.setFixedHeight(1)
        mission_lay.addWidget(sep1)

        target_layout = QHBoxLayout()
        lbl_target_icon = QLabel("🎨")
        lbl_target_icon.setFont(QFont("Segoe UI", 12))
        lbl_target = QLabel("Target Color")
        lbl_target.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl_target.setStyleSheet("color: #a5b4fc;")
        target_layout.addWidget(lbl_target_icon)
        target_layout.addWidget(lbl_target)
        target_layout.addStretch()
        mission_lay.addLayout(target_layout)

        self.combo_target_color = QComboBox()
        self.combo_target_color.setObjectName("combo_target_color")
        self.combo_target_color.setFont(QFont("Segoe UI", 11))
        self.combo_target_color.setFixedHeight(36)
        self.combo_target_color.addItems(["Red", "Green", "Blue", "Yellow"])
        mission_lay.addWidget(self.combo_target_color)

        # Upload Status
        self.lbl_upload_status = QLabel("")
        self.lbl_upload_status.setObjectName("lbl_upload_status")
        self.lbl_upload_status.setFont(QFont("JetBrains Mono", 10))
        self.lbl_upload_status.setWordWrap(True)
        self.lbl_upload_status.hide()
        mission_lay.addWidget(self.lbl_upload_status)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.btn_import_wp = QPushButton("📂  Import File")
        self.btn_import_wp.setObjectName("btn_import_wp")
        self.btn_import_wp.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.btn_import_wp.setFixedHeight(38)
        self.btn_import_wp.setCursor(Qt.PointingHandCursor)
        self.btn_import_wp.setToolTip("Görev dosyasından WP yükle")

        self.btn_clear_waypoints = QPushButton("🗑  Clear")
        self.btn_clear_waypoints.setObjectName("btn_clear_waypoints")
        self.btn_clear_waypoints.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.btn_clear_waypoints.setFixedHeight(38)
        self.btn_clear_waypoints.setCursor(Qt.PointingHandCursor)

        btn_layout.addWidget(self.btn_import_wp)
        btn_layout.addWidget(self.btn_clear_waypoints)
        mission_lay.addLayout(btn_layout)

        self.btn_upload_mission = QPushButton("⬆  Upload Mission")
        self.btn_upload_mission.setObjectName("btn_upload_mission")
        self.btn_upload_mission.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.btn_upload_mission.setFixedHeight(42)
        self.btn_upload_mission.setCursor(Qt.PointingHandCursor)
        self.btn_upload_mission.setToolTip("Koordinatları onayla ve araca yükle")
        mission_lay.addWidget(self.btn_upload_mission)

        # PRE-FLIGHT COMPATIBILITY
        sep2 = QFrame()
        sep2.setObjectName("panel_separator")
        sep2.setFrameShape(QFrame.HLine)
        sep2.setFixedHeight(1)
        mission_lay.addWidget(sep2)

        compat_header = QHBoxLayout()
        lbl_compat_icon = QLabel("✅")
        lbl_compat_icon.setFont(QFont("Segoe UI", 12))
        lbl_compat = QLabel("PRE-FLIGHT CHECK")
        lbl_compat.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl_compat.setStyleSheet("color: #c7d2fe;")
        compat_header.addWidget(lbl_compat_icon)
        compat_header.addWidget(lbl_compat)
        compat_header.addStretch()
        mission_lay.addLayout(compat_header)

        freq_layout = QHBoxLayout()
        freq_layout.setContentsMargins(0, 0, 0, 0)
        lbl_freq = QLabel("Frequency:")
        lbl_freq.setFont(QFont("Segoe UI", 10))
        lbl_freq.setStyleSheet("color: #94a3b8;")
        self.combo_frequency = QComboBox()
        self.combo_frequency.setFont(QFont("Segoe UI", 10))
        self.combo_frequency.setFixedHeight(32)
        self.combo_frequency.addItems(["433 MHz", "868 MHz", "900 MHz", "2.4 GHz"])
        freq_layout.addWidget(lbl_freq)
        freq_layout.addWidget(self.combo_frequency, 1)
        mission_lay.addLayout(freq_layout)

        self.check_wifi = QCheckBox("Wi-Fi is OFF (Required)")
        self.check_wifi.setFont(QFont("Segoe UI", 10))
        self.check_race_mode = QCheckBox("Competition Mode Verified")
        self.check_race_mode.setFont(QFont("Segoe UI", 10))

        mission_lay.addWidget(self.check_wifi)
        mission_lay.addWidget(self.check_race_mode)

        mission_lay.addStretch()

        # ── NAVIGATION MAP ──────────────────────────────
        self.navigation_map = NavigationMapWidget()
        self.navigation_map.setObjectName("navigation_map")

        self.map_content = QWidget()
        map_lay = QVBoxLayout(self.map_content)
        map_lay.setContentsMargins(10, 6, 10, 6)
        map_lay.setSpacing(6)

        map_header = QHBoxLayout()
        self.lbl_map_indicator = QLabel("")
        self.lbl_map_indicator.setFixedSize(5, 20)
        self.lbl_map_indicator.setObjectName("accent_bar")
        self.lbl_map_title = QLabel("🗺  NAVIGATION MAP")
        self.lbl_map_title.setObjectName("section_header")
        self.lbl_map_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        map_header.addWidget(self.lbl_map_indicator)
        map_header.addWidget(self.lbl_map_title)
        map_header.addStretch()
        map_lay.addLayout(map_header)
        map_lay.addWidget(self.navigation_map, 1)

        # ── TELEMETRY ────────────────────────────────────
        self.telem_content = QWidget()
        telem_lay = QVBoxLayout(self.telem_content)
        telem_lay.setContentsMargins(12, 6, 12, 6)
        telem_lay.setSpacing(3)

        telem_header = QHBoxLayout()
        lbl_telem_icon = QLabel("📡")
        lbl_telem_icon.setFont(QFont("Segoe UI", 14))
        lbl_telem_title = QLabel("TELEMETRY")
        lbl_telem_title.setObjectName("section_header")
        lbl_telem_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        telem_header.addWidget(lbl_telem_icon)
        telem_header.addWidget(lbl_telem_title)
        telem_header.addStretch()
        telem_lay.addLayout(telem_header)

        telem_scroll = QScrollArea()
        telem_scroll.setWidgetResizable(True)
        telem_scroll.setFrameShape(QFrame.NoFrame)
        telem_scroll_content = QWidget()
        self.telem_layout = QVBoxLayout(telem_scroll_content)
        self.telem_layout.setContentsMargins(0, 0, 0, 0)
        self.telem_layout.setSpacing(3)

        self.telem_labels = {}

        self._add_telem_section("⚓  Navigation")
        for key, label in [
            ("latitude", "Latitude"), ("longitude", "Longitude"),
            ("ground_speed", "Ground Speed"), ("roll", "Roll"),
            ("pitch", "Pitch"), ("heading", "Heading"),
        ]:
            self._add_telem_row(key, label)

        self._add_telem_section("📊  Control Setpoints")
        for key, label in [
            ("speed_setpoint", "Speed Setpoint"),
            ("heading_setpoint", "Heading Setpoint"),
            ("thruster_left", "Thruster Left"),
            ("thruster_right", "Thruster Right"),
        ]:
            self._add_telem_row(key, label)

        self._add_telem_section("📡  Communication")
        for key, label in [
            ("telem_link", "Telemetry Link"),
            ("rc_link", "RC Link Status"),
            ("rssi", "RSSI"),
            ("packet_loss", "Packet Loss"),
        ]:
            self._add_telem_row(key, label)

        self._add_telem_section("🔋  Vehicle Health")
        for key, label in [
            ("battery_voltage", "Battery Voltage"),
            ("battery_pct", "Battery %"),
            ("cpu_temp", "CPU Temperature"),
            ("gps_fix", "GPS Fix Type"),
            ("hdop", "HDOP"),
        ]:
            self._add_telem_row(key, label)

        self._add_telem_section("🎯  Target Detection")
        for key, label in [
            ("target_status", "Detection"),
            ("target_color", "Detected Color"),
            ("target_confidence", "Confidence"),
            ("target_distance", "Distance"),
        ]:
            self._add_telem_row(key, label)

        self.telem_layout.addStretch()
        telem_scroll.setWidget(telem_scroll_content)
        telem_lay.addWidget(telem_scroll, 1)

        # Vehicle Mode
        self.frame_vehicle_mode = QFrame()
        self.frame_vehicle_mode.setObjectName("frame_vehicle_mode")
        self.frame_vehicle_mode.setFixedHeight(56)
        vm_layout = QVBoxLayout(self.frame_vehicle_mode)
        vm_layout.setContentsMargins(12, 6, 12, 6)
        vm_layout.setSpacing(2)
        lbl_vm = QLabel("Vehicle Mode")
        lbl_vm.setFont(QFont("Segoe UI", 9, QFont.Bold))
        lbl_vm.setStyleSheet("color: rgba(148, 163, 184, 0.7);")
        self.lbl_vehicle_mode = QLabel("MANUAL")
        self.lbl_vehicle_mode.setObjectName("lbl_vehicle_mode")
        self.lbl_vehicle_mode.setFont(QFont("Segoe UI", 18, QFont.Bold))
        vm_layout.addWidget(lbl_vm)
        vm_layout.addWidget(self.lbl_vehicle_mode)
        telem_lay.addWidget(self.frame_vehicle_mode)

        # Mode Switch Button
        self.btn_mode_switch = QPushButton("⇄  Switch to MISSION")
        self.btn_mode_switch.setObjectName("btn_mode_switch")
        self.btn_mode_switch.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.btn_mode_switch.setFixedHeight(40)
        self.btn_mode_switch.setCursor(Qt.PointingHandCursor)
        self.btn_mode_switch.setToolTip("Kontrol modunu değiştirir")
        telem_lay.addWidget(self.btn_mode_switch)

        # Power Cut Warning
        self.frame_power_cut = QFrame()
        self.frame_power_cut.setObjectName("frame_power_cut")
        self.frame_power_cut.setFixedHeight(36)
        pc_layout = QHBoxLayout(self.frame_power_cut)
        pc_layout.setContentsMargins(12, 4, 12, 4)
        self.lbl_power_cut = QLabel("⚠ POWER CUT ACTIVE")
        self.lbl_power_cut.setFont(QFont("JetBrains Mono", 11, QFont.Bold))
        pc_layout.addWidget(self.lbl_power_cut)
        self.frame_power_cut.hide()
        telem_lay.addWidget(self.frame_power_cut)
        telem_lay.addStretch()

        # ── DATA LOGGING & GRAPHS ────────────────────────
        self.logging_content = QWidget()
        dl_lay = QVBoxLayout(self.logging_content)
        dl_lay.setContentsMargins(12, 10, 12, 10)
        dl_lay.setSpacing(8)

        dl_header = QHBoxLayout()
        lbl_dl_icon = QLabel("📈")
        lbl_dl_icon.setFont(QFont("Segoe UI", 14))
        lbl_dl_title = QLabel("DATA LOGGING & ANALYSIS")
        lbl_dl_title.setObjectName("section_header")
        lbl_dl_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        dl_header.addWidget(lbl_dl_icon)
        dl_header.addWidget(lbl_dl_title)
        dl_header.addStretch()
        dl_lay.addLayout(dl_header)

        # Recording status bar
        rec_layout = QHBoxLayout()
        rec_layout.setSpacing(12)
        self.lbl_rec_logging = QLabel("●  Logging")
        self.lbl_rec_logging.setFont(QFont("JetBrains Mono", 10))
        self.lbl_rec_logging.setObjectName("rec_inactive")
        self.lbl_rec_csv = QLabel("●  CSV (≥1Hz)")
        self.lbl_rec_csv.setFont(QFont("JetBrains Mono", 10))
        self.lbl_rec_csv.setObjectName("rec_inactive")
        self.lbl_rec_autonomy = QLabel("●  Autonomy")
        self.lbl_rec_autonomy.setFont(QFont("JetBrains Mono", 10))
        self.lbl_rec_autonomy.setObjectName("rec_inactive")
        self.lbl_rec_map = QLabel("●  Map")
        self.lbl_rec_map.setFont(QFont("JetBrains Mono", 10))
        self.lbl_rec_map.setObjectName("rec_inactive")

        lbl_save_icon = QLabel("💾")
        lbl_save_icon.setFont(QFont("Segoe UI", 12))
        rec_layout.addWidget(lbl_save_icon)
        rec_layout.addWidget(self.lbl_rec_logging)
        rec_layout.addWidget(self.lbl_rec_csv)
        rec_layout.addWidget(self.lbl_rec_autonomy)
        rec_layout.addWidget(self.lbl_rec_map)
        rec_layout.addStretch()

        sep_v = QFrame()
        sep_v.setFrameShape(QFrame.VLine)
        sep_v.setObjectName("separator")
        rec_layout.addWidget(sep_v)

        self.lbl_utc_label = QLabel("🕐 UTC")
        self.lbl_utc_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_utc_time = QLabel("00:00:00 UTC")
        self.lbl_utc_time.setFont(QFont("JetBrains Mono", 12, QFont.Bold))
        self.lbl_utc_time.setObjectName("lbl_utc_time")
        rec_layout.addWidget(self.lbl_utc_label)
        rec_layout.addWidget(self.lbl_utc_time)

        sep_v2 = QFrame()
        sep_v2.setFrameShape(QFrame.VLine)
        sep_v2.setObjectName("separator")
        rec_layout.addWidget(sep_v2)

        lbl_timer_icon = QLabel("⏱")
        lbl_timer_icon.setFont(QFont("Segoe UI", 12))
        lbl_timer_label = QLabel("Timer")
        lbl_timer_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_timer_label.setStyleSheet("color: #fbbf24;")
        self.lbl_competition_timer = QLabel("20:00")
        self.lbl_competition_timer.setObjectName("lbl_competition_timer")
        self.lbl_competition_timer.setFont(QFont("JetBrains Mono", 22, QFont.Bold))
        rec_layout.addWidget(lbl_timer_icon)
        rec_layout.addWidget(lbl_timer_label)
        rec_layout.addWidget(self.lbl_competition_timer)

        dl_lay.addLayout(rec_layout)

        # Graph Placeholders
        self.graph_layout = QHBoxLayout()
        self.graph_layout.setSpacing(10)

        self.frame_graph_speed = QFrame()
        self.frame_graph_speed.setObjectName("graph_frame")
        self.frame_graph_speed.setFrameShape(QFrame.StyledPanel)
        speed_lay = QVBoxLayout(self.frame_graph_speed)
        speed_lay.setContentsMargins(10, 8, 10, 8)
        self.lbl_graph_speed_title = QLabel("⚡  Speed vs Target")
        self.lbl_graph_speed_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        speed_lay.addWidget(self.lbl_graph_speed_title)
        self.graph_speed_placeholder = QWidget()
        self.graph_speed_placeholder.setObjectName("graph_speed_placeholder")
        self.graph_speed_placeholder.setMinimumHeight(140)
        speed_lay.addWidget(self.graph_speed_placeholder, 1)
        self.graph_layout.addWidget(self.frame_graph_speed)

        self.frame_graph_heading = QFrame()
        self.frame_graph_heading.setObjectName("graph_frame")
        self.frame_graph_heading.setFrameShape(QFrame.StyledPanel)
        heading_lay = QVBoxLayout(self.frame_graph_heading)
        heading_lay.setContentsMargins(10, 8, 10, 8)
        self.lbl_graph_heading_title = QLabel("🧭  Heading vs Target")
        self.lbl_graph_heading_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        heading_lay.addWidget(self.lbl_graph_heading_title)
        self.graph_heading_placeholder = QWidget()
        self.graph_heading_placeholder.setObjectName("graph_heading_placeholder")
        self.graph_heading_placeholder.setMinimumHeight(140)
        heading_lay.addWidget(self.graph_heading_placeholder, 1)
        self.graph_layout.addWidget(self.frame_graph_heading)

        self.frame_graph_thruster = QFrame()
        self.frame_graph_thruster.setObjectName("graph_frame")
        self.frame_graph_thruster.setFrameShape(QFrame.StyledPanel)
        thruster_lay = QVBoxLayout(self.frame_graph_thruster)
        thruster_lay.setContentsMargins(10, 8, 10, 8)
        self.lbl_graph_thruster_title = QLabel("🔧  Thruster Commands")
        self.lbl_graph_thruster_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        thruster_lay.addWidget(self.lbl_graph_thruster_title)
        self.graph_thruster_placeholder = QWidget()
        self.graph_thruster_placeholder.setObjectName("graph_thruster_placeholder")
        self.graph_thruster_placeholder.setMinimumHeight(140)
        thruster_lay.addWidget(self.graph_thruster_placeholder, 1)
        self.graph_layout.addWidget(self.frame_graph_thruster)

        dl_lay.addLayout(self.graph_layout)

        # ── OBSTACLE MAP ─────────────────────────────────
        self.obstacle_content = QWidget()
        obs_lay = QVBoxLayout(self.obstacle_content)
        obs_lay.setContentsMargins(12, 10, 12, 10)
        obs_lay.setSpacing(6)

        obs_header = QHBoxLayout()
        lbl_obs_icon = QLabel("🛡")
        lbl_obs_icon.setFont(QFont("Segoe UI", 14))
        lbl_obs_title = QLabel("LOCAL OBSTACLE / COST MAP")
        lbl_obs_title.setObjectName("section_header")
        lbl_obs_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        obs_header.addWidget(lbl_obs_icon)
        obs_header.addWidget(lbl_obs_title)
        obs_header.addStretch()
        obs_lay.addLayout(obs_header)

        self.lbl_obstacle_subtitle = QLabel("Live Sensor Data — 10m Range")
        self.lbl_obstacle_subtitle.setFont(QFont("JetBrains Mono", 10))
        self.lbl_obstacle_subtitle.setStyleSheet("color: rgba(148, 163, 184, 0.6);")
        obs_lay.addWidget(self.lbl_obstacle_subtitle)

        self.obstacle_map = ObstacleMapWidget()
        self.obstacle_map.setObjectName("obstacle_map")
        obs_lay.addWidget(self.obstacle_map, 1)

    # ═══════════════════════════════════════════════════════
    # LAYOUT SWITCHING
    # ═══════════════════════════════════════════════════════
    def _detach_all(self):
        """Tüm iç widget'ları mevcut yerlerinden ayır."""
        widgets = [
            self.mission_content, self.map_content,
            self.telem_content, self.logging_content,
            self.obstacle_content,
        ]
        for w in widgets:
            w.setParent(self.centralwidget)
            w.hide()

        if self._active_content is not None:
            self.content_layout.removeWidget(self._active_content)
            self._active_content.deleteLater()
            self._active_content = None

    def apply_single_layout(self):
        """Tek ekran: Üst panel (Mission|Map|Telemetry), Alt panel (Logging|Obstacle) — splitter ile boyutlandırılabilir."""
        self._detach_all()

        # Ana dikey splitter
        outer_splitter = QSplitter(Qt.Vertical)
        outer_splitter.setObjectName("splitter_main")

        # ── ÜST PANEL ──
        top_panel = QFrame()
        top_panel.setObjectName("panel_top_container")
        top_panel.setFrameShape(QFrame.StyledPanel)
        top_panel_lay = QVBoxLayout(top_panel)
        top_panel_lay.setContentsMargins(0, 0, 0, 0)
        top_panel_lay.setSpacing(0)

        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.setObjectName("splitter_top")

        # Mission scroll
        mission_scroll = QScrollArea()
        mission_scroll.setWidgetResizable(True)
        mission_scroll.setFrameShape(QFrame.NoFrame)
        mission_scroll.setMinimumWidth(240)
        mission_scroll.setWidget(self.mission_content)

        # Telem scroll
        telem_scroll = QScrollArea()
        telem_scroll.setWidgetResizable(True)
        telem_scroll.setFrameShape(QFrame.NoFrame)
        telem_scroll.setMinimumWidth(240)
        telem_scroll.setWidget(self.telem_content)

        top_splitter.addWidget(mission_scroll)
        top_splitter.addWidget(self.map_content)
        top_splitter.addWidget(telem_scroll)
        top_splitter.setStretchFactor(0, 2)
        top_splitter.setStretchFactor(1, 5)
        top_splitter.setStretchFactor(2, 2)

        top_panel_lay.addWidget(top_splitter)
        outer_splitter.addWidget(top_panel)

        # ── ALT PANEL ──
        bottom_panel = QFrame()
        bottom_panel.setObjectName("panel_bottom_left")
        bottom_panel.setFrameShape(QFrame.StyledPanel)
        bottom_panel_lay = QVBoxLayout(bottom_panel)
        bottom_panel_lay.setContentsMargins(0, 0, 0, 0)
        bottom_panel_lay.setSpacing(0)

        bottom_splitter = QSplitter(Qt.Horizontal)
        bottom_splitter.setObjectName("splitter_bottom")
        bottom_splitter.addWidget(self.logging_content)
        bottom_splitter.addWidget(self.obstacle_content)
        bottom_splitter.setStretchFactor(0, 3)
        bottom_splitter.setStretchFactor(1, 1)

        bottom_panel_lay.addWidget(bottom_splitter)
        outer_splitter.addWidget(bottom_panel)

        outer_splitter.setStretchFactor(0, 3)
        outer_splitter.setStretchFactor(1, 2)

        # Göster
        self.mission_content.show()
        self.map_content.show()
        self.telem_content.show()
        self.logging_content.show()
        self.obstacle_content.show()

        self.content_layout.addWidget(outer_splitter)
        self._active_content = outer_splitter

        self.lbl_video_subtitle.setText("")

    def apply_3screen_layout(self):
        """3-Screen Split — Şartnameye uygun video düzeni."""
        self._detach_all()

        splitter_3 = QSplitter(Qt.Horizontal)
        splitter_3.setObjectName("splitter_3screen")

        # ── SCREEN 1: GCS Interface ──
        screen1 = QFrame()
        screen1.setObjectName("screen_frame_1")
        screen1.setFrameShape(QFrame.StyledPanel)
        s1_lay = QVBoxLayout(screen1)
        s1_lay.setContentsMargins(6, 6, 6, 6)
        s1_lay.setSpacing(4)

        s1_header = QLabel("SCREEN 1: GCS INTERFACE")
        s1_header.setObjectName("screen_header")
        s1_header.setFont(QFont("Segoe UI", 10, QFont.Bold))
        s1_header.setAlignment(Qt.AlignCenter)
        s1_header.setFixedHeight(28)
        s1_lay.addWidget(s1_header)

        s1_scroll = QScrollArea()
        s1_scroll.setWidgetResizable(True)
        s1_scroll.setFrameShape(QFrame.NoFrame)
        s1_inner_widget = QWidget()
        s1_inner = QVBoxLayout(s1_inner_widget)
        s1_inner.setContentsMargins(0, 0, 0, 0)
        s1_inner.setSpacing(6)
        s1_inner.addWidget(self.mission_content)
        s1_inner.addWidget(self.map_content)
        s1_inner.addWidget(self.telem_content)
        s1_scroll.setWidget(s1_inner_widget)
        s1_lay.addWidget(s1_scroll, 1)

        # ── SCREEN 2: Graphs & Data ──
        screen2 = QFrame()
        screen2.setObjectName("screen_frame_2")
        screen2.setFrameShape(QFrame.StyledPanel)
        s2_lay = QVBoxLayout(screen2)
        s2_lay.setContentsMargins(6, 6, 6, 6)
        s2_lay.setSpacing(4)

        s2_header = QLabel("SCREEN 2: GRAPHS & DATA")
        s2_header.setObjectName("screen_header")
        s2_header.setFont(QFont("Segoe UI", 10, QFont.Bold))
        s2_header.setAlignment(Qt.AlignCenter)
        s2_header.setFixedHeight(28)
        s2_lay.addWidget(s2_header)
        s2_lay.addWidget(self.logging_content, 1)

        # ── SCREEN 3: Obstacle Map ──
        screen3 = QFrame()
        screen3.setObjectName("screen_frame_3")
        screen3.setFrameShape(QFrame.StyledPanel)
        s3_lay = QVBoxLayout(screen3)
        s3_lay.setContentsMargins(6, 6, 6, 6)
        s3_lay.setSpacing(4)

        s3_header = QLabel("SCREEN 3: LOCAL OBSTACLE MAP")
        s3_header.setObjectName("screen_header")
        s3_header.setFont(QFont("Segoe UI", 10, QFont.Bold))
        s3_header.setAlignment(Qt.AlignCenter)
        s3_header.setFixedHeight(28)
        s3_lay.addWidget(s3_header)
        s3_lay.addWidget(self.obstacle_content, 1)

        # Göster
        self.mission_content.show()
        self.map_content.show()
        self.telem_content.show()
        self.logging_content.show()
        self.obstacle_content.show()

        splitter_3.addWidget(screen1)
        splitter_3.addWidget(screen2)
        splitter_3.addWidget(screen3)
        splitter_3.setStretchFactor(0, 3)
        splitter_3.setStretchFactor(1, 4)
        splitter_3.setStretchFactor(2, 3)

        self.content_layout.addWidget(splitter_3)
        self._active_content = splitter_3

        self.lbl_video_subtitle.setText(
            "Screen 1: GCS Interface  |  Screen 2: Graphs & Data  |  Screen 3: Obstacle Map"
        )

    # ═══════════════════════════════════════════════════════
    # YARDIMCI: Telemetri bölüm başlığı
    # ═══════════════════════════════════════════════════════
    def _add_telem_section(self, title):
        lbl = QLabel(title)
        lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl.setObjectName("telem_section_header")
        self.telem_layout.addWidget(lbl)

    def _add_telem_row(self, key, label_text):
        row = QHBoxLayout()
        row.setContentsMargins(6, 2, 6, 2)
        lbl_name = QLabel(label_text)
        lbl_name.setFont(QFont("Segoe UI", 10))
        lbl_name.setObjectName("telem_label")
        lbl_value = QLabel("—")
        lbl_value.setFont(QFont("JetBrains Mono", 11, QFont.Bold))
        lbl_value.setObjectName("telem_value")
        lbl_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(lbl_name)
        row.addStretch()
        row.addWidget(lbl_value)
        self.telem_layout.addLayout(row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setObjectName("telem_separator")
        self.telem_layout.addWidget(sep)

        self.telem_labels[key] = lbl_value

    def retranslateUi(self, MainWindow):
        """Metin çevirileri (pyuic5 uyumlu)"""
        pass
