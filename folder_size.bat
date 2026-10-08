@echo off
setlocal
set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=%CD%"

echo ����ͳ��: %TARGET%
echo ��ʾ: �����Ҽ����ļ�ѡ��"�Թ���Ա��������"�����򲿷��ļ���ֻ��ͳ�Ƶ���������
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$base = $env:TARGET;" ^
  "$dirs = Get-ChildItem -LiteralPath $base -Directory -Force -ErrorAction SilentlyContinue;" ^
  "$rows = foreach ($dir in $dirs) {" ^
  "  Write-Host ('  [ɨ��] ' + $dir.Name);" ^
  "  $bytes = 0; $failed = 0; $note = '';" ^
  "  $log = @(robocopy $dir.FullName NULL /L /S /NJH /BYTES /NC /NDL /NFL /NP /XJ /R:0 /W:0 /MT:16 2>&1);" ^
  "  $numRow = $log | Where-Object { $_ -match '^[^:]*:\s*[\d\s]+\s*$' } | Select-Object -Last 1;" ^
  "  if ($numRow) { $nums = (($numRow -split ':')[1] -split '\s+') | Where-Object { $_ -ne '' }; $bytes = [int64]$nums[0]; if ($nums.Count -gt 4) { $failed = [int64]$nums[4] } };" ^
  "  if (-not $numRow) { $note = '����ʧ��-��������ɨ��'; $errs = @(); $bytes = (Get-ChildItem -LiteralPath $dir.FullName -Recurse -File -Force -ErrorAction SilentlyContinue -ErrorVariable +errs | Measure-Object Length -Sum).Sum; if ($null -eq $bytes) { $bytes = 0 }; if ($errs.Count -gt 0) { $note = '������Ȩ��' } }" ^
  "  elseif ($failed -gt 0) { $note = '��δͳ��(Ȩ��)' };" ^
  "  [PSCustomObject]@{ Name=$dir.Name; GB=[math]::Round($bytes/1GB,3); MB=[math]::Round($bytes/1MB,2); Bytes=$bytes; ��ע=$note }" ^
  "};" ^
  "$rows | Sort-Object Bytes -Descending | Select-Object Name,GB,MB,��ע | Format-Table -AutoSize;" ^
  "Write-Host ''; Write-Host ('�� {0} ���ļ���' -f $rows.Count)"

pause
