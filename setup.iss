; setup.iss - WordBook 安装脚本
; 要求 Inno Setup 6 或更高版本

[Setup]
AppName=WordBook
AppVersion=0.1.2
AppPublisher=喵布
DefaultDirName={pf}\WordBook
DefaultGroupName=WordBook
UninstallDisplayIcon={app}\WordBook.exe
LicenseFile=LICENSE
Compression=lzma2/ultra
SolidCompression=yes
InternalCompressLevel=ultra
DisableProgramGroupPage=no
DisableDirPage=no
AllowRootDirectory=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
OutputDir=installer
OutputBaseFilename=WordBook_Setup
SetupIconFile=resources\icons\app_icon.ico
Uninstallable=yes
; 高压缩设置
LZMAUseSeparateProcess=yes
LZMAAlgorithm=1
LZMANumFastBytes=273
; 安装程序版本信息
VersionInfoVersion=0.1.2
VersionInfoCompany=喵布
VersionInfoDescription=WordBook 安装程序
VersionInfoCopyright=喵布

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "创建快速启动栏图标"; GroupDescription: "附加图标"; Flags: checkedonce; MinVersion: 4,4

[Files]
; 将 dist 目录下所有文件复制到应用目录（保持目录结构）
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "wordbook.db,user\*,backup\*,logs\*,data\wordbook.db,data\user\*,data\backup\*,data\logs\*"

[Icons]
Name: "{group}\WordBook"; Filename: "{app}\WordBook.exe"
Name: "{group}\卸载 WordBook"; Filename: "{uninstallexe}"
Name: "{commondesktop}\WordBook"; Filename: "{app}\WordBook.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\WordBook"; Filename: "{app}\WordBook.exe"; Tasks: quicklaunchicon

[Run]
; 安装完成后运行程序（可选）
Filename: "{app}\WordBook.exe"; Description: "启动 WordBook"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
; 卸载时仅删除空数据目录，保留用户数据（防止误删收藏等）
Type: dirifempty; Name: "{app}\data\logs"
Type: dirifempty; Name: "{app}\data\backup"
Type: dirifempty; Name: "{app}\data\user"
Type: dirifempty; Name: "{app}\data"

[Registry]
; 添加卸载信息到注册表，使控制面板可识别
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\WordBook"; ValueType: string; ValueName: "DisplayName"; ValueData: "WordBook"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\WordBook"; ValueType: string; ValueName: "Publisher"; ValueData: "喵布"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\WordBook"; ValueType: string; ValueName: "DisplayIcon"; ValueData: "{app}\WordBook.exe"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\WordBook"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "0.1.2"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\WordBook"; ValueType: string; ValueName: "UninstallString"; ValueData: """{uninstallexe}"""
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\WordBook"; ValueType: dword; ValueName: "NoModify"; ValueData: "1"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\WordBook"; ValueType: dword; ValueName: "NoRepair"; ValueData: "1"
