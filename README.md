# Hamleys Closing Announcer

A lightweight, standalone Windows desktop application for the store's three closing announcements.

## Designed for low-spec Windows PCs

- Native Windows MP3 playback through the built-in Multimedia Control Interface (MCI / WinMM).
- Simple Tkinter desktop interface.
- No PySide6, Pygame, browser, internet connection, or Python installation required on the target PC.
- The EXE bundles the three MP3 announcement files.
- The app's volume slider changes only this application's announcement playback volume. It does not change Windows master volume or Resiowall volume.

The GitHub Actions build machine uses Python and PyInstaller to package the application. The Hamleys PC only needs to run the downloaded EXE.

## How it works

1. Press **Start Announcements**.
2. The app waits 1 minute 20 seconds.
3. It plays announcement 1, then 2, then 3, and repeats.
4. After each announcement finishes, the 1 minute 20 second countdown starts again.
5. Press **Stop** to stop playback.
6. Store closing time displayed: **10:00 PM**.

## Audio note

The app has independent volume control for its own MP3 announcements. It intentionally does not change Windows master volume or Resiowall. Therefore, Resiowall music may continue underneath the announcement. Muting or pausing Resiowall requires a separate supported control or audio mixer.

## Download

Open the **Actions** tab, select the latest successful **Build Lightweight Windows EXE** run, and download the `Hamleys-Closing-Announcer-Lightweight-Windows` artifact. Extract the ZIP and double-click `Hamleys Closing Announcer.exe`.

## Local development

Python 3.11 on Windows is required only if running from source:

```powershell
python main.py
```

The three MP3 files must be beside `main.py` when running from source.
