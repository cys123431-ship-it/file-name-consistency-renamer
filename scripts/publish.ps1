param(
    [string]$Owner = "cys123431-ship-it",
    [string]$Repo = "file-name-consistency-renamer",
    [string]$Version = "v1.0.0"
)

$ErrorActionPreference = "Stop"

# Hard-disable all interactive auth prompts.
$env:GCM_INTERACTIVE = "Never"
$env:GIT_TERMINAL_PROMPT = "0"

if (-not (git rev-parse --is-inside-work-tree 2>$null)) {
    throw "Current folder is not a git repository."
}

git add .
git commit -m "chore: release $Version" --allow-empty

if (-not (git remote | Select-String "^origin$")) {
    git remote add origin "https://github.com/$Owner/$Repo.git"
}

git checkout -B main
git push -u origin main

if (-not (git tag -l $Version)) {
    git tag $Version
}
git push origin $Version

Write-Host "Tag pushed:" $Version
Write-Host "Release is created by GitHub Actions workflow on tag push."
Write-Host "URL:" "https://github.com/$Owner/$Repo/releases/tag/$Version"
