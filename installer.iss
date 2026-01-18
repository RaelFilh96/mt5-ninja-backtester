; Script de instalação para MT5 Ninja Backtester
; Requer Inno Setup 6.x - Download: https://jrsoftware.org/isdl.php

#define MyAppName "MT5 Ninja Backtester"
#define MyAppVersion "3.0"
#define MyAppPublisher "MT5 Ninja Tools"
#define MyAppURL "https://github.com/RaelFilh96/mt5-ninja-backtester"
#define MyAppExeName "MT5_Ninja_Backtester.exe"

[Setup]
; Identificador único do app (gerar novo GUID para seu app)
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Pasta de saída do instalador
OutputDir=installers
OutputBaseFilename=MT5_Ninja_Backtester_Setup_v3.0
; Ícone do instalador (opcional)
;SetupIconFile=icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
; Requer privilégios de admin para instalar em Program Files
PrivilegesRequired=admin
; Mostrar licença
LicenseFile=LICENSE

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Executável principal
Source: "MT5_Ninja_Backtester.exe"; DestDir: "{app}"; Flags: ignoreversion
; Arquivos de configuração
Source: "config.ini"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "coordenadas.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
; Documentação
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
; Pasta de sets (exemplo)
Source: "sets\*"; DestDir: "{app}\sets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}\sets\curvas"; Permissions: users-modify

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Verificar se MetaTrader 5 está instalado (opcional)
function IsMT5Installed: Boolean;
begin
  Result := DirExists(ExpandConstant('{pf}\MetaTrader 5')) or 
            DirExists(ExpandConstant('{pf64}\MetaTrader 5')) or
            DirExists(ExpandConstant('{localappdata}\Programs\MetaTrader 5'));
end;

procedure InitializeWizard;
begin
  if not IsMT5Installed then
  begin
    MsgBox('Aviso: MetaTrader 5 não foi detectado no sistema.' + #13#10 + 
           'Certifique-se de instalar o MT5 antes de usar este programa.', 
           mbInformation, MB_OK);
  end;
end;
