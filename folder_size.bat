@echo off
setlocal
set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=%CD%"

echo 正在统计: %TARGET%
echo 提示: 建议右键本文件选择"以管理员身份运行"，否则部分文件夹只能统计到部分内容
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$base = $env:TARGET;" ^
  "$dirs = Get-ChildItem -LiteralPath $base -Directory -Force -ErrorAction SilentlyContinue;" ^
  "$rows = foreach ($dir in $dirs) {" ^
  "  Write-Host ('  [扫描] ' + $dir.Name);" ^
  "  $bytes = 0; $failed = 0; $note = '';" ^
  "  $log = @(robocopy $dir.FullName NULL /L /S /NJH /BYTES /NC /NDL /NFL /NP /XJ /R:0 /W:0 /MT:16 2>&1);" ^
  "  $numRow = $log | Where-Object { $_ -match '^[^:]*:\s*[\d\s]+\s*$' } | Select-Object -Last 1;" ^
  "  if ($numRow) { $nums = (($numRow -split ':')[1] -split '\s+') | Where-Object { $_ -ne '' }; $bytes = [int64]$nums[0]; if ($nums.Count -gt 4) { $failed = [int64]$nums[4] } };" ^
  "  if (-not $numRow) { $note = '解析失败-已用慢速扫描'; $errs = @(); $bytes = (Get-ChildItem -LiteralPath $dir.FullName -Recurse -File -Force -ErrorAction SilentlyContinue -ErrorVariable +errs | Measure-Object Length -Sum).Sum; if ($null -eq $bytes) { $bytes = 0 }; if ($errs.Count -gt 0) { $note = '部分无权限' } }" ^
  "  elseif ($failed -gt 0) { $note = '有未统计(权限)' };" ^
  "  [PSCustomObject]@{ Name=$dir.Name; GB=[math]::Round($bytes/1GB,3); MB=[math]::Round($bytes/1MB,2); Bytes=$bytes; 备注=$note }" ^
  "};" ^
  "$rows | Sort-Object Bytes -Descending | Select-Object Name,GB,MB,备注 | Format-Table -AutoSize;" ^
  "Write-Host ''; Write-Host ('共 {0} 个文件夹' -f $rows.Count)"

pause
