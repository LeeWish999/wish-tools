@echo off
:: pdf_to_png.bat —— PDF 转逐页 PNG（无界面入口）：调用同目录 pdf2png_worker.py
:: 输出：output\pdf-to-png\ ；根目录可用环境变量 OCR_OUT_ROOT 覆盖
:: 解释器：环境变量 OCR_PYTHON → 本目录 .venv / venv → PATH 中的 python
title PDF 转图片（逐页 PNG）

set "BASE=%~dp0"
set "OUTROOT=%BASE%output\pdf-to-png"
if defined OCR_OUT_ROOT set "OUTROOT=%OCR_OUT_ROOT%\pdf-to-png"
set "PY=%OCR_PYTHON%"
if not defined PY if exist "%BASE%.venv\Scripts\python.exe" set "PY=%BASE%.venv\Scripts\python.exe"
if not defined PY if exist "%BASE%venv\Scripts\python.exe" set "PY=%BASE%venv\Scripts\python.exe"
if not defined PY set "PY=python"

:menu
cls
echo ========================================
echo  PDF 转图片 - 输出到 %OUTROOT%
echo  Python: %PY%
echo ========================================
echo  [1] 单个 PDF 转图片
echo  [2] 批量处理（选一个文件夹，转换里面所有 PDF）
echo  [3] 退出
echo ========================================
choice /c 123 /n /m "请选择 (1/2/3): "
if errorlevel 3 goto end
if errorlevel 2 goto batch
if errorlevel 1 goto single

:single
set "PICKER=%TEMP%\fp_%RANDOM%.ps1"
> "%PICKER%" echo Add-Type -AssemblyName System.Windows.Forms
>> "%PICKER%" echo $form = New-Object System.Windows.Forms.Form -Property @{TopMost=$true; ShowInTaskbar=$false}
>> "%PICKER%" echo $fb = New-Object System.Windows.Forms.OpenFileDialog
>> "%PICKER%" echo $fb.Filter = 'PDF files (*.pdf)^|*.pdf'
>> "%PICKER%" echo $fb.Title = '请选择要转换的 PDF 文件'
>> "%PICKER%" echo if ($fb.ShowDialog($form) -eq [System.Windows.Forms.DialogResult]::OK) { Write-Output $fb.FileName }
set "TARGET="
for /f "usebackq delims=" %%i in (`powershell -NoProfile -STA -ExecutionPolicy Bypass -File "%PICKER%"`) do set "TARGET=%%i"
del "%PICKER%" 2>nul
if not defined TARGET (echo 已取消。 & timeout /t 1 >nul & goto menu)
"%PY%" "%BASE%pdf2png_worker.py" "%TARGET%"
goto next

:batch
set "PICKER=%TEMP%\fp_%RANDOM%.ps1"
> "%PICKER%" echo Add-Type -AssemblyName System.Windows.Forms
>> "%PICKER%" echo $form = New-Object System.Windows.Forms.Form -Property @{TopMost=$true; ShowInTaskbar=$false}
>> "%PICKER%" echo $fb = New-Object System.Windows.Forms.FolderBrowserDialog
>> "%PICKER%" echo $fb.Description = '请选择包含 PDF 的文件夹（批量转换）'
>> "%PICKER%" echo if ($fb.ShowDialog($form) -eq [System.Windows.Forms.DialogResult]::OK) { Write-Output $fb.SelectedPath }
set "TARGET="
for /f "usebackq delims=" %%i in (`powershell -NoProfile -STA -ExecutionPolicy Bypass -File "%PICKER%"`) do set "TARGET=%%i"
del "%PICKER%" 2>nul
if not defined TARGET (echo 已取消。 & timeout /t 1 >nul & goto menu)
if not exist "%TARGET%\*.pdf" (
    echo.
    echo [提示] 该文件夹里没有 PDF 文件。
    timeout /t 1 >nul
    goto next
)
for %%f in ("%TARGET%\*.pdf") do "%PY%" "%BASE%pdf2png_worker.py" "%%~ff"
goto next

:next
echo.
echo 任务结束，按任意键返回主菜单...
pause >nul
if exist "%OUTROOT%" explorer "%OUTROOT%"
goto menu

:end
echo 已退出。
timeout /t 1 >nul
