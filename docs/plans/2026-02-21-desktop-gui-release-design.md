# Desktop GUI Release Design

## Goal
Build a Windows desktop GUI for non-developers that wraps the existing filename normalization logic, supports safe preview-before-apply flow, and ships as both portable `.exe` and installer package.

## Scope
- Windows only
- Core flow: folder selection -> preview -> apply
- Preview includes mapping and warnings (conflict/reserved/duplicate risk)
- Release output includes:
  - portable executable
  - installer executable
  - checksums
  - CI tag-based release automation

## Architecture
- `src/file_name_renamer.py`: core rename rules and plan generation (reused)
- `src/gui_app.py`: Tkinter desktop application
- `src/app_services.py`: bridge layer between GUI and core logic
- `scripts/build.ps1`: local build script (portable + installer)
- `.github/workflows/release.yml`: tag-triggered CI build and release

GUI depends on service layer only. Service layer calls core functions. Core remains UI-agnostic.

## Components
- FolderPicker: choose target folder path
- OptionPanel: recursive, separator, case, hidden, extensions
- PreviewTable: original name, new name, warning status
- ActionBar: preview/apply controls
- ResultSummary: processed, changed, failed counts with errors

## Data Flow
1. User selects folder and options.
2. App gathers candidate files and generates rename plan.
3. Service annotates each planned rename with warning info.
4. Preview table renders all rename candidates.
5. User clicks apply.
6. Service performs rename operations and reports per-file results.
7. UI renders summary and failures.

## Error Handling
- Invalid folder path: block action with explicit message.
- File access error: continue processing others and record file-level failure.
- Conflict possibility: flagged in preview before apply.
- No planned changes: explicit no-op message.

## Testing Strategy
- Unit tests for service warning annotations.
- Unit tests for rename flow summary and failure handling.
- Existing core behavior remains covered by new focused tests.

## Packaging And Release
- Portable build: PyInstaller one-file executable.
- Installer build: Inno Setup script generated from app metadata.
- CI pipeline:
  - trigger on version tags
  - build portable + installer
  - generate SHA256 checksums
  - publish GitHub release assets

## Non-Goals
- macOS/Linux support in this release
- per-file selective apply in preview
- real-time folder watcher mode
