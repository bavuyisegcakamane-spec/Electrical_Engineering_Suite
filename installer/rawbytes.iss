; raw.bytes Electrical Engineering Suite Windows installer
#define AppName "Electrical Engineering Suite"
#define AppVersion "0.1.0"
[Setup]
AppId={{3F0B76C0-1F73-45F5-B8A8-8D4B3F5D6F12}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=raw.bytes
AppPublisherURL=https://github.com/bavuyisegcakamane-spec/Electrical_Engineering_Suite
DefaultDirName={localappdata}\Programs\raw.bytes\ElectricalEngineeringSuite
DefaultGroupName=raw.bytes
PrivilegesRequired=lowest
OutputDir=..\dist\installer
OutputBaseFilename=raw.bytes-ElectricalEngineeringSuite-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
UninstallDisplayName=Electrical Engineering Suite — raw.bytes
WizardStyle=modern
[Files]
Source: "..\dist\ElectricalEngineeringSuite\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\Electrical Engineering Suite"; Filename: "{app}\ElectricalEngineeringSuite.exe"
Name: "{autodesktop}\Electrical Engineering Suite"; Filename: "{app}\ElectricalEngineeringSuite.exe"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked
[Run]
Filename: "{app}\ElectricalEngineeringSuite.exe"; Description: "Launch Electrical Engineering Suite"; Flags: nowait postinstall skipifsilent
