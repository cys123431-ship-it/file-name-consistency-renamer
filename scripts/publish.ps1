param(
    [string]$Owner = "cys123431-ship-it",
    [string]$Repo = "file-name-consistency-renamer",
    [string]$Version = "v1.0.0",
    [string]$ReleaseName = "File Name Consistency Renamer v1.0.0",
    [switch]$ForceCreateRepo
)

$ErrorActionPreference = "Stop"

$token = $env:GITHUB_TOKEN
if (-not $token) {
    $token = $env:GH_TOKEN
}
if (-not $token) {
    throw "GITHUB_TOKEN 또는 GH_TOKEN 환경변수가 필요합니다."
}

$Headers = @{
    Authorization = "token $token"
    Accept = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

if (-not (git rev-parse --is-inside-work-tree 2>$null)) {
    throw "현재 폴더가 Git 저장소가 아닙니다."
}

git add .
git commit -m "feat: initial release implementation" --allow-empty

if (-not (git remote | Select-String "^origin$")) {
    git remote add origin "https://github.com/$Owner/$Repo.git"
}

if ($ForceCreateRepo) {
    $createBody = @{
        name = $Repo
        description = "Windows-friendly filename consistency renamer"
        private = $false
        auto_init = $false
    } | ConvertTo-Json

    Invoke-RestMethod -Method Post -Uri "https://api.github.com/user/repos" -Headers $Headers -Body $createBody | Out-Null
}

git checkout -B main
git push -u origin main

if (-not (git tag -l $Version)) {
    git tag $Version
    git push origin $Version
}

$release = @{
    tag_name = $Version
    name = $ReleaseName
    target_commitish = "main"
    draft = $false
    prerelease = $false
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "https://api.github.com/repos/$Owner/$Repo/releases" -Headers $Headers -Body $release | Out-Null

Write-Host "Release '$Version' created. URL:" "https://github.com/$Owner/$Repo/releases/tag/$Version"
