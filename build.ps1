# build.ps1 - WordBook 打包脚本 (Nuitka + Inno Setup)
# 要求：Python 3.8+，已安装 Nuitka, clang, upx, Inno Setup (iscc)，在 Developer Powershell for VS 14+ 中运行

param(
    [string]$OutputDir = "dist",
    [string]$BuildDir = "build",
    [string]$InnoSetupScript = "setup.iss"
)

# 切换到脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 清理旧的构建目录
if (Test-Path $BuildDir) {
    Remove-Item -Recurse -Force $BuildDir
}
if (Test-Path $OutputDir) {
    Remove-Item -Recurse -Force $OutputDir
}

# 检查必需的资源和源码目录
if (-not (Test-Path "resources")) {
    Write-Host "错误: resources 目录不存在，请确保程序资源已准备。"
    exit 1
}
if (-not (Test-Path "main.py")) {
    Write-Host "错误: 未找到 main.py，请确认在项目根目录执行此脚本。"
    exit 1
}

# 设置环境变量（可选）
$env:PYTHONHASHSEED = 0

Write-Host "开始使用 Nuitka 打包..."
# Nuitka 参数说明：
# --standalone             生成独立可执行文件夹
# --plugin-enable=pyside6  自动处理 PySide6 隐式导入
# --plugin-enable=upx      启用 UPX 压缩（需 upx 在 PATH）
# --clang                  使用 Clang 编译器（体积更小，速度更快）
# --lto=yes                启用链接时优化
# --windows-disable-console 隐藏控制台（GUI 程序）
# --windows-icon-from-ico  设置 exe 图标
# --include-data-dir       将资源目录复制到输出根目录（保持路径）
# --include-package        强制包含指定包（解决动态导入遗漏问题）
# --noinclude-pytest       不包含 pytest 测试框架（减小体积）
nuitka `
    --standalone `
    --plugin-enable=pyside6 `
    --plugin-enable=upx `
    --clang `
    --lto=yes `
    --windows-console-mode=disable `
    --windows-icon-from-ico="resources\icons\app_icon.ico" `
    --windows-product-name="WordBook" `
    --windows-file-version="0.1.1" `
    --include-data-dir="resources=resources" `
    --include-data-dir="data\graphics=data\graphics" `
    --include-package=PySide6.QtCore `
    --include-package=PySide6.QtGui `
    --include-package=PySide6.QtWidgets `
    --include-module=utils.load_settings `
    --include-module=utils.database `
    --include-module=utils.parser `
    --include-module=utils.query_worker `
    --include-module=utils.rebuild_worker `
    --include-module=handle.query_handle `
    --include-module=handle.quiz_handle `
    --include-module=graphics.main_window `
    --include-module=graphics.settings `
    --remove-output `
    --output-dir=$BuildDir `
    --output-filename="WordBook.exe" `
    main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "Nuitka 打包失败！"
    exit $LASTEXITCODE
}

# Nuitka 输出目录为 build/main.dist，移动到 $OutputDir
$DistSource = Join-Path $BuildDir "main.dist"
if (Test-Path $DistSource) {
    Move-Item -Path $DistSource -Destination $OutputDir -Force
    Write-Host "打包产物已移动到 $OutputDir"
}
else {
    Write-Host "错误: 未找到 $DistSource，请检查 Nuitka 输出。"
    exit 1
}

# 清理 build 目录
Remove-Item -Recurse -Force $BuildDir -ErrorAction SilentlyContinue

# 检查 Inno Setup 编译器是否可用
$iscc = Get-Command "iscc" -ErrorAction SilentlyContinue
if (-not $iscc) {
    Write-Host "警告：未找到 iscc，请安装 Inno Setup 并添加到 PATH。跳过安装包生成。"
    exit 0
}

if (-not (Test-Path $InnoSetupScript)) {
    Write-Host "错误：Inno Setup 脚本 $InnoSetupScript 不存在。"
    exit 1
}

# 生成安装包
Write-Host "开始生成 Inno Setup 安装包..."
iscc $InnoSetupScript

if ($LASTEXITCODE -eq 0) {
    Write-Host "安装包生成成功！"
}
else {
    Write-Host "安装包生成失败！"
    exit $LASTEXITCODE
}
