# Hamleys Closing Announcer

A lightweight Windows desktop app for playing the store's three closing announcements.

## Install on the store PC

1. Open the repository's **Actions** tab.
2. Select the latest successful **Build Windows App and Installer** run.
3. Download the `Hamleys-Closing-Announcer-Windows-Package` artifact.
4. Extract the downloaded ZIP.
5. Double-click **Hamleys-Closing-Announcer-Setup.exe**.
6. Follow the setup wizard. The desktop shortcut option is selected by default.

The installer places the app on the PC, creates a Start Menu entry and (if selected) a desktop shortcut. It also includes all three announcement MP3s inside the packaged app. No Python installation or internet connection is needed on the store PC. Internet is needed only by GitHub Actions to build the package.

## Playback sequence

1. Press **Start Announcements**.
2. Announcement 1 plays immediately.
3. After it finishes, the app waits 1 minute 20 seconds and plays announcement 2.
4. It repeats the same wait before announcement 3, then cycles through all three.
5. Press **Stop** to stop playback.

Store closing time displayed: **10:00 PM**.

## Audio and volume

- Playback uses the bundled pygame/SDL_mixer audio engine, not Windows MCI.
- The volume slider controls only this app's announcement audio. It does not change Windows master volume or Resiowall volume.
- Resiowall music may continue underneath announcements. This app deliberately does not pause or mute Resiowall.

## System requirements

- Windows 10 or Windows 11, 64-bit.
- A working audio output device and speakers.
- No Python, separate MP3 codec, or runtime internet connection required.

## Portable version

The same Actions artifact also contains **Hamleys Closing Announcer.exe**. This is the portable build; it can be run directly without installing, and does not create shortcuts.

## Local development

Python 3.11 is required to run from source:

```powershell
python -m pip install -r requirements.txt
python main.py
```

Keep the three MP3 files beside `main.py` when running from source.

https://drive.google.com/drive/folders/1gCxL8Jn2w2kzCXhqYJfimgU3Yd0rnFzU
