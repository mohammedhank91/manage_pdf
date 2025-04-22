#define MyAppName        "PDF Manager"
#define MyAppVersion     "1.0.0"
#define MyAppPublisher   "mohammedhank91"
#define MyAppURL         "https://github.com/mohammedhank91"
#define MyAppExeName     "PDFManager.exe"
#define MyAppLicenseFile "..\LICENSE.txt"
#define MyAppIcon        "..\src\resources\manage_pdf.ico"

[Setup]
AppId={{F19E2C34-317D-4B27-9BEF-1A12D8D1E9A8}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName} {#MyAppVersion}
OutputDir=..\installer_64
OutputBaseFilename=PDFManager_Setup_v{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x86 x64
WizardStyle=modern
WizardImageFile=..\src\resources\wizard_image.bmp
WizardSmallImageFile=..\src\resources\wizard_small.bmp
SetupIconFile={#MyAppIcon}
UninstallDisplayIcon={app}\manage_pdf.ico
MinVersion=6.1
PrivilegesRequired=lowest
AllowNoIcons=yes
ShowLanguageDialog=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french";  MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon";     Description: "{cm:CreateDesktopIcon}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; Flags: unchecked

[Files]
Source: "..\dist\PDFManager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#MyAppIcon}";             DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}";        Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\manage_pdf.ico"
Name: "{autodesktop}\{#MyAppName}";  Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{group}\Visit Publisher Website"; Filename: "{#MyAppURL}"; WorkingDir: "{app}"

[Registry]
Root: HKCR; Subkey: ".pdf\OpenWithProgids";      ValueType: string; ValueName: "PDFManager.pdf";        ValueData: ""; Flags: uninsdeletevalue
Root: HKCR; Subkey: "PDFManager.pdf";            ValueType: string; ValueName: "";                    ValueData: "{#MyAppName}"; Flags: uninsdeletekey
Root: HKCR; Subkey: "PDFManager.pdf\DefaultIcon";ValueType: string; ValueName: "";                    ValueData: "{app}\manage_pdf.ico,0"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "PDFManager.pdf\shell\open\command"; ValueType: string; ValueName: "";            ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletevalue

[InstallDelete]
Type: files; Name: "{app}\temp\*.*"
Type: dirifempty; Name: "{app}\temp"

[UninstallDelete]
Type: files; Name: "{userappdata}\PDF Manager\*.*"
Type: dirifempty; Name: "{userappdata}\PDF Manager"

[Code]
// Prevent running while app is open
function InitializeSetup(): Boolean;
begin
  if CheckForMutexes('PDFManagerMutex') then
  begin
    MsgBox('PDF Manager is currently running. Please close it and retry.', mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;

// Verify GhostScript dir exists
function GhostScriptDirExists(): Boolean;
var
  Path: string;
begin
  Path := ExpandConstant('{app}\ghostscript_portable\bin');
  Result := DirExists(Path);
  if not Result then
    MsgBox('Warning: GhostScript not found—compression may not work fully.', mbInformation, MB_OK);
end;
