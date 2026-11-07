# Build a raw.bytes-branded Windows desktop distribution.
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B tools/branding_guard.py --check
if ($LASTEXITCODE -ne 0) { throw 'Branding guard failed' }
python -m PyInstaller --noconfirm --clean --windowed --name ElectricalEngineeringSuite --add-data 'database/schema.sql;database' main.py
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed' }
$iscc = @('C:\Program Files (x86)\Inno Setup 6\ISCC.exe', 'C:\Program Files\Inno Setup 6\ISCC.exe') | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($iscc) {
    & $iscc 'installer/rawbytes.iss'
    if ($LASTEXITCODE -ne 0) { throw 'Inno Setup installer failed' }
    Write-Output 'Installer created under dist/installer/'
} else {
    Write-Warning 'Inno Setup 6 not installed. Portable Windows application built in dist/ElectricalEngineeringSuite/. Install Inno Setup 6 and rerun to create the Setup.exe installer.'
}
