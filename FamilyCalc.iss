; ============================================================
;  Family Calculator - Windows installer (Inno Setup script)
;  Build dist\FamilyCalc.exe first (run build.bat), then open
;  this file in Inno Setup (free: https://jrsoftware.org/isdl.php)
;  and click Compile. Produces Output\FamilyCalc-Setup.exe.
; ============================================================

[Setup]
AppId={{B7E2B3C4-1A6D-4F2E-9C3A-FAMILYCALC001}
AppName=Family Calculator
AppVersion=1.0
AppPublisher=Bluestem Systems
DefaultDirName={autopf}\FamilyCalc
DefaultGroupName=Family Calculator
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\FamilyCalc.exe
OutputBaseFilename=FamilyCalc-Setup
Compression=lzma2
SolidCompression=yes
; Per-user install: no admin prompt, installs under the user's profile.
PrivilegesRequired=lowest
WizardStyle=modern
SetupIconFile=FamilyCalc.ico

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop shortcut"; GroupDescription: "Additional shortcuts:"
Name: "autostart";  Description: "Start Family Calculator automatically when I log in"; GroupDescription: "Startup:"

[Files]
Source: "dist\FamilyCalc.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu and (optional) Desktop shortcuts open the app (server + browser).
Name: "{group}\Family Calculator"; Filename: "{app}\FamilyCalc.exe"
Name: "{userdesktop}\Family Calculator"; Filename: "{app}\FamilyCalc.exe"; Tasks: desktopicon
Name: "{group}\Uninstall Family Calculator"; Filename: "{uninstallexe}"

[Registry]
; Auto-start the SERVER ONLY at login (no browser pop-up), if the user opted in.
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
  ValueType: string; ValueName: "FamilyCalc"; \
  ValueData: """{app}\FamilyCalc.exe"" --serve-only"; \
  Flags: uninsdeletevalue; Tasks: autostart

[Run]
; Offer to launch right after install.
Filename: "{app}\FamilyCalc.exe"; Description: "Launch Family Calculator now"; \
  Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Note: the user's data lives in %LOCALAPPDATA%\FamilyCalc and is intentionally
; left in place on uninstall, so removing/reinstalling never loses data.
