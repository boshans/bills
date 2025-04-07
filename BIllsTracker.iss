[Setup]
AppName=BillsTracker
AppVersion=1.0
DefaultDirName={pf}\BillsTracker
DefaultGroupName=BillsTracker
UninstallDisplayIcon={app}\billPayments.exe
OutputDir=dist
OutputBaseFilename=BillsTracker_Setup
Compression=lzma
SolidCompression=yes
LicenseFile=license.txt

[Files]
Source: "dist\\billPayments.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "license.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "readme.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{commondesktop}\\BillsTracker"; Filename: "{app}\\billPayments.exe"

[Run]
Filename: "{app}\\billPayments.exe"; Description: "Launch BillsTracker"; Flags: nowait postinstall skipifsilent
Filename: "notepad.exe"; Parameters: "{app}\\readme.txt"; Flags: postinstall shellexec skipifsilent
