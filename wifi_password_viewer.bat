@echo off
@echo off
setlocal enabledelayedexpansion
title WiFi Password Viewer v4.1

:menu
cls
echo.
echo ============================================
echo          WiFi Password Viewer v4.1
echo ============================================
echo.
echo   Saved WiFi Profiles:
echo.
echo --------------------------------------------

set "count=0"
for /f "tokens=1* delims=:" %%a in ('netsh wlan show profiles') do (
    set "name=%%b"
    if defined name if "!name:~0,1!"==" " set "name=!name:~1!"
    if defined name (
        set /a count+=1
        set "wifi!count!=!name!"
        echo     [!count!] !name!
    )
)

if "%count%"=="0" echo   [INFO] No saved WiFi profiles found.

echo.
echo     [S] Scan nearby WiFi
echo     [0] Exit
echo.
echo --------------------------------------------
echo.
set "choice="
set /p "choice=Enter number / option: "

if /i "%choice%"=="0" goto :bye
if /i "%choice%"=="s" goto :scan
if not defined choice goto :menu

set "valid=0"
for /l %%i in (1,1,%count%) do (
    if "%choice%"=="%%i" set "valid=1"
)
if "!valid!"=="0" goto :menu
set "selectedWifi=!wifi%choice%!"

:showPwd
cls
echo.
echo ============================================
echo   WiFi Name: !selectedWifi!
echo ============================================
echo.
echo   Password:
echo   --------------------------------------------
netsh wlan show profile name="!selectedWifi!" key=clear > "%TEMP%\wifi_pwd_tmp.txt"
powershell -NoProfile -Command "$k=([string][char]0x5173+[char]0x952E+[char]0x5185+[char]0x5BB9); $f=Join-Path $env:TEMP 'wifi_pwd_tmp.txt'; $found=$false; foreach($l in (Get-Content -LiteralPath $f -Encoding Default -ErrorAction SilentlyContinue)){ if($l -match ':' -and ($l -match $k -or $l -match 'Key Content')){ Write-Output ('    ' + ($l -split ':',2)[1].Trim()); $found=$true; break } }; if(-not $found){ Write-Output '    (No password found)' }"
del "%TEMP%\wifi_pwd_tmp.txt" >nul 2>&1
echo.
echo ============================================
echo.
echo   [M] Back to List
echo   [D] Full Details
echo   [S] Scan Nearby
echo   [0] Exit
echo.
set "back="
set /p "back=Choose an option: "
if /i "%back%"=="0" goto :bye
if /i "%back%"=="m" goto :menu
if /i "%back%"=="s" goto :scan
if /i "%back%"=="d" goto :fullDetails
goto :showPwd

:fullDetails
cls
echo.
echo ============================================
echo   Full Details: !selectedWifi!
echo ============================================
echo.
netsh wlan show profile name="!selectedWifi!" key=clear
echo.
echo ============================================
pause
goto :showPwd

:scan
cls
echo.
echo ============================================
echo   Scanning nearby WiFi networks...
echo ============================================
echo.
netsh wlan show networks mode=bssid
echo.
echo ============================================
echo.
echo   [M] Back to List
echo   [0] Exit
echo.
set "back="
set /p "back=Choose an option: "
if /i "%back%"=="0" goto :bye
if /i "%back%"=="m" goto :menu
goto :scan

:bye
echo.
echo   Thanks for using. Goodbye!
ping -n 3 127.0.0.1 >nul
exit /b