; Inno Setup script for packaging AI Teacher Quest
#define MyAppName "AI Teacher Quest"
#define MyAppVersion "1.0.0"
#define MyAppExeName "AI_Teacher_Quest.exe"
#define MyDistDir "..\dist\AI_Teacher_Quest"

[Setup]
AppId={{5AA00A54-8D03-4C47-9D7B-7F5E7D1976C7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=AI-Teacher-Quest-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Files]
Source: "{#MyDistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Создать ярлык на рабочем столе"; GroupDescription: "Дополнительные задачи:"

