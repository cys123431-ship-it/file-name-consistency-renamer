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

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )
    & git @Args
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Args -join ' ') failed with exit code $LASTEXITCODE"
    }
}

function Get-GitOutput {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )
    $output = & git @Args
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Args -join ' ') failed with exit code $LASTEXITCODE"
    }
    return $output
}

$insideWorkTree = Get-GitOutput -Args @("rev-parse", "--is-inside-work-tree")
if ($insideWorkTree.Trim() -ne "true") {
    throw "Current folder is not a git repository."
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

if ([string]::IsNullOrWhiteSpace($Branch)) {
    $Branch = (Get-GitOutput -Args @("branch", "--show-current")).Trim()
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
    if ($LASTEXITCODE -ne 0) {
        throw "Local build failed with exit code $LASTEXITCODE"
    }
}

$status = Get-GitOutput -Args @("status", "--porcelain")
if ($status) {
    throw "Working tree is not clean. Commit or stash changes before publish."
}

$remotes = Get-GitOutput -Args @("remote")
if (-not ($remotes | Select-String "^origin$")) {
    Invoke-Git -Args @("remote", "add", "origin", "https://github.com/$Owner/$Repo.git")
}

Invoke-Git -Args @("push", "-u", "origin", $Branch)

$existingTag = Get-GitOutput -Args @("tag", "-l", $Version)
if (-not $existingTag) {
    Invoke-Git -Args @("tag", "-a", $Version, "-m", "Release $Version")
}
Invoke-Git -Args @("push", "origin", $Version)

Write-Host "Tag pushed:" $Version
Write-Host "Release is created by GitHub Actions workflow on tag push."
Write-Host "URL:" "https://github.com/$Owner/$Repo/releases/tag/$Version"
