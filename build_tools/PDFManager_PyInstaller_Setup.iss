; -- Inno Setup Script for PDF Manager 1.0.0

#define SourceDir        ".."
#define MyAppName         "PDF Manager"
#define MyAppVersion      "1.0.0"
#define MyAppPublisher    "Mohammed Hank"
#define MyAppURL          "https://github.com/mohammedhank91"
#define MyAppExeName      "PDFManager.exe"
#define MyAppIcon         "..\src\resources\manage_pdf.ico"
#define MyAppLicenseFile  "..\LICENSE.txt"

[Setup]
; Basic Application Information
AppId={{F19E2C34-317D-4B27-9BEF-1A12D8D1E9A8}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
; Installer Settings
DisableStartupPrompt=yes
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=..\installer_64
OutputBaseFilename=PDFManager_Setup_v{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
; Architecture
ArchitecturesAllowed=x86 x64
ArchitecturesInstallIn64BitMode=x64
; UI Style
WizardStyle=modern
WizardSmallImageFile=..\src\resources\wizard_small.bmp
; Icon & License
SetupIconFile={#MyAppIcon}
UninstallDisplayIcon={app}\\manage_pdf.ico
LicenseFile={#MyAppLicenseFile}
; System Requirements
MinVersion=6.1
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french";  MessagesFile: "compiler:Languages\\French.isl"

[Components]
Name: "core"; Description: "Main application files"; Types: full compact custom; Flags: fixed
Name: "tools"; Description: "Portable Tools (ImageMagick, Poppler)"; Types: full custom

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Create a Quick&Launch icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; Core application files
Source: "..\dist\PDFManager\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion createallsubdirs; Components: core
Source: "{#MyAppIcon}"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; Portable tools (optional) — take them from your PyInstaller dist tree
Source: "..\dist\PDFManager\imagick_portable_64\*"; DestDir: "{app}\imagick_portable_64"; Flags: recursesubdirs ignoreversion createallsubdirs; Components: tools
Source: "..\dist\PDFManager\poppler_portable_64\*";   DestDir: "{app}\poppler_portable_64";   Flags: recursesubdirs ignoreversion createallsubdirs; Components: tools

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\manage_pdf.ico"; Components: core
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; Components: core
Name: "{group}\{#MyAppName} &Quick Launch"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon; Components: core
Name: "{group}\Visit &Publisher Website"; Filename: "{#MyAppURL}"; WorkingDir: "{app}"

[Registry]
; File association for .pdf
Root: HKCR; Subkey: ".pdf\OpenWithProgids"; ValueType: string; ValueName: "PDFManager.pdf"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCR; Subkey: "PDFManager.pdf"; ValueType: string; ValueName: ""; ValueData: "{#MyAppName}"; Flags: uninsdeletekey
Root: HKCR; Subkey: "PDFManager.pdf\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\manage_pdf.ico,0"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "PDFManager.pdf\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletevalue

[InstallDelete]
Type: files; Name: "{app}\\temp\\*.*"
Type: dirifempty; Name: "{app}\\temp"

[UninstallDelete]
Type: files; Name: "{userappdata}\\PDF Manager\\*.*"
Type: dirifempty; Name: "{userappdata}\\PDF Manager"

[Code]
// Prevent installation if application is running
function InitializeSetup(): Boolean;
begin
  if CheckForMutexes('PDFManagerMutex') then
  begin
    MsgBox(ExpandConstant('"{#MyAppName}" is currently running. Please close it and retry.'), mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;

// Show custom welcome message
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpWelcome then
    MsgBox('Welcome to the ' + ExpandConstant('{#MyAppName} Setup') + ' wizard.', mbInformation, MB_OK);
end;

// End of script
