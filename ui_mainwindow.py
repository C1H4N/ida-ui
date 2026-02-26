# -*- coding: utf-8 -*-
"""
ui_mainwindow.py — pyuic5 ile oluşturulmuş gibi UI tanımı.
Qt Designer'dan "pyuic5 gcs_mainwindow.ui -o ui_mainwindow.py" ile üretilir.

USV Ground Control Station — Teknofest
"""

from PyQt5.QtCore import QMetaObject, Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QGroupBox,
    QFrame, QSplitter, QSizePolicy, QSpacerItem, QScrollArea,
    QStatusBar
)

# Özel widget import'ları (Qt Designer'da "Promote" edilir)
from custom_widgets import NavigationMapWidget, ObstacleMapWidget


class Ui_MainWindow(object):
    """
    Bu sınıf pyuic5 çıktısını taklit eder.
    setupUi() tüm widget'ları oluşturur ve yerleştirir.
    retranslateUi() metin çevirilerini ayarlar.
    """

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1600, 950)
        MainWindow.setMinimumSize(QSize(1200, 700))
        MainWindow.setWindowTitle("USV Ground Control Station — Teknofest")

        # ═══════════════════════════════════════════════════
        # Central Widget
        # ═══════════════════════════════════════════════════
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background-color: #020617;")
        MainWindow.setCentralWidget(self.centralwidget)

        self.main_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(8, 8, 8, 4)
        self.main_layout.setSpacing(6)

        # ═══════════════════════════════════════════════════
        # HEADER BAR
        # ═══════════════════════════════════════════════════
        self._build_header()
        self.main_layout.addWidget(self.header_frame)

        # ═══════════════════════════════════════════════════
        # FAILSAFE ALERT BANNER (header altında, tam genişlik)
        # ═══════════════════════════════════════════════════
        self.frame_failsafe = QFrame()
        self.frame_failsafe.setObjectName("frame_failsafe")
        self.frame_failsafe.setFixedHeight(36)
        fs_layout = QHBoxLayout(self.frame_failsafe)
        fs_layout.setContentsMargins(12, 4, 12, 4)
        self.lbl_failsafe = QLabel("⚠  LINK LOST — FAILSAFE ACTIVE  ⚠")
        self.lbl_failsafe.setFont(QFont("Consolas", 12, QFont.Bold))
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
        # CONTENT AREA — Layout switching
        # ═══════════════════════════════════════════════════
        self.content_container = QWidget()
        self.content_container.setObjectName("content_container")
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(6)
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
    # HEADER
    # ═══════════════════════════════════════════════════════
    def _build_header(self):
        self.header_frame = QFrame()
        self.header_frame.setObjectName("header_frame")
        self.header_frame.setFrameShape(QFrame.StyledPanel)
        self.header_frame.setFixedHeight(56)
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(12, 4, 12, 4)

        # Başlık
        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)
        self.lbl_title = QLabel("USV Ground Control Station")
        self.lbl_title.setObjectName("lbl_title")
        self.lbl_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.lbl_subtitle = QLabel("Autonomous Navigation Monitor")
        self.lbl_subtitle.setObjectName("lbl_subtitle")
        self.lbl_subtitle.setFont(QFont("Consolas", 9))
        title_layout.addWidget(self.lbl_title)
        title_layout.addWidget(self.lbl_subtitle)
        header_layout.addLayout(title_layout)

        header_layout.addStretch()

        # Mission Progress göstergesi
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(1)
        self.lbl_mission_progress = QLabel("WP 0/0 — %0")
        self.lbl_mission_progress.setObjectName("lbl_mission_progress")
        self.lbl_mission_progress.setFont(QFont("Consolas", 9, QFont.Bold))
        self.lbl_mission_progress.setAlignment(Qt.AlignCenter)
        from PyQt5.QtWidgets import QProgressBar
        self.progress_mission = QProgressBar()
        self.progress_mission.setObjectName("progress_mission")
        self.progress_mission.setFixedSize(160, 12)
        self.progress_mission.setTextVisible(False)
        self.progress_mission.setRange(0, 100)
        self.progress_mission.setValue(0)
        progress_layout.addWidget(self.lbl_mission_progress)
        progress_layout.addWidget(self.progress_mission)
        header_layout.addLayout(progress_layout)

        # Mission State göstergesi
        self.frame_mission_state = QFrame()
        self.frame_mission_state.setObjectName("frame_mission_state")
        self.frame_mission_state.setFixedSize(180, 44)
        ms_layout = QVBoxLayout(self.frame_mission_state)
        ms_layout.setContentsMargins(10, 2, 10, 2)
        ms_layout.setSpacing(0)
        self.lbl_mission_state_label = QLabel("Mission State")
        self.lbl_mission_state_label.setFont(QFont("Consolas", 8))
        self.lbl_mission_state_label.setObjectName("lbl_mission_state_label")
        self.lbl_mission_state = QLabel("STANDBY")
        self.lbl_mission_state.setObjectName("lbl_mission_state")
        self.lbl_mission_state.setFont(QFont("Consolas", 12, QFont.Bold))
        ms_layout.addWidget(self.lbl_mission_state_label)
        ms_layout.addWidget(self.lbl_mission_state)
        header_layout.addWidget(self.frame_mission_state)

        # Start Mission butonu
        self.btn_start_mission = QPushButton("▶  Start Mission")
        self.btn_start_mission.setObjectName("btn_start_mission")
        self.btn_start_mission.setFixedSize(150, 36)
        self.btn_start_mission.setFont(QFont("Segoe UI", 10, QFont.Bold))
        header_layout.addWidget(self.btn_start_mission)

        # Power durumu
        self.lbl_power_status = QLabel("⏻ ACTIVE")
        self.lbl_power_status.setObjectName("lbl_power_status")
        self.lbl_power_status.setFont(QFont("Consolas", 10, QFont.Bold))
        header_layout.addWidget(self.lbl_power_status)

    # ═══════════════════════════════════════════════════════
    # VIDEO LAYOUT SELECTOR BAR
    # ═══════════════════════════════════════════════════════
    def _build_video_layout_bar(self):
        self.frame_video_layout = QFrame()
        self.frame_video_layout.setObjectName("frame_video_layout")
        self.frame_video_layout.setFixedHeight(36)
        vl_layout = QHBoxLayout(self.frame_video_layout)
        vl_layout.setContentsMargins(12, 4, 12, 4)
        self.lbl_video_icon = QLabel("🖥")
        self.lbl_video_layout_title = QLabel("Video Layout")
        self.lbl_video_layout_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        vl_layout.addWidget(self.lbl_video_icon)
        vl_layout.addWidget(self.lbl_video_layout_title)

        self.lbl_video_subtitle = QLabel("")
        self.lbl_video_subtitle.setObjectName("lbl_video_subtitle")
        self.lbl_video_subtitle.setFont(QFont("Consolas", 8))
        vl_layout.addWidget(self.lbl_video_subtitle)

        vl_layout.addStretch()
        self.btn_single_screen = QPushButton("Single Screen")
        self.btn_single_screen.setObjectName("btn_single_screen")
        self.btn_single_screen.setCheckable(True)
        self.btn_single_screen.setChecked(True)
        self.btn_single_screen.setFixedSize(120, 26)
        self.btn_single_screen.setFont(QFont("Consolas", 9))
        self.btn_3screen = QPushButton("3-Screen Split")
        self.btn_3screen.setObjectName("btn_3screen")
        self.btn_3screen.setCheckable(True)
        self.btn_3screen.setFixedSize(120, 26)
        self.btn_3screen.setFont(QFont("Consolas", 9))
        vl_layout.addWidget(self.btn_single_screen)
        vl_layout.addWidget(self.btn_3screen)

    # ═══════════════════════════════════════════════════════
    # TÜM İÇ WIDGET'LARI OLUŞTUR
    # ═══════════════════════════════════════════════════════
    def _create_all_inner_widgets(self):
        """Tüm iç widget'ları oluştur (layout-bağımsız)."""

        # ── MISSION SETUP iç widget'ları ────────────────
        self.mission_content = QWidget()
        mission_lay = QVBoxLayout(self.mission_content)
        mission_lay.setContentsMargins(8, 4, 8, 4)
        mission_lay.setSpacing(4)

        lbl_mission = QLabel("MISSION SETUP")
        lbl_mission.setObjectName("section_header")
        lbl_mission.setFont(QFont("Segoe UI", 10, QFont.Bold))
        mission_lay.addWidget(lbl_mission)

        # Waypoint giriş alanları
        self.wp_entries = []
        for i in range(4):
            wp_frame = QFrame()
            wp_frame.setObjectName("wp_group")
            wp_grid = QGridLayout(wp_frame)
            wp_grid.setContentsMargins(4, 14, 4, 4)
            wp_grid.setSpacing(4)

            lbl_wp = QLabel(f"WP{i+1}")
            lbl_wp.setFont(QFont("Consolas", 9, QFont.Bold))
            lbl_wp.setStyleSheet("color: #64748b;")
            wp_grid.addWidget(lbl_wp, 0, 0, 1, 2)

            lbl_lat = QLabel("Latitude")
            lbl_lat.setFont(QFont("Consolas", 8))
            lbl_lat.setStyleSheet("color: #64748b;")
            edit_lat = QLineEdit()
            edit_lat.setObjectName(f"edit_wp{i+1}_lat")
            edit_lat.setFont(QFont("Consolas", 9))
            edit_lat.setPlaceholderText("00.0000000")

            lbl_lon = QLabel("Longitude")
            lbl_lon.setFont(QFont("Consolas", 8))
            lbl_lon.setStyleSheet("color: #64748b;")
            edit_lon = QLineEdit()
            edit_lon.setObjectName(f"edit_wp{i+1}_lon")
            edit_lon.setFont(QFont("Consolas", 9))
            edit_lon.setPlaceholderText("00.0000000")

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

        lbl_target = QLabel("Target Color")
        lbl_target.setFont(QFont("Consolas", 9))
        lbl_target.setStyleSheet("color: #94a3b8;")
        self.combo_target_color = QComboBox()
        self.combo_target_color.setObjectName("combo_target_color")
        self.combo_target_color.setFont(QFont("Consolas", 9))
        self.combo_target_color.addItems(["Red", "Green", "Blue", "Yellow"])
        mission_lay.addWidget(lbl_target)
        mission_lay.addWidget(self.combo_target_color)

        # Upload Status
        self.lbl_upload_status = QLabel("")
        self.lbl_upload_status.setObjectName("lbl_upload_status")
        self.lbl_upload_status.setFont(QFont("Consolas", 8))
        self.lbl_upload_status.setWordWrap(True)
        self.lbl_upload_status.hide()
        mission_lay.addWidget(self.lbl_upload_status)

        # Butonlar
        self.btn_upload_mission = QPushButton("⬆  Upload Mission")
        self.btn_upload_mission.setObjectName("btn_upload_mission")
        self.btn_upload_mission.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.btn_upload_mission.setFixedHeight(32)

        self.btn_clear_waypoints = QPushButton("🗑  Clear Waypoints")
        self.btn_clear_waypoints.setObjectName("btn_clear_waypoints")
        self.btn_clear_waypoints.setFont(QFont("Segoe UI", 9))
        self.btn_clear_waypoints.setFixedHeight(32)

        mission_lay.addWidget(self.btn_upload_mission)
        mission_lay.addWidget(self.btn_clear_waypoints)
        mission_lay.addStretch()

        # ── NAVIGATION MAP ──────────────────────────────
        self.navigation_map = NavigationMapWidget()
        self.navigation_map.setObjectName("navigation_map")

        self.map_content = QWidget()
        map_lay = QVBoxLayout(self.map_content)
        map_lay.setContentsMargins(8, 4, 8, 4)
        map_lay.setSpacing(4)

        map_header = QHBoxLayout()
        self.lbl_map_indicator = QLabel("")
        self.lbl_map_indicator.setFixedSize(4, 16)
        self.lbl_map_indicator.setObjectName("accent_bar")
        self.lbl_map_title = QLabel("NAVIGATION MAP")
        self.lbl_map_title.setObjectName("section_header")
        self.lbl_map_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        map_header.addWidget(self.lbl_map_indicator)
        map_header.addWidget(self.lbl_map_title)
        map_header.addStretch()
        map_lay.addLayout(map_header)
        map_lay.addWidget(self.navigation_map, 1)

        # ── TELEMETRY ────────────────────────────────────
        self.telem_content = QWidget()
        telem_lay = QVBoxLayout(self.telem_content)
        telem_lay.setContentsMargins(8, 4, 8, 4)
        telem_lay.setSpacing(2)

        lbl_telem_title = QLabel("TELEMETRY")
        lbl_telem_title.setObjectName("section_header")
        lbl_telem_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        telem_lay.addWidget(lbl_telem_title)

        telem_scroll = QScrollArea()
        telem_scroll.setWidgetResizable(True)
        telem_scroll.setFrameShape(QFrame.NoFrame)
        telem_scroll_content = QWidget()
        self.telem_layout = QVBoxLayout(telem_scroll_content)
        self.telem_layout.setContentsMargins(0, 0, 0, 0)
        self.telem_layout.setSpacing(2)

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

        # Target Detection bölümü
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

        # Vehicle Mode kutusu + Mod geçiş butonu
        self.frame_vehicle_mode = QFrame()
        self.frame_vehicle_mode.setObjectName("frame_vehicle_mode")
        self.frame_vehicle_mode.setFixedHeight(44)
        vm_layout = QVBoxLayout(self.frame_vehicle_mode)
        vm_layout.setContentsMargins(8, 4, 8, 4)
        vm_layout.setSpacing(0)
        lbl_vm = QLabel("Vehicle Mode")
        lbl_vm.setFont(QFont("Consolas", 8))
        self.lbl_vehicle_mode = QLabel("MANUAL")
        self.lbl_vehicle_mode.setObjectName("lbl_vehicle_mode")
        self.lbl_vehicle_mode.setFont(QFont("Consolas", 14, QFont.Bold))
        vm_layout.addWidget(lbl_vm)
        vm_layout.addWidget(self.lbl_vehicle_mode)
        telem_lay.addWidget(self.frame_vehicle_mode)

        # Mod değiştirme butonu
        self.btn_mode_switch = QPushButton("⇄  Switch to MISSION")
        self.btn_mode_switch.setObjectName("btn_mode_switch")
        self.btn_mode_switch.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.btn_mode_switch.setFixedHeight(32)
        telem_lay.addWidget(self.btn_mode_switch)

        # Power Cut uyarısı
        self.frame_power_cut = QFrame()
        self.frame_power_cut.setObjectName("frame_power_cut")
        self.frame_power_cut.setFixedHeight(28)
        pc_layout = QHBoxLayout(self.frame_power_cut)
        pc_layout.setContentsMargins(8, 2, 8, 2)
        self.lbl_power_cut = QLabel("⚠ POWER CUT ACTIVE")
        self.lbl_power_cut.setFont(QFont("Consolas", 9, QFont.Bold))
        pc_layout.addWidget(self.lbl_power_cut)
        self.frame_power_cut.hide()
        telem_lay.addWidget(self.frame_power_cut)

        # E-STOP butonu
        self.btn_estop = QPushButton("⛔  E-STOP")
        self.btn_estop.setObjectName("btn_estop")
        self.btn_estop.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_estop.setFixedHeight(44)
        telem_lay.addWidget(self.btn_estop)

        # ── DATA LOGGING & GRAPHS ────────────────────────
        self.logging_content = QWidget()
        dl_lay = QVBoxLayout(self.logging_content)
        dl_lay.setContentsMargins(8, 8, 8, 8)
        dl_lay.setSpacing(6)

        lbl_dl_title = QLabel("DATA LOGGING & ANALYSIS")
        lbl_dl_title.setObjectName("section_header")
        lbl_dl_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        dl_lay.addWidget(lbl_dl_title)

        # Recording status bar
        rec_layout = QHBoxLayout()
        self.lbl_rec_logging = QLabel("● Logging")
        self.lbl_rec_logging.setFont(QFont("Consolas", 8))
        self.lbl_rec_logging.setObjectName("rec_inactive")
        self.lbl_rec_csv = QLabel("● CSV (≥1Hz)")
        self.lbl_rec_csv.setFont(QFont("Consolas", 8))
        self.lbl_rec_csv.setObjectName("rec_inactive")
        self.lbl_rec_autonomy = QLabel("● Autonomy")
        self.lbl_rec_autonomy.setFont(QFont("Consolas", 8))
        self.lbl_rec_autonomy.setObjectName("rec_inactive")
        self.lbl_rec_map = QLabel("● Map")
        self.lbl_rec_map.setFont(QFont("Consolas", 8))
        self.lbl_rec_map.setObjectName("rec_inactive")

        rec_layout.addWidget(QLabel("💾"))
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
        self.lbl_utc_label.setFont(QFont("Consolas", 8))
        self.lbl_utc_time = QLabel("00:00:00 UTC")
        self.lbl_utc_time.setFont(QFont("Consolas", 9))
        self.lbl_utc_time.setObjectName("lbl_utc_time")
        rec_layout.addWidget(self.lbl_utc_label)
        rec_layout.addWidget(self.lbl_utc_time)

        sep_v2 = QFrame()
        sep_v2.setFrameShape(QFrame.VLine)
        sep_v2.setObjectName("separator")
        rec_layout.addWidget(sep_v2)

        lbl_timer_label = QLabel("Timer")
        lbl_timer_label.setFont(QFont("Consolas", 8))
        self.lbl_competition_timer = QLabel("20:00")
        self.lbl_competition_timer.setObjectName("lbl_competition_timer")
        self.lbl_competition_timer.setFont(QFont("Consolas", 16, QFont.Bold))
        rec_layout.addWidget(lbl_timer_label)
        rec_layout.addWidget(self.lbl_competition_timer)

        dl_lay.addLayout(rec_layout)

        # Grafik Placeholder'ları
        self.graph_layout = QHBoxLayout()
        self.graph_layout.setSpacing(6)

        self.frame_graph_speed = QFrame()
        self.frame_graph_speed.setObjectName("graph_frame")
        self.frame_graph_speed.setFrameShape(QFrame.StyledPanel)
        speed_lay = QVBoxLayout(self.frame_graph_speed)
        speed_lay.setContentsMargins(6, 6, 6, 6)
        self.lbl_graph_speed_title = QLabel("Speed vs Target")
        self.lbl_graph_speed_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        speed_lay.addWidget(self.lbl_graph_speed_title)
        self.graph_speed_placeholder = QWidget()
        self.graph_speed_placeholder.setObjectName("graph_speed_placeholder")
        self.graph_speed_placeholder.setMinimumHeight(120)
        speed_lay.addWidget(self.graph_speed_placeholder, 1)
        self.graph_layout.addWidget(self.frame_graph_speed)

        self.frame_graph_heading = QFrame()
        self.frame_graph_heading.setObjectName("graph_frame")
        self.frame_graph_heading.setFrameShape(QFrame.StyledPanel)
        heading_lay = QVBoxLayout(self.frame_graph_heading)
        heading_lay.setContentsMargins(6, 6, 6, 6)
        self.lbl_graph_heading_title = QLabel("Heading vs Target")
        self.lbl_graph_heading_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        heading_lay.addWidget(self.lbl_graph_heading_title)
        self.graph_heading_placeholder = QWidget()
        self.graph_heading_placeholder.setObjectName("graph_heading_placeholder")
        self.graph_heading_placeholder.setMinimumHeight(120)
        heading_lay.addWidget(self.graph_heading_placeholder, 1)
        self.graph_layout.addWidget(self.frame_graph_heading)

        self.frame_graph_thruster = QFrame()
        self.frame_graph_thruster.setObjectName("graph_frame")
        self.frame_graph_thruster.setFrameShape(QFrame.StyledPanel)
        thruster_lay = QVBoxLayout(self.frame_graph_thruster)
        thruster_lay.setContentsMargins(6, 6, 6, 6)
        self.lbl_graph_thruster_title = QLabel("Thruster Commands")
        self.lbl_graph_thruster_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        thruster_lay.addWidget(self.lbl_graph_thruster_title)
        self.graph_thruster_placeholder = QWidget()
        self.graph_thruster_placeholder.setObjectName("graph_thruster_placeholder")
        self.graph_thruster_placeholder.setMinimumHeight(120)
        thruster_lay.addWidget(self.graph_thruster_placeholder, 1)
        self.graph_layout.addWidget(self.frame_graph_thruster)

        dl_lay.addLayout(self.graph_layout)

        # ── OBSTACLE MAP ─────────────────────────────────
        self.obstacle_content = QWidget()
        obs_lay = QVBoxLayout(self.obstacle_content)
        obs_lay.setContentsMargins(8, 8, 8, 8)
        obs_lay.setSpacing(4)

        lbl_obs_title = QLabel("LOCAL OBSTACLE / COST MAP")
        lbl_obs_title.setObjectName("section_header")
        lbl_obs_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        obs_lay.addWidget(lbl_obs_title)

        self.lbl_obstacle_subtitle = QLabel("Live Sensor Data — 10m Range")
        self.lbl_obstacle_subtitle.setFont(QFont("Consolas", 8))
        self.lbl_obstacle_subtitle.setStyleSheet("color: #64748b;")
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

        # Ana dikey splitter (üst / alt)
        outer_splitter = QSplitter(Qt.Vertical)
        outer_splitter.setObjectName("splitter_main")

        # ── ÜST PANEL ─ yuvarlatılmış container içinde splitter ──
        top_panel = QFrame()
        top_panel.setObjectName("panel_top_container")
        top_panel.setFrameShape(QFrame.StyledPanel)
        top_panel_lay = QVBoxLayout(top_panel)
        top_panel_lay.setContentsMargins(0, 0, 0, 0)
        top_panel_lay.setSpacing(0)

        # Üst yatay splitter
        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.setObjectName("splitter_top")

        # Mission scroll
        mission_scroll = QScrollArea()
        mission_scroll.setWidgetResizable(True)
        mission_scroll.setFrameShape(QFrame.NoFrame)
        mission_scroll.setMinimumWidth(200)
        mission_scroll.setWidget(self.mission_content)

        # Telem scroll
        telem_scroll = QScrollArea()
        telem_scroll.setWidgetResizable(True)
        telem_scroll.setFrameShape(QFrame.NoFrame)
        telem_scroll.setMinimumWidth(200)
        telem_scroll.setWidget(self.telem_content)

        top_splitter.addWidget(mission_scroll)
        top_splitter.addWidget(self.map_content)
        top_splitter.addWidget(telem_scroll)
        top_splitter.setStretchFactor(0, 2)
        top_splitter.setStretchFactor(1, 5)
        top_splitter.setStretchFactor(2, 2)

        top_panel_lay.addWidget(top_splitter)
        outer_splitter.addWidget(top_panel)

        # ── ALT PANEL ─ splitter ile boyutlandırılabilir ──
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

        # Panelleri göster
        self.mission_content.show()
        self.map_content.show()
        self.telem_content.show()
        self.logging_content.show()
        self.obstacle_content.show()

        self.content_layout.addWidget(outer_splitter)
        self._active_content = outer_splitter

        self.lbl_video_subtitle.setText("")

    def apply_3screen_layout(self):
        """3-Screen Split — Şartnameye uygun video düzeni, splitter ile boyutlandırılabilir."""
        self._detach_all()

        # Ana yatay splitter — 3 ekran
        splitter_3 = QSplitter(Qt.Horizontal)
        splitter_3.setObjectName("splitter_3screen")

        # ── SCREEN 1: GCS Interface ──────────────────
        screen1 = QFrame()
        screen1.setObjectName("screen_frame_1")
        screen1.setFrameShape(QFrame.StyledPanel)
        s1_lay = QVBoxLayout(screen1)
        s1_lay.setContentsMargins(4, 4, 4, 4)
        s1_lay.setSpacing(2)

        s1_header = QLabel("SCREEN 1: GCS INTERFACE")
        s1_header.setObjectName("screen_header")
        s1_header.setFont(QFont("Consolas", 9, QFont.Bold))
        s1_header.setAlignment(Qt.AlignCenter)
        s1_header.setFixedHeight(22)
        s1_lay.addWidget(s1_header)

        s1_scroll = QScrollArea()
        s1_scroll.setWidgetResizable(True)
        s1_scroll.setFrameShape(QFrame.NoFrame)
        s1_inner_widget = QWidget()
        s1_inner = QVBoxLayout(s1_inner_widget)
        s1_inner.setContentsMargins(0, 0, 0, 0)
        s1_inner.setSpacing(4)
        s1_inner.addWidget(self.mission_content)
        s1_inner.addWidget(self.map_content)
        s1_inner.addWidget(self.telem_content)
        s1_scroll.setWidget(s1_inner_widget)
        s1_lay.addWidget(s1_scroll, 1)

        # ── SCREEN 2: Graphs & Data ──────────────────
        screen2 = QFrame()
        screen2.setObjectName("screen_frame_2")
        screen2.setFrameShape(QFrame.StyledPanel)
        s2_lay = QVBoxLayout(screen2)
        s2_lay.setContentsMargins(4, 4, 4, 4)
        s2_lay.setSpacing(2)

        s2_header = QLabel("SCREEN 2: GRAPHS & DATA")
        s2_header.setObjectName("screen_header")
        s2_header.setFont(QFont("Consolas", 9, QFont.Bold))
        s2_header.setAlignment(Qt.AlignCenter)
        s2_header.setFixedHeight(22)
        s2_lay.addWidget(s2_header)
        s2_lay.addWidget(self.logging_content, 1)

        # ── SCREEN 3: Obstacle/Cost Map ──────────────
        screen3 = QFrame()
        screen3.setObjectName("screen_frame_3")
        screen3.setFrameShape(QFrame.StyledPanel)
        s3_lay = QVBoxLayout(screen3)
        s3_lay.setContentsMargins(4, 4, 4, 4)
        s3_lay.setSpacing(2)

        s3_header = QLabel("SCREEN 3: LOCAL OBSTACLE MAP")
        s3_header.setObjectName("screen_header")
        s3_header.setFont(QFont("Consolas", 9, QFont.Bold))
        s3_header.setAlignment(Qt.AlignCenter)
        s3_header.setFixedHeight(22)
        s3_lay.addWidget(s3_header)
        s3_lay.addWidget(self.obstacle_content, 1)

        # Panelleri göster
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
        lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
        lbl.setObjectName("telem_section_header")
        self.telem_layout.addWidget(lbl)

    def _add_telem_row(self, key, label_text):
        row = QHBoxLayout()
        row.setContentsMargins(4, 0, 4, 0)
        lbl_name = QLabel(label_text)
        lbl_name.setFont(QFont("Consolas", 8))
        lbl_name.setObjectName("telem_label")
        lbl_value = QLabel("—")
        lbl_value.setFont(QFont("Consolas", 9))
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
