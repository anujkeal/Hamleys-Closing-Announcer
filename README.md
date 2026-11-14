# Hamleys Closing Announcer

A simple Windows desktop app for playing the store's three closing announcements.

## How it works
- Press **Start Announcements**.
- The app waits 1 minute 20 seconds, then plays the next MP3.
- Announcements rotate in order: 1st, 2nd, 3rd, then repeat.
- After an announcement finishes, the 1 minute 20 second interval starts again.
- Press **Stop** at any time to stop playback and restore audio.

During playback, the app attempts to mute other Windows audio sessions and restores their previous mute states afterwards. This is best-effort and must be tested with the store's Resiowall setup before live use.

## Build
GitHub Actions builds the Windows executable on every push to `main`, or when manually started from the Actions tab.

Download the **Hamleys-Closing-Announcer-Windows** artifact from the completed workflow run.

## Local development
```powershell
python -m pip install -r requirements.txt
python main.py
```

The three MP3 files must remain in the project root when running from source.
