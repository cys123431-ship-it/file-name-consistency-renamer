# Desktop GUI Release Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deliver a Windows-only Tkinter desktop app for safe filename normalization with preview/apply flow and automated release artifacts (portable exe + installer).

**Architecture:** Keep rename rules in `src/file_name_renamer.py` and add a thin service layer for preview/apply behavior that the GUI calls. Keep GUI mostly wiring and state updates, with testable behavior moved into service/viewmodel helpers. Build and release assets with PowerShell scripts and a tag-triggered GitHub Actions workflow.

**Tech Stack:** Python 3 (standard library + Tkinter), `unittest`, PyInstaller, Inno Setup, GitHub Actions.

---

### Task 1: Add test harness and service contract tests

**Files:**
- Create: `tests/test_app_services.py`
- Create: `tests/__init__.py`
- Test: `tests/test_app_services.py`

**Step 1: Write the failing test**

```python
from pathlib import Path
from src.app_services import build_preview_rows


def test_preview_rows_include_warning_types(tmp_path: Path):
    (tmp_path / "CON.txt").write_text("x", encoding="utf-8")
    rows = build_preview_rows(
        root=tmp_path,
        recursive=False,
        include_hidden=False,
        extensions=[],
        separator="_",
        case_mode="preserve",
    )
    assert len(rows) == 1
    assert rows[0].warning in {"reserved-name", "none"}
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_app_services -v`  
Expected: FAIL with import error for `src.app_services`.

**Step 3: Write minimal implementation**

```python
def build_preview_rows(...):
    return []
```

**Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_app_services -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add tests/__init__.py tests/test_app_services.py src/app_services.py
git commit -m "test: add preview row service contract tests"
```

### Task 2: Implement preview + apply service with TDD

**Files:**
- Modify: `tests/test_app_services.py`
- Modify: `src/app_services.py`
- Test: `tests/test_app_services.py`

**Step 1: Write the failing tests**

```python
def test_preview_rows_returns_old_new_and_warning(...):
    ...

def test_apply_preview_plan_returns_success_and_failures(...):
    ...
```

**Step 2: Run tests to verify they fail**

Run: `python -m unittest tests.test_app_services -v`  
Expected: FAIL on missing fields/behavior.

**Step 3: Write minimal implementation**

```python
@dataclass
class PreviewRow:
    source: Path
    target: Path
    warning: str

@dataclass
class ApplySummary:
    attempted: int
    changed: int
    failed: int
```

Implement:
- preview generation from `gather_files` + `plan_renames`
- warning tagging (`none`, `name-conflict-risk`, `reserved-name`, `hidden-dotfile`)
- apply function with per-file exception capture

**Step 4: Run tests to verify they pass**

Run: `python -m unittest tests.test_app_services -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add tests/test_app_services.py src/app_services.py
git commit -m "feat: add app service for preview and apply summaries"
```

### Task 3: Add GUI viewmodel helpers with TDD

**Files:**
- Create: `tests/test_gui_viewmodel.py`
- Create: `src/gui_viewmodel.py`
- Test: `tests/test_gui_viewmodel.py`

**Step 1: Write the failing tests**

```python
def test_parse_extensions_input_normalizes_values():
    ...

def test_validate_folder_path_rejects_missing_dir():
    ...
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_gui_viewmodel -v`  
Expected: FAIL with missing module/functions.

**Step 3: Write minimal implementation**

```python
def parse_extensions_input(raw: str) -> list[str]:
    ...

def validate_folder_path(raw: str) -> tuple[bool, str]:
    ...
```

**Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_gui_viewmodel -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add tests/test_gui_viewmodel.py src/gui_viewmodel.py
git commit -m "feat: add gui viewmodel validation helpers"
```

### Task 4: Build Tkinter desktop app shell

**Files:**
- Create: `src/gui_app.py`
- Modify: `README.md`
- Test: `tests/test_app_services.py`
- Test: `tests/test_gui_viewmodel.py`

**Step 1: Write the failing test**

```python
def test_service_rows_can_be_rendered_as_table_values():
    # Keep GUI behavior test at service boundary.
    ...
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_app_services tests.test_gui_viewmodel -v`  
Expected: FAIL for missing helper/formatter.

**Step 3: Write minimal implementation**

Add GUI with:
- folder picker
- options panel
- preview table (`ttk.Treeview`)
- preview/apply buttons
- summary/error dialog

Add script entry:
- `python src/gui_app.py`

**Step 4: Run tests to verify they pass**

Run: `python -m unittest tests.test_app_services tests.test_gui_viewmodel -v`  
Expected: PASS.

**Step 5: Commit**

```bash
git add src/gui_app.py README.md tests/test_app_services.py
git commit -m "feat: add tkinter desktop app for preview and apply flow"
```

### Task 5: Add build scripts for portable exe and installer

**Files:**
- Create: `scripts/build.ps1`
- Create: `installer/file-name-renamer.iss`
- Modify: `requirements.txt`
- Modify: `README.md`

**Step 1: Write the failing check**

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 -SkipInstaller
```

Expected: FAIL before script exists.

**Step 2: Run failing check**

Run the command and observe missing file error.

**Step 3: Write minimal implementation**

Implement `scripts/build.ps1`:
- create virtual env (optional reuse)
- install `pyinstaller`
- build one-file gui exe
- compute SHA256
- optionally invoke Inno Setup (`ISCC.exe`) for installer

Implement `.iss` file:
- app metadata
- source exe include
- output installer naming

**Step 4: Run verification**

Run: `powershell -ExecutionPolicy Bypass -File scripts/build.ps1 -SkipInstaller`  
Expected: portable exe + sha256 in `artifacts/`.

**Step 5: Commit**

```bash
git add scripts/build.ps1 installer/file-name-renamer.iss requirements.txt README.md
git commit -m "build: add portable and installer packaging scripts"
```

### Task 6: Add tag-based CI release automation

**Files:**
- Modify: `.github/workflows/release.yml`
- Modify: `scripts/publish.ps1`
- Modify: `README.md`

**Step 1: Write the failing check**

Run: `python -m unittest tests.test_app_services tests.test_gui_viewmodel -v`  
Expected: PASS (baseline guard)  
Then run local workflow lint check if available (or parse YAML by script) and expect release job definitions missing before update.

**Step 2: Implement minimal workflow changes**

Add CI job on tag push:
- set up Python
- install build deps
- run tests
- run build script for portable+installer
- upload release assets via `gh release upload` or Actions release step

**Step 3: Verify changes**

Run:
- `python -m unittest tests.test_app_services tests.test_gui_viewmodel -v`
- `python src/gui_app.py --help` is not applicable for Tkinter; instead run import smoke:
  `python -c "import src.gui_app; print('ok')"`

Expected: tests pass + import smoke ok.

**Step 4: Commit**

```bash
git add .github/workflows/release.yml scripts/publish.ps1 README.md
git commit -m "ci: automate tagged desktop release assets"
```

### Task 7: Final verification and release

**Files:**
- Verify all modified files

**Step 1: Run full verification**

```bash
python -m unittest discover -s tests -v
powershell -ExecutionPolicy Bypass -File scripts/build.ps1 -SkipInstaller
git status --short
```

**Step 2: Create release tag**

```bash
git tag -a v1.1.0 -m "v1.1.0"
git push origin feat/gui-desktop-release
git push origin v1.1.0
```

**Step 3: Validate release artifacts**

Check GitHub release contains:
- portable `.exe`
- installer `.exe`
- `.sha256` files

**Step 4: Commit (if docs/changelog changed)**

```bash
git add README.md
git commit -m "docs: update release usage for desktop app"
```
