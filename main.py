import ctypes
import sys
import tkinter as tk
import pygame
from pathlib import Path
from tkinter import messagebox, ttk

APP_TITLE = "Hamleys Closing Announcer"
INTERVAL_SECONDS = 80
CLOSING_TIME_TEXT = "10:00 PM"
DEFAULT_VOLUME = 80
AUDIO_FILES = [
    ("1st_announcement.mp3", "Announcement 1"),
    ("2nd_announcement.mp3", "Announcement 2"),
    ("3th_announcement.mp3", "Announcement 3"),
]

BG = "#FFF8F1"
CARD = "#FFFCF9"
CARD_HERO = "#FFF0E9"
RED = "#C8102E"
RED_DARK = "#8F1020"
GREEN = "#20A64A"
TEXT = "#321515"
MUTED = "#766A66"
BORDER = "#F0DED5"


def resource_path(filename):
    """Return a bundled asset path (PyInstaller) or source-tree path."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / filename


class AudioPlayer:
    """Play bundled MP3 files through pygame/SDL_mixer, not Windows MCI."""

    def __init__(self):
        self.volume = DEFAULT_VOLUME
        self.initialized = False

    def _ensure_initialized(self):
        if not self.initialized:
            try:
                pygame.mixer.init()
                self.initialized = True
                pygame.mixer.music.set_volume(self.volume / 100.0)
            except pygame.error as exc:
                raise RuntimeError(
                    "The audio device could not be initialized. Check that the PC has an active audio output device.\\n\\n"
                    + str(exc)
                ) from exc

    def set_volume(self, percent):
        self.volume = max(0, min(100, int(percent)))
        if self.initialized:
            pygame.mixer.music.set_volume(self.volume / 100.0)

    def play(self, filename):
        self._ensure_initialized()
        path = resource_path(filename)
        if not path.is_file():
            raise FileNotFoundError(f"Audio file not found:\\n{path}")
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(self.volume / 100.0)
            pygame.mixer.music.play()
        except pygame.error as exc:
            raise RuntimeError(f"Could not decode or play {filename}: {exc}") from exc

    def playing(self):
        return self.initialized and pygame.mixer.music.get_busy()

    def stop(self):
        if self.initialized:
            pygame.mixer.music.stop()

    def close(self):
        if self.initialized:
            pygame.mixer.music.stop()

    def shutdown(self):
        if self.initialized:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            self.initialized = False


class ClosingAnnouncer:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("820x650")
        self.root.minsize(700, 600)
        self.root.configure(bg=BG)
        self.running = False
        self.is_playing = False
        self.next_index = 0
        self.seconds_left = INTERVAL_SECONDS
        self.player = AudioPlayer()
        self.volume_var = tk.IntVar(value=DEFAULT_VOLUME)
        self.playlist_states = []
        self._build_ui()
        self._refresh_countdown()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Hamleys.Horizontal.TScale",
            background=CARD,
            troughcolor="#F0DED5",
            sliderthickness=18,
        )

        page = tk.Frame(self.root, bg=BG, padx=34, pady=24)
        page.pack(fill="both", expand=True)

        header = tk.Frame(page, bg=BG)
        header.pack(fill="x", pady=(0, 4))
        tk.Label(
            header, text="★ Hamleys", bg=BG, fg=RED,
            font=("Segoe UI", 23, "bold")
        ).pack(side="left")
        tk.Label(
            header, text="Hamleys Closing Announcer", bg=BG, fg=RED_DARK,
            font=("Segoe UI", 21, "bold")
        ).pack(side="left", padx=(18, 0))

        tk.Label(
            page, text="A simple helper for store closing announcements",
            bg=BG, fg=MUTED, font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 16))

        hero = tk.Frame(
            page, bg=CARD_HERO, highlightbackground=BORDER,
            highlightthickness=1, padx=20, pady=18
        )
        hero.pack(fill="x", pady=(0, 16))
        self.status_label = tk.Label(
            hero, text="●  STOPPED", bg=CARD_HERO, fg=RED_DARK,
            font=("Segoe UI", 10, "bold")
        )
        self.status_label.pack()
        self.message_label = tk.Label(
            hero, text="Ready when you are", bg=CARD_HERO, fg=TEXT,
            font=("Segoe UI", 23, "bold")
        )
        self.message_label.pack(pady=(7, 3))
        self.countdown_label = tk.Label(
            hero, text="Next announcement in 01:20", bg=CARD_HERO,
            fg=MUTED, font=("Segoe UI", 13)
        )
        self.countdown_label.pack()

        buttons = tk.Frame(page, bg=BG)
        buttons.pack(fill="x", pady=(0, 16))
        self.start_button = tk.Button(
            buttons, text="▶   START ANNOUNCEMENTS",
            command=self.start, bg=GREEN, fg="white",
            activebackground="#168A3B", activeforeground="white",
            relief="flat", bd=0, font=("Segoe UI", 14, "bold"),
            cursor="hand2", height=2
        )
        self.start_button.pack(side="left", fill="x", expand=True, padx=(0, 7))
        self.stop_button = tk.Button(
            buttons, text="■   STOP", command=self.stop,
            bg="#E7E1DE", fg="#514744", activebackground="#D8CFCA",
            relief="flat", bd=0, font=("Segoe UI", 13, "bold"),
            cursor="hand2", height=2, state="disabled"
        )
        self.stop_button.pack(side="left", fill="x", expand=True, padx=(7, 0))

        info = tk.Frame(page, bg=BG)
        info.pack(fill="x", pady=(0, 14))
        self._info_card(info, "CLOSING TIME", CLOSING_TIME_TEXT)
        self._info_card(info, "INTERVAL", "01:20")
        self._info_card(info, "ANNOUNCEMENTS", "3")

        volume_card = tk.Frame(
            page, bg=CARD, highlightbackground=BORDER, highlightthickness=1,
            padx=16, pady=10
        )
        volume_card.pack(fill="x", pady=(0, 14))
        volume_header = tk.Frame(volume_card, bg=CARD)
        volume_header.pack(fill="x")
        tk.Label(
            volume_header, text="ANNOUNCEMENT VOLUME", bg=CARD, fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left")
        self.volume_value = tk.Label(
            volume_header, text="80%", bg=CARD, fg=RED_DARK,
            font=("Segoe UI", 11, "bold")
        )
        self.volume_value.pack(side="right")
        self.volume_scale = ttk.Scale(
            volume_card, from_=0, to=100, orient="horizontal",
            variable=self.volume_var, style="Hamleys.Horizontal.TScale",
            command=self._volume_changed
        )
        self.volume_scale.pack(fill="x", pady=(7, 0))

        tk.Label(
            page, text="ANNOUNCEMENT PLAYLIST", bg=BG, fg=RED_DARK,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 7))

        for _, name in AUDIO_FILES:
            item = tk.Frame(
                page, bg=CARD, highlightbackground=BORDER,
                highlightthickness=1, padx=12, pady=7
            )
            item.pack(fill="x", pady=3)
            tk.Label(
                item, text="♫", bg=CARD, fg=RED,
                font=("Segoe UI", 16, "bold")
            ).pack(side="left", padx=(0, 10))
            tk.Label(
                item, text=name, bg=CARD, fg=TEXT,
                font=("Segoe UI", 10, "bold")
            ).pack(side="left")
            state = tk.Label(
                item, text="READY", bg=CARD, fg=GREEN,
                font=("Segoe UI", 8, "bold")
            )
            state.pack(side="right")
            self.playlist_states.append(state)

        tk.Label(
            page,
            text="Volume affects announcements only. Windows and Resiowall stay unchanged.",
            bg=BG, fg=MUTED, font=("Segoe UI", 8)
        ).pack(side="bottom", pady=(12, 0))

    def _info_card(self, parent, title, value):
        card = tk.Frame(
            parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1,
            padx=12, pady=10
        )
        card.pack(side="left", fill="both", expand=True, padx=4)
        tk.Label(
            card, text=title, bg=CARD, fg=MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack()
        tk.Label(
            card, text=value, bg=CARD, fg=RED_DARK,
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(3, 0))

    def _volume_changed(self, _value=None):
        value = self.volume_var.get()
        self.volume_value.configure(text=f"{value}%")
        self.player.set_volume(value)

    def start(self):
        missing = [
            filename for filename, _ in AUDIO_FILES
            if not resource_path(filename).is_file()
        ]
        if missing:
            messagebox.showerror(
                "Audio files missing",
                "These announcement files are missing:\n\n" + "\n".join(missing),
                parent=self.root,
            )
            return
        self.running = True
        self.is_playing = False
        self.next_index = 0
        self.seconds_left = INTERVAL_SECONDS
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_label.configure(text="●  RUNNING", fg=GREEN)
        self.message_label.configure(text="Starting first announcement…")
        self._play_next()

    def stop(self):
        self.running = False
        self.is_playing = False
        self.player.stop()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="●  STOPPED", fg=RED_DARK)
        self.message_label.configure(text="Ready when you are")
        self.seconds_left = INTERVAL_SECONDS
        self._refresh_countdown()
        for state in self.playlist_states:
            state.configure(text="READY", fg=GREEN)

    def _tick(self):
        if not self.running:
            return
        if self.is_playing:
            if not self.player.playing():
                self.player.close()
                self.is_playing = False
                for state in self.playlist_states:
                    state.configure(text="READY", fg=GREEN)
                self.message_label.configure(text="Announcement complete")
                self.seconds_left = INTERVAL_SECONDS
                self._refresh_countdown()
            self.root.after(300, self._tick)
            return

        self.seconds_left -= 1
        self._refresh_countdown()
        if self.seconds_left <= 0:
            self._play_next()
            return
        self.root.after(1000, self._tick)

    def _play_next(self):
        filename, display_name = AUDIO_FILES[self.next_index]
        try:
            self.player.play(filename)
        except Exception as exc:
            messagebox.showerror(
                "Playback error",
                f"Could not play {filename}.\n\n{exc}",
                parent=self.root,
            )
            self.stop()
            return

        for state in self.playlist_states:
            state.configure(text="READY", fg=GREEN)
        self.playlist_states[self.next_index].configure(
            text="PLAYING", fg=RED
        )
        self.message_label.configure(text=f"Playing {display_name}")
        self.countdown_label.configure(text="Announcement playing…")
        self.is_playing = True
        self.next_index = (self.next_index + 1) % len(AUDIO_FILES)
        self.root.after(300, self._tick)

    def _refresh_countdown(self):
        minutes, seconds = divmod(max(0, self.seconds_left), 60)
        self.countdown_label.configure(
            text=f"Next announcement in {minutes:02d}:{seconds:02d}"
        )

    def on_close(self):
        self.running = False
        self.player.shutdown()
        self.root.destroy()


def main():
    root = tk.Tk()
    icon_file = resource_path("assets/hamleys-announcer.ico")
    if icon_file.is_file():
        try:
            root.iconbitmap(str(icon_file))
        except tk.TclError:
            pass
    ClosingAnnouncer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
