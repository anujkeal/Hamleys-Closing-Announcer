# Hamleys Closing Announcer

A simple Windows desktop app for playing the store's three closing announcements.

## How it works
- Press **Start Announcements**.
- The app waits 1 minute 20 seconds, then plays the next MP3.
- Announcements rotate in order: 1st, 2nd, 3rd, then repeat.
- After an announcement finishes, the 1 minute 20 second interval starts again.
- Press **Stop** at any time to stop playback.
- The closing time displayed in the app is **10:00 PM**.

## Announcement volume
The app has its own announcement-volume slider. It controls only MP3 playback inside this application. It does not change Windows master volume, mute other applications, or change Resiowall's volume.

**Audio behaviour:** Because Resiowall remains untouched, its music may continue underneath an announcement. To pause or duck Resiowall independently, the store's audio setup needs a separate supported control or mixer input.

## Build
GitHub Actions builds the Windows executable on every push to `main`, or when manually started from the Actions tab.

Download the **Hamleys-Closing-Announcer-Windows** artifact from the completed workflow run.

## Local development
```powershell
python -m pip install -r requirements.txt
python main.py
```

The three MP3 files must remain in the project root when running from source.
