# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

@AGENTS.md

위 가져오기로 `AGENTS.md`(LLM Wiki Operating Schema)를 두 런타임이 같은 본문으로 읽는다(글로벌 §규칙 계층 ③ — 규칙 본문은 한 곳). 아래는 이 파일만의 항목이다.

## Repository Overview

CS 지식과 프로그래밍 학습 내용을 정리하는 개인 학습 저장소. 모든 문서는 한국어로 작성. 빌드 시스템 없음 — Java 파일은 `javac`/`java`로 개별 컴파일.

## Rules

프로젝트 구조, 폴더 배치, 네이밍 컨벤션 규칙은 `.claude/rules/structure-rules.md`에 정의되어 있다.
콘텐츠 생성, 수정, 이동 시 반드시 해당 문서의 규칙을 따른다.

## Compiling & Running Java

```bash
cd coding-test/stage1/practice
javac HelloPrint.java
java HelloPrint
```

## Conventions

- **Language**: All documentation is written in Korean
- **Commit messages**: Korean descriptions with category prefix (e.g., `docs:`, `java:`)
- Existing `CLAUDE.md` files inside subdirectories are auto-generated claude-mem context files, not project guidance
