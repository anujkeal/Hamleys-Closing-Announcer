[Setup]
AppId={{B78A3C2D-5B8E-4B8A-A30E-5A6C9E7D2041}}
AppName=Hamleys Closing Announcer
AppVersion=1.0.0
AppPublisher=Keal
DefaultDirName={autopf}\Hamleys Closing Announcer
DefaultGroupName=Hamleys Closing Announcer
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=Hamleys-Closing-Announcer-Setup
SetupIconFile=assets\hamleys-announcer.ico
UninstallDisplayIcon={app}\Hamleys Closing Announcer.exe
ArchitecturesInstallIn64BitMode=x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: checked

[Files]
Source: "dist\Hamleys Closing Announcer.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Hamleys Closing Announcer"; Filename: "{app}\Hamleys Closing Announcer.exe"
Name: "{autodesktop}\Hamleys Closing Announcer"; Filename: "{app}\Hamleys Closing Announcer.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Hamleys Closing Announcer.exe"; Description: "Launch Hamleys Closing Announcer"; Flags: postinstall nowait skipifsilent
