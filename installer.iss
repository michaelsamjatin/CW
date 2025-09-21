[Setup]
AppName=Realisierungsdatenvisualizer
AppVersion=1.0
AppPublisher=Changing Waves Fundraising GmbH
AppPublisherURL=https://changingwaves.org
AppSupportURL=https://github.com/michael.samjatin/CW
AppUpdatesURL=https://github.com/michael.samjatin/CW/releases
DefaultDirName={autopf}\Realisierungsdatenvisualizer
DefaultGroupName=Realisierungsdatenvisualizer
AllowNoIcons=yes
LicenseFile=
OutputDir=dist
OutputBaseFilename=Realisierungsdatenvisualizer-Setup
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64 arm64
ArchitecturesInstallIn64BitMode=x64 arm64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Realisierungsdatenvisualizer.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "realisierungsdaten.html"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Realisierungsdatenvisualizer"; Filename: "{app}\Realisierungsdatenvisualizer.exe"
Name: "{group}\{cm:UninstallProgram,Realisierungsdatenvisualizer}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Realisierungsdatenvisualizer"; Filename: "{app}\Realisierungsdatenvisualizer.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Realisierungsdatenvisualizer.exe"; Description: "{cm:LaunchProgram,Realisierungsdatenvisualizer}"; Flags: nowait postinstall skipifsilent