[Setup]
AppId={{D37B832E-6582-4E90-A899-7E4F63D4A802}}
AppName=NAM Hardware Finder
AppVersion=1.0.0
AppPublisher=NAM Hardware Finder
AppPublisherURL=https://github.com/
DefaultDirName={autopf}\NAM Hardware Finder
DefaultGroupName=NAM Hardware Finder
OutputDir=output
OutputBaseFilename=NAM_Hardware_Finder_Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\NAM_Hardware_Finder\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\NAM Hardware Finder"; Filename: "{app}\NAM_Hardware_Finder.exe"
Name: "{autodesktop}\NAM Hardware Finder"; Filename: "{app}\NAM_Hardware_Finder.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\NAM_Hardware_Finder.exe"; Description: "{cm:LaunchProgram,NAM Hardware Finder}"; Flags: nowait postinstall skipifsilent