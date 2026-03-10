# Requirements Document

## Introduction

기존 마크다운 파일 기반 프롬프트 라이브러리(461개, 8개 카테고리)를 SQLite DB 기반 관리 앱으로 전환한다. FastAPI 백엔드 REST API를 통해 프롬프트 CRUD, 버전 히스토리, 마이그레이션/익스포트를 제공하고, 기존 읽기 전용 SPA를 편집 가능한 웹 앱으로 확장한다. 기존 CLI와 MCP 서버와의 호환성을 유지한다.

## Glossary

- **Backend**: FastAPI 기반 Python 웹 서버로, REST API를 제공하는 서버 컴포넌트
- **Database**: SQLite 기반 저장소로, prompts 테이블과 versions 테이블을 포함
- **Web_App**: 브라우저에서 동작하는 프론트엔드 SPA로, 프롬프트 조회/편집/관리 UI를 제공
- **Editor**: Web_App 내 마크다운 편집 컴포넌트로, 실시간 미리보기를 지원
- **Migrator**: 기존 .md 파일에서 Database로 데이터를 가져오는 임포트 스크립트
- **Exporter**: Database에서 .md 파일로 데이터를 내보내는 익스포트 기능
- **Prompt**: 카테고리, 태그, 역할, 마크다운 본문을 포함하는 프롬프트 데이터 단위
- **Version**: Prompt의 특정 시점 스냅샷으로, 수정 시마다 자동 생성되는 이력 레코드

## Requirements

### Requirement 1: 데이터베이스 스키마 및 초기화

**User Story:** As a 개발자, I want SQLite 데이터베이스에 프롬프트를 구조화하여 저장하고 싶다, so that 파일 시스템 대신 DB 기반으로 효율적인 CRUD와 버전 관리가 가능하다.

#### Acceptance Criteria

1. WHEN the Backend starts for the first time, THE Database SHALL create a prompts 테이블 with columns: id (TEXT PRIMARY KEY), title (TEXT), category (TEXT), content (TEXT), tags (JSON), role (TEXT), origin (TEXT), source (TEXT), file_path (TEXT), created_at (DATETIME), updated_at (DATETIME)
2. WHEN the Backend starts for the first time, THE Database SHALL create a versions 테이블 with columns: id (INTEGER PRIMARY KEY AUTOINCREMENT), prompt_id (TEXT FOREIGN KEY), title (TEXT), content (TEXT), tags (JSON), version_number (INTEGER), created_at (DATETIME), change_summary (TEXT)
3. THE Database SHALL enforce a FOREIGN KEY constraint between versions.prompt_id and prompts.id
4. WHEN a prompt record is queried by category or tag, THE Database SHALL return results within 100ms for up to 500 records

### Requirement 2: 마크다운 파일에서 DB 마이그레이션

**User Story:** As a 개발자, I want 기존 461개 마크다운 파일을 SQLite DB로 임포트하고 싶다, so that 기존 프롬프트 자산을 DB 기반 시스템에서 활용할 수 있다.

#### Acceptance Criteria

1. WHEN the Migrator is executed, THE Migrator SHALL scan all .md files in the 8 category directories (rca, incident-response, application, infrastructure, security, data-ai, shared, techniques)
2. WHEN a .md file with YAML frontmatter is found, THE Migrator SHALL parse the frontmatter fields (category, source, origin, tags, role) and the markdown body separately
3. WHEN parsing is complete, THE Migrator SHALL insert each Prompt into the Database prompts 테이블 with the parsed metadata and content
4. WHEN a Prompt with the same id already exists in the Database, THE Migrator SHALL skip that record and log a warning message
5. WHEN the Migrator completes, THE Migrator SHALL print a summary showing total files scanned, successfully imported count, and skipped count
6. FOR ALL imported Prompts, reading from the Database then exporting to .md format SHALL produce content equivalent to the original .md file (round-trip property)

### Requirement 3: REST API를 통한 프롬프트 CRUD

**User Story:** As a 웹 앱 사용자, I want REST API를 통해 프롬프트를 생성, 조회, 수정, 삭제하고 싶다, so that 웹 인터페이스에서 프롬프트를 관리할 수 있다.

#### Acceptance Criteria

1. WHEN a GET request is sent to /api/prompts, THE Backend SHALL return a paginated list of Prompts with fields: id, title, category, tags, role, origin, updated_at
2. WHEN a GET request is sent to /api/prompts with query parameter q, THE Backend SHALL return Prompts where the title or content contains the search term
3. WHEN a GET request is sent to /api/prompts with query parameter category, THE Backend SHALL return only Prompts matching that category
4. WHEN a GET request is sent to /api/prompts with query parameter tag, THE Backend SHALL return only Prompts that include that tag in the tags list
5. WHEN a GET request is sent to /api/prompts/{id}, THE Backend SHALL return the full Prompt including content
6. WHEN a POST request is sent to /api/prompts with valid Prompt data, THE Backend SHALL create a new Prompt in the Database and return the created Prompt with HTTP 201
7. WHEN a PUT request is sent to /api/prompts/{id} with updated fields, THE Backend SHALL update the Prompt in the Database and set updated_at to the current timestamp
8. WHEN a DELETE request is sent to /api/prompts/{id}, THE Backend SHALL remove the Prompt and all associated Versions from the Database and return HTTP 204
9. IF a request references a Prompt id that does not exist, THEN THE Backend SHALL return HTTP 404 with an error message
10. IF a POST or PUT request contains invalid data (missing title or content), THEN THE Backend SHALL return HTTP 422 with validation error details

### Requirement 4: 버전 히스토리 관리

**User Story:** As a 웹 앱 사용자, I want 프롬프트 수정 시 이전 버전이 자동 저장되고 싶다, so that 변경 이력을 추적하고 필요 시 이전 버전으로 롤백할 수 있다.

#### Acceptance Criteria

1. WHEN a Prompt is updated via PUT /api/prompts/{id}, THE Backend SHALL save the current state as a new Version record before applying the update
2. THE Backend SHALL assign an auto-incrementing version_number to each Version within the same prompt_id scope
3. WHEN a GET request is sent to /api/prompts/{id}/versions, THE Backend SHALL return a list of all Versions for that Prompt ordered by version_number descending
4. WHEN a GET request is sent to /api/prompts/{id}/versions/{version_number}, THE Backend SHALL return the full content of that specific Version
5. WHEN a POST request is sent to /api/prompts/{id}/versions/{version_number}/restore, THE Backend SHALL replace the current Prompt content with the specified Version content and create a new Version recording the restore action
6. IF a restore request references a version_number that does not exist, THEN THE Backend SHALL return HTTP 404 with an error message

### Requirement 5: DB에서 마크다운 파일 익스포트

**User Story:** As a 개발자, I want DB의 프롬프트를 .md 파일로 익스포트하고 싶다, so that 기존 CLI와 MCP 서버가 파일 기반으로 계속 동작할 수 있다.

#### Acceptance Criteria

1. WHEN a GET request is sent to /api/export, THE Exporter SHALL generate .md files for all Prompts in the Database
2. WHEN generating a .md file, THE Exporter SHALL write YAML frontmatter containing category, source, origin, tags, role fields followed by the markdown content body
3. WHEN generating a .md file, THE Exporter SHALL place the file in the correct category directory based on the Prompt category field
4. WHEN the export completes, THE Exporter SHALL return a summary with total exported count and the output directory path
5. WHEN a POST request is sent to /api/export/sync, THE Exporter SHALL regenerate prompts.meta.yaml and web/data.json to synchronize with the current Database state

### Requirement 6: 웹 앱 프롬프트 목록 및 필터링

**User Story:** As a 웹 앱 사용자, I want 프롬프트를 카테고리, 태그, 키워드로 필터링하여 조회하고 싶다, so that 원하는 프롬프트를 빠르게 찾을 수 있다.

#### Acceptance Criteria

1. WHEN the Web_App loads, THE Web_App SHALL fetch the prompt list from the Backend API and display it in the sidebar
2. WHEN a user selects a category button, THE Web_App SHALL filter the displayed list to show only Prompts in that category
3. WHEN a user types in the search input, THE Web_App SHALL filter the displayed list to show Prompts matching the search term within 300ms of the last keystroke
4. WHEN a user selects a tag from the tag filter, THE Web_App SHALL filter the displayed list to show only Prompts containing that tag
5. WHEN a user selects a Prompt from the list, THE Web_App SHALL fetch the full Prompt content from the Backend API and display it in the viewer panel

### Requirement 7: 웹 앱 프롬프트 생성 및 편집

**User Story:** As a 웹 앱 사용자, I want 웹에서 프롬프트를 생성하고 편집하고 싶다, so that 파일을 직접 수정하지 않고도 프롬프트를 관리할 수 있다.

#### Acceptance Criteria

1. WHEN a user clicks the "새 프롬프트" button, THE Web_App SHALL display a creation form with fields for title, category (dropdown), tags (multi-input), role, and a markdown Editor
2. WHEN a user clicks the "편집" button on a Prompt, THE Web_App SHALL switch the viewer to edit mode, populating the Editor with the current content
3. WHILE a user is editing in the Editor, THE Editor SHALL display a real-time rendered preview of the markdown content in a side panel
4. WHEN a user clicks "저장" in the creation form, THE Web_App SHALL send a POST request to the Backend API and add the new Prompt to the list on success
5. WHEN a user clicks "저장" in the edit mode, THE Web_App SHALL send a PUT request to the Backend API and update the displayed content on success
6. WHEN a user clicks "삭제" on a Prompt and confirms the action, THE Web_App SHALL send a DELETE request to the Backend API and remove the Prompt from the list on success
7. IF the Backend API returns a validation error, THEN THE Web_App SHALL display the error message near the relevant form field

### Requirement 8: 웹 앱 버전 히스토리 UI

**User Story:** As a 웹 앱 사용자, I want 프롬프트의 버전 히스토리를 조회하고 이전 버전으로 롤백하고 싶다, so that 변경 이력을 확인하고 실수를 되돌릴 수 있다.

#### Acceptance Criteria

1. WHEN a user clicks the "히스토리" button on a Prompt, THE Web_App SHALL fetch and display a list of Versions with version_number, created_at, and change_summary
2. WHEN a user selects a specific Version from the history list, THE Web_App SHALL display the content of that Version in the viewer panel
3. WHEN a user clicks "이 버전으로 복원" on a selected Version, THE Web_App SHALL send a restore request to the Backend API and update the current Prompt content on success
4. IF the restore operation fails, THEN THE Web_App SHALL display an error notification without modifying the current content

### Requirement 9: 마크다운 에디터

**User Story:** As a 웹 앱 사용자, I want 마크다운 편집 시 구문 강조와 실시간 미리보기를 제공받고 싶다, so that 편집 경험이 향상되고 결과물을 즉시 확인할 수 있다.

#### Acceptance Criteria

1. THE Editor SHALL provide syntax highlighting for markdown content including headings, bold, italic, code blocks, and lists
2. WHILE a user types in the Editor, THE Editor SHALL update the rendered preview within 200ms of the last keystroke
3. THE Editor SHALL support code block syntax highlighting for common languages (python, yaml, json, bash, javascript)
4. WHEN a user pastes content into the Editor, THE Editor SHALL preserve the original formatting of the pasted text
