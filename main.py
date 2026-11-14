import os
import sys
from pathlib import Path

import pygame
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QMainWindow,
    QMessageBox, QPushButton, QVBoxLayout, QWidget
)

APP_TITLE = "Hamleys Closing Announcer"
INTERVAL_SECONDS = 80
CLOSING_TIME_TEXT = "09:00 PM"
AUDIO_FILES = [
    ("1st_announcement.mp3", "Announcement 1"),
    ("2nd_announcement.mp3", "Announcement 2"),
    ("3th_announcement.mp3", "Announcement 3"),
]


def resource_path(filename: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / filename


class AudioDucker:
    """Temporarily mute other Windows audio sessions during an announcement."""

    def __init__(self):
        self.saved_sessions = []

    def mute_other_apps(self):
        self.restore()
        if os.name != "nt":
            return False
        try:
            from pycaw.pycaw import AudioUtilities
            current_pid = os.getpid()
            for session in AudioUtilities.GetAllSessions():
                process = session.Process
                if process is None or process.pid == current_pid:
                    continue
                volume = session.SimpleAudioVolume
                was_muted = bool(volume.GetMute())
                self.saved_sessions.append((volume, was_muted))
                volume.SetMute(True, None)
            return True
        except Exception:
            self.restore()
            return False

    def restore(self):
        for volume, was_muted in self.saved_sessions:
            try:
                volume.SetMute(was_muted, None)
            except Exception:
                pass
        self.saved_sessions.clear()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(760, 540)
        self.resize(900, 620)
        self.running = False
        self.is_announcement_playing = False
        self.next_audio_index = 0
        self.seconds_remaining = INTERVAL_SECONDS
        self.ducker = AudioDucker()
        pygame.mixer.init()

        self.countdown_timer = QTimer(self)
        self.countdown_timer.setInterval(1000)
        self.countdown_timer.timeout.connect(self.countdown_tick)
        self.playback_timer = QTimer(self)
        self.playback_timer.setInterval(250)
        self.playback_timer.timeout.connect(self.check_playback)
        self.build_ui()
        self.update_countdown()

    def build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(34, 24, 34, 26)
        outer.setSpacing(18)

        header = QHBoxLayout()
        brand = QLabel("★ Hamleys")
        brand.setObjectName("brand")
        heading = QLabel("Hamleys Closing Announcer")
        heading.setObjectName("heading")
        header.addWidget(brand)
        header.addSpacing(18)
        header.addWidget(heading, 1)
        outer.addLayout(header)

        subtitle = QLabel("A simple helper for store closing announcements")
        subtitle.setObjectName("subtitle")
        outer.addWidget(subtitle)

        status_card = QFrame()
        status_card.setObjectName("statusCard")
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(24, 18, 24, 18)
        status_layout.setSpacing(8)
        self.status_label = QLabel("●  STOPPED")
        self.status_label.setObjectName("statusLabel")
        self.main_message = QLabel("Ready when you are")
        self.main_message.setObjectName("mainMessage")
        self.countdown_label = QLabel("Next announcement in 01:20")
        self.countdown_label.setObjectName("countdownLabel")
        status_layout.addWidget(self.status_label, alignment=Qt.AlignHCenter)
        status_layout.addWidget(self.main_message, alignment=Qt.AlignHCenter)
        status_layout.addWidget(self.countdown_label, alignment=Qt.AlignHCenter)
        outer.addWidget(status_card)

        controls = QHBoxLayout()
        controls.setSpacing(14)
        self.start_button = QPushButton("▶   START ANNOUNCEMENTS")
        self.start_button.setObjectName("startButton")
        self.start_button.setMinimumHeight(68)
        self.start_button.clicked.connect(self.start_announcements)
        self.stop_button = QPushButton("■   STOP")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setMinimumHeight(68)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_announcements)
        controls.addWidget(self.start_button, 2)
        controls.addWidget(self.stop_button, 1)
        outer.addLayout(controls)

        info_row = QHBoxLayout()
        info_row.setSpacing(12)
        info_row.addWidget(self.info_card("CLOSING TIME", CLOSING_TIME_TEXT))
        info_row.addWidget(self.info_card("INTERVAL", "01:20"))
        info_row.addWidget(self.info_card("ANNOUNCEMENTS", "3"))
        outer.addLayout(info_row)

        playlist_title = QLabel("Announcement playlist")
        playlist_title.setObjectName("sectionTitle")
        outer.addWidget(playlist_title)
        self.playlist_labels = []
        for _, display_name in AUDIO_FILES:
            item = QFrame()
            item.setObjectName("playlistItem")
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(16, 10, 16, 10)
            dot = QLabel("♪")
            dot.setObjectName("musicIcon")
            name = QLabel(display_name)
            name.setObjectName("playlistName")
            state = QLabel("READY")
            state.setObjectName("fileState")
            item_layout.addWidget(dot)
            item_layout.addWidget(name, 1)
            item_layout.addWidget(state)
            self.playlist_labels.append((item, state))
            outer.addWidget(item)

        footer = QLabel("Other app audio is muted during announcements, then restored.")
        footer.setObjectName("footer")
        footer.setAlignment(Qt.AlignCenter)
        outer.addStretch(1)
        outer.addWidget(footer)

        self.setStyleSheet("""
            QWidget#root { background: #FFF8F1; color: #321515; }
            QLabel { font-family: 'Segoe UI'; }
            QLabel#brand { color: #C8102E; font-size: 24px; font-weight: 800; }
            QLabel#heading { color: #8F1020; font-size: 25px; font-weight: 750; }
            QLabel#subtitle { color: #766A66; font-size: 14px; }
            QFrame#statusCard { background: #FFF0E9; border: 1px solid #F0D8CE; border-radius: 22px; }
            QLabel#statusLabel { color: #9A1826; font-size: 13px; font-weight: 800; letter-spacing: 1px; }
            QLabel#mainMessage { color: #281313; font-size: 27px; font-weight: 750; }
            QLabel#countdownLabel { color: #756460; font-size: 16px; }
            QPushButton { border: 0; border-radius: 16px; padding: 14px 18px; font-size: 16px; font-weight: 750; }
            QPushButton#startButton { background: #20A64A; color: white; }
            QPushButton#startButton:hover { background: #168A3B; }
            QPushButton#startButton:disabled { background: #A8CDB1; color: #F7FFF8; }
            QPushButton#stopButton { background: #E7E1DE; color: #514744; }
            QPushButton#stopButton:hover { background: #D8CFCA; }
            QPushButton#stopButton:disabled { color: #A69D98; }
            QFrame#infoCard, QFrame#playlistItem { background: #FFFCF9; border: 1px solid #F0DED5; border-radius: 14px; }
            QLabel#infoTitle { color: #887873; font-size: 11px; font-weight: 800; }
            QLabel#infoValue { color: #8F1020; font-size: 20px; font-weight: 800; }
            QLabel#sectionTitle { color: #541B1B; font-size: 17px; font-weight: 800; margin-top: 3px; }
            QLabel#musicIcon { color: #C8102E; font-size: 21px; font-weight: 800; }
            QLabel#playlistName { color: #382321; font-size: 14px; font-weight: 650; }
            QLabel#fileState { color: #188342; font-size: 11px; font-weight: 800; }
            QLabel#footer { color: #8B7B75; font-size: 11px; }
        """)

    def info_card(self, title, value):
        card = QFrame()
        card.setObjectName("infoCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(5)
        title_label = QLabel(title)
        title_label.setObjectName("infoTitle")
        value_label = QLabel(value)
        value_label.setObjectName("infoValue")
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card

    def start_announcements(self):
        missing = [name for name, _ in AUDIO_FILES if not resource_path(name).is_file()]
        if missing:
            QMessageBox.critical(self, "Audio files missing",
                "These announcement files could not be found:\n\n" + "\n".join(missing))
            return
        self.running = True
        self.is_announcement_playing = False
        self.next_audio_index = 0
        self.seconds_remaining = INTERVAL_SECONDS
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("●  RUNNING")
        self.status_label.setStyleSheet("color: #168A3B;")
        self.main_message.setText("Announcements are scheduled")
        self.countdown_timer.start()
        self.update_countdown()

    def stop_announcements(self):
        self.running = False
        self.countdown_timer.stop()
        self.playback_timer.stop()
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
        self.ducker.restore()
        self.is_announcement_playing = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("●  STOPPED")
        self.status_label.setStyleSheet("color: #9A1826;")
        self.main_message.setText("Ready when you are")
        self.countdown_label.setText("Next announcement in 01:20")
        for _, state in self.playlist_labels:
            state.setText("READY")

    def countdown_tick(self):
        if not self.running or self.is_announcement_playing:
            return
        self.seconds_remaining -= 1
        self.update_countdown()
        if self.seconds_remaining <= 0:
            self.play_next_announcement()

    def update_countdown(self):
        minutes, seconds = divmod(max(0, self.seconds_remaining), 60)
        self.countdown_label.setText(f"Next announcement in {minutes:02d}:{seconds:02d}")

    def play_next_announcement(self):
        if not self.running:
            return
        filename, display_name = AUDIO_FILES[self.next_audio_index]
        try:
            self.ducker.mute_other_apps()
            pygame.mixer.music.load(str(resource_path(filename)))
            pygame.mixer.music.play()
        except Exception as exc:
            self.ducker.restore()
            QMessageBox.critical(self, "Playback error", f"Could not play {filename}.\n\n{exc}")
            self.stop_announcements()
            return
        for _, state in self.playlist_labels:
            state.setText("READY")
        self.playlist_labels[self.next_audio_index][1].setText("PLAYING")
        self.main_message.setText(f"Playing {display_name}")
        self.countdown_label.setText("Please wait — announcement playing")
        self.is_announcement_playing = True
        self.playback_timer.start()
        self.next_audio_index = (self.next_audio_index + 1) % len(AUDIO_FILES)

    def check_playback(self):
        if not self.running or not self.is_announcement_playing:
            return
        if not pygame.mixer.music.get_busy():
            self.playback_timer.stop()
            self.ducker.restore()
            self.is_announcement_playing = False
            for _, state in self.playlist_labels:
                state.setText("READY")
            self.main_message.setText("Announcement complete")
            self.seconds_remaining = INTERVAL_SECONDS
            self.update_countdown()

    def closeEvent(self, event):
        self.stop_announcements()
        try:
            pygame.mixer.quit()
        except pygame.error:
            pass
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
