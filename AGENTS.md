# LLM Wiki Operating Schema — cs-study

본 파일은 AI 에이전트 (Claude Code / Cursor / Codex / Gemini 등) 가 본 vault 에서 동작할 때의 운영 규약이다. CLAUDE.md 가 사람 (사용자) 의 룰이라면 AGENTS.md 는 LLM 의 룰이다. 두 파일이 충돌 시 CLAUDE.md 가 우선.

## Mission

- 본 vault 는 사용자의 **개인 학습 위키 (CS · 보안 · 개발 · 코딩테스트 · 도구)** 이자 **LLM 학습/RAG ground truth** 이다.
- AI 에이전트는 vault 의 합성 페이지 (`wiki/`) 를 ground truth 로 소비할 수 있어야 한다. 정확도·전문성·일관성·논리성·정합성·재현성·시의성 + 규칙·원칙 준수 보장이 필수.

## Scope 분리 (B0 — Panel C 핵심 결정)

본 schema 는 **외부 LLM 호출** 만 통제한다. Claude Code 본체와 9 portfolio subagent 는 harness 영역.

| Layer | 모델 결정 주체 | 변경 방식 |
|---|---|---|
| Claude Code 본체 + 9 portfolio subagent (arch-cycle-detector, logic-proposition-checker, grounding-verifier 등) | harness 자동 | 사용자 `/model` 명령 |
| Ollama + 외부 LLM API 호출 (scripts/, Smart Connections plugin, LLM Tagger plugin) | `_meta/llm-config.yaml` profile alias | YAML 1곳 수정 |
| Hybrid (subagent 가 외부 LLM 호출) | 해당 subagent 의 prompt 가 `_meta/llm-config.yaml` alias 인용 | 동상 |

## Layered Architecture

| 등급 | 위치 | 변경권 (write) | 역할 |
|---|---|---|---|
| **raw** | immutable bundle `raw/sources/<source_type>/<source_id>/<digest>/`, legacy curated page `raw/sources/{papers,web,conversations,urls,video}/`, `raw/assets/` | LLM + 사용자 (capture / Web Clipper / legacy importer) | 외부 1차 자료. 원본 불변. wiki 합성 source |
| **authored** | `cs/`, `development/`, `coding-test/`, `lang/`, `tools/` | **사용자 only** (LLM read-only) | 사용자 1차 학습 노트. wiki 합성 source |
| **synthesis** | `wiki/{overview,index,domains/<domain>/,collections/,staging/,archive/,templates/,views/}` | 사용자 검토·정정 + deterministic pipeline (LLM은 semantic draft만 생성) | 합성 페이지. canonical knowledge |
| **project** | `projects/<project>/` | 사용자 + LLM | 실행 코드·테스트·프로젝트 문서. wiki 합성 대상이 아니며 필요한 지식 원본은 repo-relative path로 단방향 참조 |
| **schema** | `_meta/`, `scripts/`, `AGENTS.md` | 사용자 + LLM 공진화 | 운영 규약 |

**중요**:
- LLM 은 `cs/`, `development/`, `coding-test/`, `lang/`, `tools/` 의 어떤 파일도 수정·생성·삭제할 수 없다 (PreToolUse hook 강제).
- LLM 은 legacy curated `raw/sources/*.md`에 인용 보존 목적의 작은 frontmatter 보강만 가능하다. content-addressed bundle은 기존 bytes 수정 없이 새 digest revision만 추가한다.
- 사용자는 `wiki/`를 검토·정정할 수 있다. canonical write는 승인된 semantic plan을 deterministic renderer가 수행한다.
- `projects/` 는 `wiki/` migration·materialization·knowledge check 입력에 포함하지 않는다.
- `projects/**/*.md`는 일반 프로젝트 문서이며 `wiki/` frontmatter를 사용하지 않는다. 프로젝트 계약은 문서 본문과 실행 가능한 테스트가 소유한다.

## SoT 규약

- **cs/, development/, coding-test/, lang/, tools/ = authored SoT** (사람 1차 사실). frontmatter `tier: human-note`
- **wiki/ = synthesis SoT**. 현재 페이지 계약은 `_meta/knowledge.schema.json`의 최소 properties와 본문 section/table 계약이다.
- **projects/ = executable SoT**. 실행 코드·테스트·프로젝트 계약을 소유하며 canonical knowledge를 복제하지 않는다.
- **_meta/domains.yaml = domain registry SoT**. wiki domain 목록, active/inactive 상태, source root hint 는 이 파일에서만 관리한다.
- **_meta/taxonomy.md = vocabulary SoT**. tag/entity/concept controlled vocabulary 를 관리하며 domain registry 와 병합하지 않는다.
- **_meta/knowledge.schema.json = 현재 지식 문서·ArtifactManifest·SemanticPlan schema SoT**. `_meta/wiki-ingest-write-plan.schema.json`은 superseded v1 회귀 fixture이며 현재 CLI 입력이 아니다.
- 같은 사실이 양쪽에 존재 시 cs/는 authored 원본, wiki/는 합성·정제·인용 추적을 소유한다. target `source_paths`는 capture된 artifact manifest만 허용하며 authored 원본도 capture 후 인용한다.

## Cross-link

- **단방향 only**: wiki는 capture된 artifact manifest만 근거로 인용하며 `cs/development/ → wiki/` 자동 link는 금지한다.
- backlink와 inverse relation은 checker·Obsidian view가 outgoing edge에서 계산한다. persistent backlink index는 생성·소비하지 않는다.
- Obsidian graph view가 사람용 UX 시각화를 소유한다.

## Ingest

target ingest universe는 사용자가 명시한 artifact manifest 목록뿐이다. `raw/`, `cs/`, `development/`의 암묵 scan과 `wiki/` 재-ingest를 금지한다. 현재 legacy ingest 설명은 migration 전 기록이며 신규 CLI 규약이 아니다.

### Ingest 순서 (단일 source 최종 wiki 반영)

아래 순서는 source 가 wiki ground truth 로 최종 반영되는 일반 lifecycle 이다. 특정 MVP stage 는 이 순서의 일부만 수행할 수 있으며, 해당 stage 의 설계 문서가 범위를 더 좁게 제한하면 그 제한을 따른다.
raw/authored 입력은 선행 capture로 content-addressed artifact manifest를 만든 뒤에만 이 lifecycle에 들어온다.
1. 사용자가 명시한 artifact manifest와 결속된 immutable payload read
2. `_meta/domains.yaml` 기반 domain 분류 (low confidence, missing/inactive domain → `wiki/staging/domain-review/` 후 사람 검토)
3. 주요 claim·entity·concept 추출
4. wiki/domains/<domain>/sources/ 에 source summary 페이지 생성
5. wiki/domains/<domain>/{entities,concepts}/ 페이지 신규·갱신
6. 순서 8 이후 materializer가 index·overview를 derived-only로 재생성한다. 그 전 stage는 generated surface를 직접 갱신하지 않는다.
7. full check와 사용자 review 뒤 프로젝트 커밋 규약을 따른다.

target lifecycle은 위 1–7과 materializer의 index·overview derived-only 생성만 따른다.

## Query

1. `wiki/index.md` 읽고 관련 domain·페이지 식별
2. domain-local 페이지 우선, collection 페이지는 명시적 membership 탐색 시 사용
3. 답변에 인용 path inline
4. 유의미한 답변의 file-back이 필요하면 해당 `wiki/domains/<domain>/`의 적합한 canonical page를 갱신하고 새 질의 전용 root는 만들지 않는다

## Lint

`scripts/lint.py` 가 6축 + AGENTS.md directive 자동 검증. 사람 호출: `python3 scripts/lint.py`.

## Quality Bar — 6축 + directive

상세는 `_meta/quality-bar.md`. 요약:

| 축 | hard / soft | 자동 도구 |
|---|---|---|
| 1. 정확도 | hard | lint.py + grounding-verifier |
| 2. 전문성 | soft (LLM judge) | LLM judge (수동·주기) |
| 3. 일관성 | hard | lint.py + logic-proposition-checker (D2) |
| 4. 논리성 (페이지 간) | hard | logic-proposition-checker (D3 changed pages + 1-hop) |
| 4. 논리성 (페이지 내부) | soft (사람 review) | 사람 게이트 |
| 5. 정합성 | hard | lint.py + cross-linker |
| 6. 재현성·시의성 | canonical checker는 immutable artifact digest·manifest 존재와 current lifecycle 계약을 검사한다 | lint.py dispatcher + target checker |
| + directive | hard | lint.py |

## 사람 review 게이트

4 시점에 사람 review 필수:
1. PR 단위 1회
2. raw → wiki 승격 시점 (staging/domain-review/ → domains/)
3. target claim의 contradiction·insufficient review 상태 해소 시점
4. taxonomy supersede 시점 (ADR + alias)

페이지 단위·commit 단위 강제 게이트 금지.

## Frontmatter spec

상세 수명은 `_meta/frontmatter-spec.md`가 정의한다. 현재 wiki content는 `_meta/knowledge.schema.json`의 7개 필수 properties와 조건부 필드만 허용한다. legacy 15필드 절은 historical non-normative다.

## Page type

현재 page type enum과 섹션은 `_meta/knowledge.schema.json`만 소유한다. `_meta/page-type-spec.md`의 legacy enum 절은 historical non-normative이며 현재 checker 입력이 아니다.

## Taxonomy

상세는 `_meta/taxonomy.md`. controlled vocabulary 만 tag 허용. supersede 시 ADR + alias. domain 추가·비활성화는 `_meta/domains.yaml` 변경에서 시작하며, taxonomy 확장이 필요하면 별도 review 로 처리한다.

## Naming

- 파일명: lowercase kebab-case
- 디렉토리: 동일
- 동음이의 시 disambiguation suffix
- 폴더 구조·파일 배치·네이밍 상세는 `.claude/rules/structure-rules.md` 가 소유한다. Claude Code 는 자동 로드하고 다른 도구는 열어서 읽는다. 콘텐츠 생성·수정·이동 시 그 규칙을 따른다

## LLM 호출 규약

- `model_id` 직접 인용 금지 — **LLM 호출 설정·프롬프트(scripts/)** 한정 (ADR-0001). `_meta/llm-config.yaml` profile alias 만 사용
- 페이지 본문(raw·wiki)의 모델명은 검열하지 않음 — `taxonomy.md` 가 모델명을 entity vocab 으로 요구 (ADR-0001, model_id 본문 grep 폐기)
- 자기 추론 어휘 (`I am Claude`, `I am Opus`, ...) 는 **prompt 본문** 에 등장 금지 (페이지 본문 grep 아님)
- runtime canary 가 1일 주기 검증

## Commit 규약

- wiki/ commit author = `swan-bot` (자동 — `git config` + `scripts/commit_wiki.sh`)
- wiki/ commit subject prefix = `[wiki-bot]`
- cs/, development/, coding-test/, lang/, tools/ commit author = 사용자 (`swan`)
- cs/, development/ 커밋 메시지: Conventional Commits 접두(`docs:`, `java:`, `feat(pipeline):`)와 한국어 본문 — git log 의 실제 패턴

## Quality 보장

- 페이지 새로 만들기보다 기존 페이지 갱신 우선
- 인용 누락 페이지 거부
- taxonomy alias는 canonical 대체값을 MEDIUM으로 안내하고, taxonomy 미등재 tag·entity와 잘못된 stable ID는 거부한다. 의미상 paraphrase처럼 자동 판정할 수 없는 변형은 soft-review 대상으로 둔다.
- 표시되지 않은 페이지 간 명제 모순은 거부한다. Claims evidence verdict와 Open Questions로 명시한 contradiction·insufficient 상태는 보존 가능한 review 상태다.
- 모든 op 후 vault 가 이전보다 더 정합된 상태여야 함

## Repository Overview

CS 지식과 프로그래밍 학습 내용을 정리하는 개인 학습 저장소. 모든 문서는 한국어로 작성. 빌드 시스템 없음 — Java 파일은 `javac`/`java`로 개별 컴파일.

## Compiling & Running Java

```bash
cd coding-test/stage1/practice
javac HelloPrint.java
java HelloPrint
```

## 참고

- Karpathy LLM Wiki gist (2026-04-04): 본 패턴의 원형
- Panel-debate A/B/C 결정 (2026-05-20): 본 schema 의 합의 근거
- ~/.claude/panel-debate/20260520-*-llm-wiki-{A,B,C}/ : 세션 로그
