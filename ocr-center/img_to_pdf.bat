@echo off
:: img_to_pdf.bat —— 图片合成"图片型 PDF"（无界面入口）：调用同目录 img2pdf_worker.py
:: 输出：output\img-to-pdf\ ；根目录可用环境变量 OCR_OUT_ROOT 覆盖
:: 解释器：环境变量 OCR_PYTHON → 本目录 .venv / venv → PATH 中的 python
title 图片合成PDF（图片型PDF）

set "BASE=%~dp0"
set "OUTROOT=%BASE%output\img-to-pdf"
if defined OCR_OUT_ROOT set "OUTROOT=%OCR_OUT_ROOT%\img-to-pdf"
set "PY=%OCR_PYTHON%"
if not defined PY if exist "%BASE%.venv\Scripts\python.exe" set "PY=%BASE%.venv\Scripts\python.exe"
if not defined PY if exist "%BASE%venv\Scripts\python.exe" set "PY=%BASE%venv\Scripts\python.exe"
if not defined PY set "PY=python"

:menu
cls
echo ========================================
echo  图片合成PDF - 输出到 %OUTROOT%
echo  Python: %PY%
echo ========================================
echo  [1] 单个文件夹（把一整套图片合成一个 PDF）
echo  [2] 批量处理（选一个总文件夹，里面每个子文件夹各合成一个 PDF）
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
>> "%PICKER%" echo $fb = New-Object System.Windows.Forms.FolderBrowserDialog
>> "%PICKER%" echo $fb.Description = '请选择包含图片的文件夹（单套图片）'
>> "%PICKER%" echo if ($fb.ShowDialog($form) -eq [System.Windows.Forms.DialogResult]::OK) { Write-Output $fb.SelectedPath }
set "TARGET="
for /f "usebackq delims=" %%i in (`powershell -NoProfile -STA -ExecutionPolicy Bypass -File "%PICKER%"`) do set "TARGET=%%i"
del "%PICKER%" 2>nul
if not defined TARGET (echo 已取消。 & timeout /t 1 >nul & goto menu)
"%PY%" "%BASE%img2pdf_worker.py" "%TARGET%"
goto next

:batch
set "PICKER=%TEMP%\fp_%RANDOM%.ps1"
> "%PICKER%" echo Add-Type -AssemblyName System.Windows.Forms
>> "%PICKER%" echo $form = New-Object System.Windows.Forms.Form -Property @{TopMost=$true; ShowInTaskbar=$false}
>> "%PICKER%" echo $fb = New-Object System.Windows.Forms.FolderBrowserDialog
>> "%PICKER%" echo $fb.Description = '请选择总文件夹（其下每个子文件夹将各合成一个 PDF）'
>> "%PICKER%" echo if ($fb.ShowDialog($form) -eq [System.Windows.Forms.DialogResult]::OK) { Write-Output $fb.SelectedPath }
set "TARGET="
for /f "usebackq delims=" %%i in (`powershell -NoProfile -STA -ExecutionPolicy Bypass -File "%PICKER%"`) do set "TARGET=%%i"
del "%PICKER%" 2>nul
if not defined TARGET (echo 已取消。 & timeout /t 1 >nul & goto menu)
for /d %%d in ("%TARGET%\*") do "%PY%" "%BASE%img2pdf_worker.py" "%%~fd"
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
