# File Name Renamer (Windows)

Desktop GUI and CLI tool for normalizing file names on Windows with a safe preview-before-apply workflow.

## Features

- Folder-based batch rename
- Recursive scan option
- Separator option: `_`, `-`, `.`
- Case option: `lower`, `upper`, `preserve`
- Extension filtering
- Hidden file include/exclude
- Preview list before apply
- Collision-safe numbering (`_1`, `_2`, ...)
- Windows reserved name handling (`CON`, `PRN`, ...)

## Run (GUI)

```powershell
python src/gui_app.py
```

Recommended flow:

1. Select folder
2. Configure options
3. Click `Preview`
4. Review warnings
5. Click `Apply`

## Run (CLI)

```powershell
python src/file_name_renamer.py "C:\target-folder" --recursive --case lower --separator "_"
```

Dry run:

```powershell
python src/file_name_renamer.py "C:\target-folder" --dry-run
```

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Build Artifacts

Portable exe only:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 -Version v1.1.0 -SkipInstaller
```

Portable exe + installer:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 -Version v1.1.0
```

Installer generation uses Inno Setup if available; otherwise a setup-named fallback `.exe` is produced from the portable binary.

Artifacts are generated in `artifacts/`:

- `file-name-renamer.exe`
- `file-name-renamer-<version>-portable-windows-x64.exe`
- `file-name-renamer-<version>-setup-windows-x64.exe`
- matching `.sha256` files

## Publish Tag Release

```powershell
powershell -ExecutionPolicy Bypass -File scripts/publish.ps1 -Version v1.1.0 -Branch feat/gui-desktop-release -BuildLocal
```

Behavior:

- optional local build (`-BuildLocal`)
- push selected branch
- create/push annotated tag
- GitHub Actions `release.yml` publishes release assets

## CI Release

Tag push (`v*`) runs `.github/workflows/release.yml`:

1. Install Python deps
2. Install Inno Setup
3. Run unit tests
4. Build portable + installer artifacts
5. Upload release assets
