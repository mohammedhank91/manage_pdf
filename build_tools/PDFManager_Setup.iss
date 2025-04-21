#define MyAppName "PDF Manager"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "mohammedhank91"
#define MyAppURL "https://github.com/mohammedhank91"
#define MyAppExeName "PDFManager.exe"
#define MyAppCopyright "Copyright © 2023-2024"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{F19E2C34-317D-4B27-9BEF-1A12D8D1E9A8}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright={#MyAppCopyright}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=..\installer_64
OutputBaseFilename=PDFManager_Setup
Compression=lzma2/ultra64
SolidCompression=yes
; "ArchitecturesInstallIn64BitMode=x64" requests that the install be
; done in "64-bit mode" on x64, meaning it should use the native
; 64-bit Program Files directory and the 64-bit view of the registry.
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x86 x64
; Add a nice background image and icon
WizardStyle=modern
WizardImageFile=..\src\resources\wizard_image.bmp
WizardSmallImageFile=..\src\resources\wizard_small.bmp
SetupIconFile=..\src\resources\manage_pdf.ico
UninstallDisplayIcon={app}\manage_pdf.ico
; Windows Vista or newer
MinVersion=6.0
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Allow user to change installation directory
AllowNoIcons=yes
; Sign the installer
;SignTool=signtool
ShowLanguageDialog=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
WelcomeLabel1=Welcome to the [name] Setup Wizard
WelcomeLabel2=This will install [name/ver] on your computer.%n%nIt is recommended that you close all other applications before continuing.
FinishedHeadingLabel=Completing the [name] Setup Wizard
FinishedLabel=Setup has finished installing [name] on your computer. The application may be launched by selecting the installed shortcuts.

[CustomMessages]
LaunchProgram=Launch PDF Manager after installation
DescriptionAppName=PDF Manager - A comprehensive tool for manipulating PDF files
AppIsRunning=PDF Manager is currently running. Please close it and then click Retry to continue, or Cancel to exit.

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; OnlyBelowVersion: 6.1; Flags: unchecked

[Files]
; NOTE: Don't use "Flags: ignoreversion" on any shared system files
Source: "..\build\exe.win-amd64-*\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\src\resources\manage_pdf.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\manage_pdf.ico"; Comment: "PDF Manager - Manage your PDF files"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; IconFilename: "{app}\manage_pdf.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\manage_pdf.ico"; Tasks: desktopicon; Comment: "PDF Manager - Manage your PDF files"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\manage_pdf.ico"; Tasks: quicklaunchicon; Comment: "PDF Manager - Manage your PDF files"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Add to "Open with" menu for PDF files
Root: HKCR; Subkey: ".pdf\OpenWithProgids"; ValueType: string; ValueName: "PDFManager.pdf"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCR; Subkey: "PDFManager.pdf"; ValueType: string; ValueName: ""; ValueData: "PDF Manager"; Flags: uninsdeletekey
Root: HKCR; Subkey: "PDFManager.pdf\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\manage_pdf.ico,0"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "PDFManager.pdf\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletevalue

[Code]
function InitializeSetup(): Boolean;
begin
  // Check if the application is running
  if CheckForMutexes('PDFManagerMutex') then
  begin
    MsgBox(ExpandConstant('{cm:AppIsRunning}'), mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end; 