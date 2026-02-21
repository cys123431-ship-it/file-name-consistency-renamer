param(
    [string]$Owner = "cys123431-ship-it",
    [string]$Repo = "file-name-consistency-renamer",
    [string]$Version = "v1.1.0",
    [string]$Branch = "",
    [switch]$BuildLocal,
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"

# Hard-disable all interactive auth prompts.
$env:GCM_INTERACTIVE = "Never"
$env:GIT_TERMINAL_PROMPT = "0"

if (-not (git rev-parse --is-inside-work-tree 2>$null)) {
    throw "Current folder is not a git repository."
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

if ([string]::IsNullOrWhiteSpace($Branch)) {
    $Branch = (git branch --show-current).Trim()
}
if ([string]::IsNullOrWhiteSpace($Branch)) {
    throw "Could not detect current branch."
}

if ($BuildLocal) {
    $args = @(
        "-ExecutionPolicy", "Bypass",
        "-File", "scripts/build.ps1",
        "-Version", $Version
    )
    if ($SkipInstaller) {
        $args += "-SkipInstaller"
    }
    powershell @args
}

$status = (git status --porcelain)
if ($status) {
    throw "Working tree is not clean. Commit or stash changes before publish."
}

if (-not (git remote | Select-String "^origin$")) {
    git remote add origin "https://github.com/$Owner/$Repo.git"
}

git push -u origin $Branch

if (-not (git tag -l $Version)) {
    git tag -a $Version -m "Release $Version"
}
git push origin $Version

Write-Host "Tag pushed:" $Version
Write-Host "Release is created by GitHub Actions workflow on tag push."
Write-Host "URL:" "https://github.com/$Owner/$Repo/releases/tag/$Version"
