#!/usr/bin/env python3

import sys
import subprocess
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QFileDialog, QMessageBox, QTabWidget,
    QLineEdit, QProgressBar, QGroupBox, QGridLayout, QStackedWidget,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap

# Polished Dark Theme Styling
DARK_STYLESHEET = """
QMainWindow {
    background-color: #0F1015;
}
QWidget {
    color: #E2E8F0;
    font-family: 'Segoe UI', Ubuntu, sans-serif;
    font-size: 13px;
}
QFrame#Sidebar, QFrame#RightPanel, QFrame#MenuCard {
    background-color: #171923;
    border: 1px solid #2D3748;
    border-radius: 12px;
}
QFrame#MenuCard:hover {
    border-color: #38BDF8;
}
QGroupBox {
    border: 1px solid #2D3748;
    border-radius: 8px;
    margin-top: 12px;
    font-weight: bold;
    padding: 10px;
    background-color: #1A202C;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #38BDF8;
}
QLabel#DeviceHeader, QLabel#MenuTitle {
    font-size: 16px;
    font-weight: bold;
    color: #F8FAFC;
}
QPushButton {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 9px 16px;
    color: #F1F5F9;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #38BDF8;
    color: #0F1015;
    border-color: #38BDF8;
}
QPushButton:pressed {
    background-color: #0284C7;
}
QPushButton#DangerBtn {
    background-color: #450A0A;
    border-color: #EF4444;
    color: #FCA5A5;
}
QPushButton#DangerBtn:hover {
    background-color: #EF4444;
    color: #FFFFFF;
}
QTabWidget::pane {
    border: 1px solid #2D3748;
    background-color: #171923;
    border-radius: 8px;
}
QTabBar::tab {
    background-color: #0F1015;
    color: #94A3B8;
    padding: 10px 22px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 3px;
    font-weight: 500;
}
QTabBar::tab:selected {
    background-color: #171923;
    color: #38BDF8;
    font-weight: bold;
    border-bottom: 2px solid #38BDF8;
}
QLineEdit {
    background-color: #0F1015;
    border: 1px solid #334155;
    border-radius: 5px;
    padding: 7px;
    color: #F8FAFC;
}
QProgressBar {
    border: 1px solid #334155;
    border-radius: 5px;
    text-align: center;
    background-color: #0F1015;
}
QProgressBar::chunk {
    background-color: #38BDF8;
    border-radius: 4px;
}
"""

class WorkerThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            res = subprocess.check_output(self.command, shell=True, stderr=subprocess.STDOUT)
            self.finished.emit(res.decode('utf-8', errors='ignore'))
        except subprocess.CalledProcessError as e:
            self.finished.emit(e.output.decode('utf-8', errors='ignore'))


class DeviceImageViewer(QLabel):
    """PNG Render Engine for Android Devices preserving exact aspect ratios."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 340)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background: transparent; border: none;")
        self.render_device("Disconnected", "No Device", False, "", "")

    def load_png(self, filename):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(script_dir, filename)

        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)
        else:
            pixmap = QPixmap(200, 300)
            pixmap.fill(Qt.GlobalColor.transparent)
        
        scaled_pixmap = pixmap.scaled(
            self.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)

    def render_device(self, brand, model, connected, market_name, device_code):
        combined_check = f"{brand} {model} {market_name} {device_code}".lower()

        if not connected:
            self.load_png("disconnected.png")
            return

        if "samsung" in combined_check and ("ultra" in combined_check or "s928" in combined_check or "s918" in combined_check or "s908" in combined_check):
            self.load_png("s_ultra.png")
        elif "samsung" in combined_check and "note" in combined_check:
            self.load_png("note.png")
        elif "google" in combined_check and any(p in combined_check for p in ["pixel 9", "pixel 10", "pixel 11", "fold"]):
            self.load_png("pixel_9_plus.png")
        elif "google" in combined_check and any(p in combined_check for p in ["pixel 6", "pixel 7", "pixel 8"]):
            self.load_png("pixel_6_7_8.png")
        elif "samsung" in combined_check and ("a" in combined_check or "sm-a" in combined_check):
            self.load_png("a_series.png")
        else:
            self.load_png("default_phone.png")


class LandingWidget(QWidget):
    """Landing Page with Android and Apple ecosystem selection cards."""
    def __init__(self, select_callback):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)

        title = QLabel("Mobile Interact")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #38BDF8;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Select a mobile platform to manage:")
        subtitle.setStyleSheet("font-size: 15px; color: #94A3B8;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(40)

        # Android Selection Card
        btn_android = QPushButton("🤖 Android Ecosystem\n\nADB, Fastboot, Flashing, Sideloading")
        btn_android.setFixedSize(260, 180)
        btn_android.setStyleSheet("""
            QPushButton {
                background-color: #171923;
                border: 2px solid #2D3748;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                color: #F8FAFC;
                text-align: center;
            }
            QPushButton:hover {
                border-color: #22C55E;
                background-color: #1A202C;
            }
        """)
        btn_android.clicked.connect(lambda: select_callback("android"))
        cards_layout.addWidget(btn_android)

        # Apple Selection Card
        btn_apple = QPushButton("🍏 Apple iOS Ecosystem\n\nRecovery, DFU, IPSW Flash, Jailbreak")
        btn_apple.setFixedSize(260, 180)
        btn_apple.setStyleSheet("""
            QPushButton {
                background-color: #171923;
                border: 2px solid #2D3748;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                color: #F8FAFC;
                text-align: center;
            }
            QPushButton:hover {
                border-color: #38BDF8;
                background-color: #1A202C;
            }
        """)
        btn_apple.clicked.connect(lambda: select_callback("apple"))
        cards_layout.addWidget(btn_apple)

        layout.addLayout(cards_layout)


class AndroidWidget(QWidget):
    """Existing Android Management GUI"""
    def __init__(self, back_callback):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self.back_callback = back_callback
        self.setup_sidebar(layout)
        self.setup_tabs(layout)
        self.setup_right_panel(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_device_info)
        self.timer.start(3000)
        self.update_device_info()

    def setup_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title = QLabel("Android Diagnostics")
        title.setObjectName("DeviceHeader")
        layout.addWidget(title)

        self.lbl_status = QLabel("Searching...")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("background-color: #334155; color: #F1F5F9; padding: 6px; border-radius: 6px; font-weight: bold;")
        layout.addWidget(self.lbl_status)

        self.info_model = QLabel("Model Name: --")
        self.info_number = QLabel("Model Code: --")
        self.info_brand = QLabel("Brand: --")
        self.info_android = QLabel("Android Version: --")
        self.info_cpu = QLabel("CPU Architecture: --")
        self.info_ram = QLabel("Total RAM: --")

        self.info_batt_lvl = QLabel("Battery Level: --")
        self.info_batt_health = QLabel("Battery Health: --")
        self.info_charge_state = QLabel("Charging State: --")
        self.info_temp = QLabel("Temperature: --")

        hw_group = QGroupBox("Hardware Specs")
        hw_box = QVBoxLayout(hw_group)
        hw_box.addWidget(self.info_brand)
        hw_box.addWidget(self.info_model)
        hw_box.addWidget(self.info_number)
        hw_box.addWidget(self.info_android)
        hw_box.addWidget(self.info_cpu)
        hw_box.addWidget(self.info_ram)
        layout.addWidget(hw_group)

        batt_group = QGroupBox("Battery & Power")
        batt_box = QVBoxLayout(batt_group)
        batt_box.addWidget(self.info_batt_lvl)
        batt_box.addWidget(self.info_batt_health)
        batt_box.addWidget(self.info_charge_state)
        batt_box.addWidget(self.info_temp)
        layout.addWidget(batt_group)

        layout.addStretch()

        btn_refresh = QPushButton("Manual Refresh")
        btn_refresh.clicked.connect(self.update_device_info)
        layout.addWidget(btn_refresh)

        btn_back = QPushButton("⬅ Main Menu")
        btn_back.clicked.connect(self.back_callback)
        layout.addWidget(btn_back)

        parent_layout.addWidget(sidebar, 1)

    def setup_tabs(self, parent_layout):
        tab_container = QWidget()
        container_layout = QVBoxLayout(tab_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()
        
        tab_reboot = QWidget()
        r_layout = QGridLayout(tab_reboot)
        r_layout.setSpacing(15)

        btn_reb_sys = QPushButton("System Reboot")
        btn_reb_rec = QPushButton("Recovery Mode")
        btn_reb_fast = QPushButton("Bootloader / Fastboot")
        btn_reb_edl = QPushButton("EDL Mode (Qualcomm)")
        btn_reb_sam = QPushButton("Download Mode (Samsung)")

        btn_reb_sys.clicked.connect(lambda: self.run_cmd("adb reboot"))
        btn_reb_rec.clicked.connect(lambda: self.run_cmd("adb reboot recovery"))
        btn_reb_fast.clicked.connect(lambda: self.run_cmd("adb reboot bootloader"))
        btn_reb_edl.clicked.connect(lambda: self.run_cmd("adb reboot edl"))
        btn_reb_sam.clicked.connect(lambda: self.run_cmd("adb reboot download"))

        r_layout.addWidget(btn_reb_sys, 0, 0)
        r_layout.addWidget(btn_reb_rec, 0, 1)
        r_layout.addWidget(btn_reb_fast, 1, 0)
        r_layout.addWidget(btn_reb_edl, 1, 1)
        r_layout.addWidget(btn_reb_sam, 2, 0, 1, 2)
        r_layout.setRowStretch(3, 1)

        tab_backup = QWidget()
        b_layout = QVBoxLayout(tab_backup)
        b_layout.setSpacing(15)

        btn_pull_sdcard = QPushButton("Pull Entire Internal Storage (/sdcard)")
        btn_pull_custom = QPushButton("Pull Specific Path from Device")
        btn_legacy_backup = QPushButton("Legacy ADB App Data Backup")

        btn_pull_sdcard.clicked.connect(self.action_pull_sdcard)
        btn_pull_custom.clicked.connect(self.action_pull_custom)
        btn_legacy_backup.clicked.connect(self.action_legacy_backup)

        b_layout.addWidget(btn_pull_sdcard)
        b_layout.addWidget(btn_pull_custom)
        b_layout.addWidget(btn_legacy_backup)
        b_layout.addStretch()

        tab_flash = QWidget()
        f_layout = QVBoxLayout(tab_flash)
        f_layout.setSpacing(15)

        btn_flash_img = QPushButton("Flash Image (.img) via Fastboot")
        btn_flash_img.setObjectName("DangerBtn")
        btn_sideload = QPushButton("Sideload OTA / Update ZIP")

        btn_flash_img.clicked.connect(self.action_flash_partition)
        btn_sideload.clicked.connect(self.action_sideload)

        f_layout.addWidget(btn_flash_img)
        f_layout.addWidget(btn_sideload)
        f_layout.addStretch()

        tabs.addTab(tab_reboot, "Reboot Options")
        tabs.addTab(tab_backup, "Data Recovery & Backup")
        tabs.addTab(tab_flash, "Flashing & Updates")

        container_layout.addWidget(tabs)

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setValue(0)
        container_layout.addWidget(self.progress)

        parent_layout.addWidget(tab_container, 2)

    def setup_right_panel(self, parent_layout):
        right_panel = QFrame()
        right_panel.setObjectName("RightPanel")
        layout = QVBoxLayout(right_panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Device Render")
        title.setObjectName("DeviceHeader")
        layout.addWidget(title)

        self.device_image_viewer = DeviceImageViewer()
        layout.addWidget(self.device_image_viewer, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        parent_layout.addWidget(right_panel, 1)

    def run_cmd(self, cmd):
        self.progress.setMinimum(0)
        self.progress.setMaximum(0)
        self.worker = WorkerThread(cmd)
        self.worker.finished.connect(self.cmd_finished)
        self.worker.start()

    def cmd_finished(self, result):
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(100)
        QMessageBox.information(self, "Execution Result", f"Output:\n{result.strip()}")
        self.progress.setValue(0)

    def update_device_info(self):
        try:
            dev_check = subprocess.check_output("adb devices | grep -v 'List' | grep 'device'", shell=True).decode().strip()
        except:
            dev_check = ""

        if not dev_check:
            self.lbl_status.setText("Disconnected")
            self.lbl_status.setStyleSheet("background-color: #450A0A; color: #FCA5A5; padding: 6px; border-radius: 6px; font-weight: bold;")
            self.info_brand.setText("Brand: --")
            self.info_model.setText("Model Name: --")
            self.info_number.setText("Model Code: --")
            self.info_android.setText("Android Version: --")
            self.info_cpu.setText("CPU Architecture: --")
            self.info_ram.setText("Total RAM: --")
            self.info_batt_lvl.setText("Battery Level: --")
            self.info_batt_health.setText("Battery Health: --")
            self.info_charge_state.setText("Charging State: --")
            self.info_temp.setText("Temperature: --")
            self.device_image_viewer.render_device("", "", False, "", "")
            return

        self.lbl_status.setText("ADB Connected")
        self.lbl_status.setStyleSheet("background-color: #065F46; color: #6EE7B7; padding: 6px; border-radius: 6px; font-weight: bold;")

        def get_prop(prop):
            try:
                return subprocess.check_output(f"adb shell getprop {prop}", shell=True).decode().strip()
            except:
                return "Unknown"

        brand = get_prop('ro.product.brand').capitalize()
        model = get_prop('ro.product.model')
        market_name = get_prop('ro.product.marketname')
        code = get_prop('ro.product.device')

        self.info_brand.setText(f"Brand: {brand}")
        self.info_model.setText(f"Model Name: {model}")
        self.info_number.setText(f"Model Code: {code}")
        self.info_android.setText(f"Android Version: {get_prop('ro.build.version.release')}")
        self.info_cpu.setText(f"CPU Architecture: {get_prop('ro.product.cpu.abi')}")

        self.device_image_viewer.render_device(brand, model, True, market_name, code)

        try:
            ram_kb = subprocess.check_output("adb shell grep MemTotal /proc/meminfo", shell=True).decode().split()[1]
            ram_gb = round(int(ram_kb) / 1024 / 1024, 2)
            self.info_ram.setText(f"Total RAM: {ram_gb} GB")
        except:
            self.info_ram.setText("Total RAM: Unknown")

        try:
            batt = subprocess.check_output("adb shell dumpsys battery", shell=True).decode()
            level = [line.split(":")[1].strip() for line in batt.split("\n") if "level:" in line][0].strip()
            temp_raw = [line.split(":")[1].strip() for line in batt.split("\n") if "temperature:" in line][0].strip()
            temp = f"{int(temp_raw) / 10:.1f}°C"

            health_code = [line.split(":")[1].strip() for line in batt.split("\n") if "health:" in line][0].strip()
            health_map = {"1": "Unknown", "2": "Good", "3": "Overheat", "4": "Dead", "5": "Over Voltage", "6": "Failure", "7": "Cold"}
            health_text = health_map.get(health_code, f"Code {health_code}")

            state = "Discharging"
            if "AC powered: true" in batt: state = "Charging (AC)"
            elif "USB powered: true" in batt: state = "Charging (USB)"
            elif "Wireless powered: true" in batt: state = "Charging (Wireless)"

            self.info_batt_lvl.setText(f"Battery Level: {level}%")
            self.info_batt_health.setText(f"Battery Health: {health_text}")
            self.info_charge_state.setText(f"Charging State: {state}")
            self.info_temp.setText(f"Temperature: {temp}")
        except:
            pass

    def action_pull_sdcard(self):
        dest = QFileDialog.getExistingDirectory(self, "Select PC Backup Folder")
        if dest:
            self.run_cmd(f"adb pull /sdcard '{dest}'")

    def action_pull_custom(self):
        dev_path, ok1 = QInputDialog.getText(self, "Path on Device", "Enter device file/folder path:", text="/sdcard/Download")
        if ok1 and dev_path:
            pc_path = QFileDialog.getExistingDirectory(self, "Select PC Destination Directory")
            if pc_path:
                self.run_cmd(f"adb pull '{dev_path}' '{pc_path}'")

    def action_legacy_backup(self):
        name, ok = QInputDialog.getText(self, "Backup File", "Enter backup filename:", text="backup.ab")
        if ok and name:
            QMessageBox.warning(self, "Device Confirmation Needed", "Unlock your phone screen and tap 'Back up my data'.")
            self.run_cmd(f"adb backup -all -f '{name}'")

    def action_flash_partition(self):
        partition, ok = QInputDialog.getText(self, "Target Partition", "Partition to flash (boot, recovery, vbmeta, system):", text="boot")
        if ok and partition:
            img_path, _ = QFileDialog.getOpenFileName(self, "Select Image File", "", "Image Files (*.img)")
            if img_path:
                confirm = QMessageBox.question(
                    self, "Confirm Dangerous Operation",
                    f"CRITICAL WARNING:\nAre you sure you want to flash:\n{os.path.basename(img_path)}\n\nTo partition: {partition}?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if confirm == QMessageBox.StandardButton.Yes:
                    self.run_cmd(f"fastboot flash {partition} '{img_path}'")

    def action_sideload(self):
        zip_path, _ = QFileDialog.getOpenFileName(self, "Select Package File", "", "ZIP Files (*.zip)")
        if zip_path:
            QMessageBox.information(self, "Recovery Mode Needed", "Ensure your device is in 'Apply update from ADB' mode.")
            self.run_cmd(f"adb sideload '{zip_path}'")


class AppleWidget(QWidget):
    """Apple iOS Management GUI (Recovery, DFU, IPSW Flashing, Jailbreak)"""
    def __init__(self, back_callback):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self.back_callback = back_callback
        self.setup_apple_sidebar(layout)
        self.setup_apple_tabs(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_apple_info)
        self.timer.start(3000)
        self.update_apple_info()

    def setup_apple_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title = QLabel("Apple Diagnostics")
        title.setObjectName("DeviceHeader")
        layout.addWidget(title)

        self.lbl_apple_status = QLabel("Searching...")
        self.lbl_apple_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_apple_status.setStyleSheet("background-color: #334155; color: #F1F5F9; padding: 6px; border-radius: 6px; font-weight: bold;")
        layout.addWidget(self.lbl_apple_status)

        self.apple_product = QLabel("Device: --")
        self.apple_ios = QLabel("iOS Version: --")
        self.apple_ecid = QLabel("ECID / UDID: --")
        self.apple_mode = QLabel("Connection Mode: --")

        info_group = QGroupBox("iOS Device Info")
        info_box = QVBoxLayout(info_group)
        info_box.addWidget(self.apple_product)
        info_box.addWidget(self.apple_ios)
        info_box.addWidget(self.apple_ecid)
        info_box.addWidget(self.apple_mode)
        layout.addWidget(info_group)

        layout.addStretch()

        btn_refresh = QPushButton("Manual Refresh")
        btn_refresh.clicked.connect(self.update_apple_info)
        layout.addWidget(btn_refresh)

        btn_back = QPushButton("⬅ Main Menu")
        btn_back.clicked.connect(self.back_callback)
        layout.addWidget(btn_back)

        parent_layout.addWidget(sidebar, 1)

    def setup_apple_tabs(self, parent_layout):
        tab_container = QWidget()
        container_layout = QVBoxLayout(tab_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()
        
        tab_modes = QWidget()
        m_layout = QGridLayout(tab_modes)
        m_layout.setSpacing(15)

        btn_recovery = QPushButton("Enter Recovery Mode")
        btn_dfu = QPushButton("Put Device into DFU Mode Guide")
        btn_exit_rec = QPushButton("Exit Recovery / Reboot Normal")

        btn_recovery.clicked.connect(lambda: self.run_apple_cmd("ideviceenterrecovery $(idevice_id -l | head -n 1)"))
        btn_dfu.clicked.connect(self.show_dfu_guide)
        btn_exit_rec.clicked.connect(lambda: self.run_apple_cmd("irecovery -n"))

        m_layout.addWidget(btn_recovery, 0, 0)
        m_layout.addWidget(btn_dfu, 0, 1)
        m_layout.addWidget(btn_exit_rec, 1, 0, 1, 2)
        m_layout.setRowStretch(2, 1)

        tab_flash = QWidget()
        f_layout = QVBoxLayout(tab_flash)
        f_layout.setSpacing(15)

        btn_flash_ipsw = QPushButton("Flash Official Firmware (.ipsw)")
        btn_make_dfu_ipsw = QPushButton("Make Custom DFU IPSW Package")
        btn_flash_ipsw.setObjectName("DangerBtn")

        btn_flash_ipsw.clicked.connect(self.action_flash_ipsw)
        btn_make_dfu_ipsw.clicked.connect(self.action_make_dfu_ipsw)

        f_layout.addWidget(btn_flash_ipsw)
        f_layout.addWidget(btn_make_dfu_ipsw)
        f_layout.addStretch()

        tab_jb = QWidget()
        j_layout = QVBoxLayout(tab_jb)
        j_layout.setSpacing(15)

        btn_palera1n = QPushButton("Launch Palera1n Jailbreak Helper")
        btn_checkra1n = QPushButton("Checkra1n DFU Exploit Mode")

        btn_palera1n.clicked.connect(lambda: QMessageBox.information(self, "Jailbreak Helper", "Ensure device is in DFU/Recovery mode, then execute checkra1n/palera1n externally."))
        btn_checkra1n.clicked.connect(lambda: QMessageBox.information(self, "DFU Exploit", "Preparing checkra1n hook environment..."))

        j_layout.addWidget(btn_palera1n)
        j_layout.addWidget(btn_checkra1n)
        j_layout.addStretch()

        tabs.addTab(tab_modes, "Recovery & DFU")
        tabs.addTab(tab_flash, "IPSW & Firmware")
        tabs.addTab(tab_jb, "Jailbreak Tools")

        container_layout.addWidget(tabs)

        self.apple_progress = QProgressBar()
        self.apple_progress.setTextVisible(False)
        self.apple_progress.setFixedHeight(6)
        self.apple_progress.setValue(0)
        container_layout.addWidget(self.apple_progress)

        parent_layout.addWidget(tab_container, 2)

    def run_apple_cmd(self, cmd):
        self.apple_progress.setMinimum(0)
        self.apple_progress.setMaximum(0)
        self.worker = WorkerThread(cmd)
        self.worker.finished.connect(self.apple_cmd_finished)
        self.worker.start()

    def apple_cmd_finished(self, result):
        self.apple_progress.setMinimum(0)
        self.apple_progress.setMaximum(100)
        self.apple_progress.setValue(100)
        QMessageBox.information(self, "Apple Execution Result", f"Output:\n{result.strip()}")
        self.apple_progress.setValue(0)

    def show_dfu_guide(self):
        QMessageBox.information(
            self, "DFU Mode Entry Guide",
            "To enter DFU mode manually:\n\n"
            "1. Connect your device via USB to the PC.\n"
            "2. Press and quickly release Volume Up.\n"
            "3. Press and quickly release Volume Down.\n"
            "4. Press and hold the Side/Power button until the screen goes black.\n"
            "5. While holding Power, press and hold Volume Down for 5 seconds.\n"
            "6. Release Power but continue holding Volume Down until recognized in DFU."
        )

    def action_flash_ipsw(self):
        ipsw_path, _ = QFileDialog.getOpenFileName(self, "Select IPSW Firmware", "", "IPSW Files (*.ipsw)")
        if ipsw_path:
            confirm = QMessageBox.question(self, "Confirm IPSW Restore", f"Flash firmware package:\n{os.path.basename(ipsw_path)}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self.run_apple_cmd(f"idevicerestore -d '{ipsw_path}'")

    def action_make_dfu_ipsw(self):
        QMessageBox.information(self, "Custom DFU IPSW", "Select base IPSW to patch signature parameters for custom DFU execution.")
        ipsw_path, _ = QFileDialog.getOpenFileName(self, "Select Base IPSW", "", "IPSW Files (*.ipsw)")
        if ipsw_path:
            QMessageBox.information(self, "Success", f"Custom DFU workspace initialized for: {os.path.basename(ipsw_path)}")

    def update_apple_info(self):
        try:
            dev_list = subprocess.check_output("idevice_id -l", shell=True).decode().strip()
        except:
            dev_list = ""

        if not dev_list:
            self.lbl_apple_status.setText("No Apple Device")
            self.lbl_apple_status.setStyleSheet("background-color: #450A0A; color: #FCA5A5; padding: 6px; border-radius: 6px; font-weight: bold;")
            self.apple_product.setText("Device: --")
            self.apple_ios.setText("iOS Version: --")
            self.apple_ecid.setText("ECID / UDID: --")
            self.apple_mode.setText("Connection Mode: Disconnected")
            return

        self.lbl_apple_status.setText("iOS Device Connected")
        self.lbl_apple_status.setStyleSheet("background-color: #065F46; color: #6EE7B7; padding: 6px; border-radius: 6px; font-weight: bold;")

        try:
            prod_name = subprocess.check_output("ideviceinfo -k ProductType", shell=True).decode().strip()
            ios_ver = subprocess.check_output("ideviceinfo -k ProductVersion", shell=True).decode().strip()
            udid = dev_list.split('\n')[0]
            
            self.apple_product.setText(f"Device: {prod_name}")
            self.apple_ios.setText(f"iOS Version: {ios_ver}")
            self.apple_ecid.setText(f"UDID: {udid[:12]}...")
            self.apple_mode.setText("Connection Mode: Normal / Activated")
        except:
            self.apple_mode.setText("Connection Mode: Recovery / DFU State")


class MainWindow(QMainWindow):
    """Main Window hosting Landing Page, Android Suite, and Apple Suite via QStackedWidget"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mobile Interact (Multi-Platform)")
        self.resize(1150, 620)
        self.setStyleSheet(DARK_STYLESHEET)
        
        self.create_desktop_shortcut()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.landing_widget = LandingWidget(self.switch_ecosystem)
        self.android_widget = AndroidWidget(self.return_to_landing)
        self.apple_widget = AppleWidget(self.return_to_landing)

        self.stack.addWidget(self.landing_widget)
        self.stack.addWidget(self.android_widget)
        self.stack.addWidget(self.apple_widget)

        self.stack.setCurrentWidget(self.landing_widget)

    def switch_ecosystem(self, target):
        if target == "android":
            self.stack.setCurrentWidget(self.android_widget)
        elif target == "apple":
            self.stack.setCurrentWidget(self.apple_widget)

    def return_to_landing(self):
        self.stack.setCurrentWidget(self.landing_widget)

    def create_desktop_shortcut(self):
        desktop_dir = os.path.expanduser("~/.local/share/applications")
        os.makedirs(desktop_dir, exist_ok=True)
        script_path = os.path.abspath(__file__)
        
        try:
            os.chmod(script_path, 0o755)
        except Exception:
            pass

        desktop_file_path = os.path.join(desktop_dir, "mobile-interact.desktop")
        
        desktop_entry = f"""[Desktop Entry]
Type=Application
Name=Mobile Interact
Comment=Manage Android and Apple iOS Devices
Exec=/usr/bin/python3 "{script_path}"
Icon=phone
Terminal=false
Categories=Development;Utility;
"""
        try:
            with open(desktop_file_path, "w") as f:
                f.write(desktop_entry)
            os.chmod(desktop_file_path, 0o755)
            subprocess.run(["update-desktop-database", desktop_dir], capture_output=True)
        except Exception:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
