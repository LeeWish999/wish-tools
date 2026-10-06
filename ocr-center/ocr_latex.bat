@echo off
:: ocr_latex.bat —— 公式书 OCR（无界面入口）：调用同目录 ocr_worker.py
:: 输出：output\ocr\ ；根目录可用环境变量 OCR_OUT_ROOT 覆盖
:: 解释器：环境变量 OCR_PYTHON → 本目录 .venv / venv → PATH 中的 python
title 公式书 OCR - PaddleOCR-VL（LaTeX）

set "BASE=%~dp0"
set "OUTROOT=%BASE%output\ocr"
if defined OCR_OUT_ROOT set "OUTROOT=%OCR_OUT_ROOT%\ocr"
set "PY=%OCR_PYTHON%"
if not defined PY if exist "%BASE%.venv\Scripts\python.exe" set "PY=%BASE%.venv\Scripts\python.exe"
if not defined PY if exist "%BASE%venv\Scripts\python.exe" set "PY=%BASE%venv\Scripts\python.exe"
if not defined PY set "PY=python"

:menu
cls
echo ========================================
echo  公式书 OCR（LaTeX）- 输出到 %OUTROOT%
echo  Python: %PY%
echo ========================================
echo  [1] 单个 PDF 识别
echo  [2] 批量处理（选一个文件夹，识别里面所有 PDF）
echo  [3] 退出
echo ========================================
echo  提醒：若 Umi-OCR 正在运行，请先退出（占显存）。
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
>> "%PICKER%" echo $fb.Title = '请选择要识别的 PDF 文件'
>> "%PICKER%" echo if ($fb.ShowDialog($form) -eq [System.Windows.Forms.DialogResult]::OK) { Write-Output $fb.FileName }
set "TARGET="
for /f "usebackq delims=" %%i in (`powershell -NoProfile -STA -ExecutionPolicy Bypass -File "%PICKER%"`) do set "TARGET=%%i"
del "%PICKER%" 2>nul
if not defined TARGET (echo 已取消。 & timeout /t 1 >nul & goto menu)
echo.
echo [识别] %TARGET%
echo 模型加载较慢（首次尤甚），请耐心等待，勿关闭窗口...
"%PY%" "%BASE%ocr_worker.py" "%TARGET%"
goto next

:batch
set "PICKER=%TEMP%\fp_%RANDOM%.ps1"
> "%PICKER%" echo Add-Type -AssemblyName System.Windows.Forms
>> "%PICKER%" echo $form = New-Object System.Windows.Forms.Form -Property @{TopMost=$true; ShowInTaskbar=$false}
>> "%PICKER%" echo $fb = New-Object System.Windows.Forms.FolderBrowserDialog
>> "%PICKER%" echo $fb.Description = '请选择包含 PDF 的文件夹（批量识别）'
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
setlocal enabledelayedexpansion
set "LIST="
for %%f in ("%TARGET%\*.pdf") do set "LIST=!LIST! "%%~ff""
"%PY%" "%BASE%ocr_worker.py" !LIST!
endlocal
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
