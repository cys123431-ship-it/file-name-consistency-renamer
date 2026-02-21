# 파일명 일관 정리기 (Windows File Name Consistency Renamer)

특수문자/공백/대소문자 규칙을 통일해서 파일명을 일괄 정리하는 간단한 윈도우용 도구입니다.

## 주요 기능

- 폴더 내 파일명 일괄 정규화
- 재귀 탐색 옵션
- 구분자 지정 (`_`, `-`, `.`)
- 대소문자 규칙 지정 (`lower`, `upper`, `preserve`)
- 확장자 필터 옵션
- 숨김 파일 포함 옵션
- 변경 미리보기(`--dry-run`)
- 충돌 시 `_1`, `_2` 방식으로 자동 번호 처리

## 사용 방법

```powershell
python src/file_name_renamer.py "C:\정리할폴더" --recursive --case lower --separator "_"
```

### 미리보기만 보기

```powershell
python src/file_name_renamer.py "C:\정리할폴더" --dry-run
```

### 특정 확장자만 처리

```powershell
python src/file_name_renamer.py "C:\정리할폴더" --extensions .png .jpg .jpeg
```

### 한 번에 실행 스크립트

```bat
python src/file_name_renamer.py "%~1" --recursive
```

## 릴리스 및 배포

- 로컬에서 `.zip` 패키지를 만들기:

```powershell
Compress-Archive -Path src/file_name_renamer.py,README.md -DestinationPath file-name-renamer.zip
```

- GitHub 배포는 `scripts/publish.ps1`로 진행합니다.
- `GITHUB_TOKEN`/`GH_TOKEN`이 없으면, Git Credential Manager 로그인 정보를 자동 사용합니다.

## 동작 규칙

- Windows에서 금지된 파일명 문자(`<`, `>`, `:`, `"`, `/`, `\`, `|`, `?`, `*`)를 구분자로 치환
- 영문/숫자/한글/밑줄/마침표/하이픈 외 문자는 구분자로 치환
- 빈 이름은 `renamed_file`로 처리
- Windows 예약 이름(`CON`, `PRN`, `AUX`, `NUL`, `COM1~9`, `LPT1~9`)은 `_file`이 붙습니다.

## 옵션 정리

- `-r, --recursive`: 하위 폴더까지 재귀 처리
- `--separator`: `_`, `-`, `.` 중 하나
- `--case`: `lower` / `upper` / `preserve`
- `--include-hidden`: 점(`.`)으로 시작하는 파일도 포함
- `--extensions`: 처리할 확장자 목록 (예: `--extensions .txt .md`)
- `--dry-run`: 실제 변경 없이 출력만
