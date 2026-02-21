param(
    [string]$Version = "dev",
    [string]$OutputDir = "artifacts",
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"

function Resolve-IsccPath {
    $candidates = @(
        "$env:ProgramFiles(x86)\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
    )

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) {
            return $candidate
        }
    }

    try {
        $fromPath = (Get-Command ISCC.exe -ErrorAction Stop).Source
        if ($fromPath) {
            return $fromPath
        }
    }
    catch {
        return $null
    }

    return $null
}

function Write-Sha256([string]$FilePath) {
    $hash = (Get-FileHash -Path $FilePath -Algorithm SHA256).Hash.ToLower()
    $fileName = Split-Path -Path $FilePath -Leaf
    $shaPath = "$FilePath.sha256"
    Set-Content -Path $shaPath -Value "$hash  $fileName" -NoNewline
    return $shaPath
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

$buildPath = Join-Path $repoRoot ".tmp/build"
$specPath = Join-Path $repoRoot ".tmp/spec"
New-Item -ItemType Directory -Path $buildPath -Force | Out-Null
New-Item -ItemType Directory -Path $specPath -Force | Out-Null

python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name "file-name-renamer" `
    "src/gui_app.py" `
    --distpath $OutputDir `
    --workpath $buildPath `
    --specpath $specPath

$safeVersion = $Version.Trim()
if ([string]::IsNullOrWhiteSpace($safeVersion)) {
    $safeVersion = "dev"
}

$portableExe = Join-Path $repoRoot "$OutputDir/file-name-renamer.exe"
if (-not (Test-Path $portableExe)) {
    throw "Portable exe was not produced: $portableExe"
}

$versionedPortable = Join-Path $repoRoot "$OutputDir/file-name-renamer-$safeVersion-portable-windows-x64.exe"
Copy-Item -Path $portableExe -Destination $versionedPortable -Force

$portableSha = Write-Sha256 -FilePath $portableExe
$versionedPortableSha = Write-Sha256 -FilePath $versionedPortable

if ($SkipInstaller) {
    Write-Host "Portable build complete."
    Write-Host "Artifacts:"
    Write-Host " - $portableExe"
    Write-Host " - $portableSha"
    Write-Host " - $versionedPortable"
    Write-Host " - $versionedPortableSha"
    exit 0
}

$isccPath = Resolve-IsccPath
$installerExe = Join-Path $repoRoot "$OutputDir/file-name-renamer-$safeVersion-setup-windows-x64.exe"
if ($isccPath) {
    & $isccPath "/DMyAppVersion=$safeVersion" "installer/file-name-renamer.iss"
}
else {
    Write-Host "ISCC.exe not found; creating setup fallback from portable executable."
    Copy-Item -Path $versionedPortable -Destination $installerExe -Force
}
if (-not (Test-Path $installerExe)) {
    throw "Installer was not produced: $installerExe"
}

$installerSha = Write-Sha256 -FilePath $installerExe

Write-Host "Build complete."
Write-Host "Artifacts:"
Write-Host " - $portableExe"
Write-Host " - $portableSha"
Write-Host " - $versionedPortable"
Write-Host " - $versionedPortableSha"
Write-Host " - $installerExe"
Write-Host " - $installerSha"
