# Taxonomy — Controlled Vocabulary

본 문서는 tag 와 entity·concept 명칭의 controlled vocabulary 를 정의한다. wiki/ 페이지의 모든 tag·entity 명칭은 본 목록에서만 선택.

## 갱신 워크플로우 (Panel B B7)

| 변경 | 절차 |
|---|---|
| 신규 vocab 추가 | PR 1개 — taxonomy.md 수정 + 사람 review |
| vocab supersede (예: foundation → frontier) | ADR + taxonomy.md canonical 항목의 `(alias: ...)` 갱신. page frontmatter `tags:`는 canonical만 저장하고 자동 일괄 치환하지 않는다 |
| vocab 삭제 | ADR + 1주 deprecation window + alias redirect |

## Tag 목록 — LLM/AI 도메인

### 아키텍처 (architecture)

- `transformer`
- `attention` (alias: `self-attention`)
- `mixture-of-experts` (alias: `moe`)
- `sparse-models`
- `dense-models`
- `state-space-models` (alias: `ssm`, `mamba`)
- `diffusion-models`
- `autoregressive`
- `encoder-decoder`
- `decoder-only`

### 훈련 (training)

- `pretraining`
- `post-training`
- `instruction-tuning` (alias: `sft`, `supervised-fine-tuning`)
- `rlhf`
- `dpo`
- `rlaif`
- `lora`
- `qlora`
- `continual-learning`
- `curriculum-learning`

### 추론 (inference)

- `speculative-decoding`
- `kv-cache`
- `quantization`
- `pruning`
- `distillation`

### Scaling

- `scaling-laws`
- `chinchilla-scaling`
- `emergent-abilities`
- `compute-optimal`

### Evaluation

- `benchmark`
- `mmlu`
- `humaneval`
- `mt-bench`
- `lm-eval-harness`
- `holistic-evaluation` (alias: `helm`)

### Safety / Alignment

- `alignment`
- `constitutional-ai` (alias: `cai`)
- `red-teaming`
- `jailbreak`
- `prompt-injection`
- `hallucination`
- `refusal`

### Infrastructure

- `vllm`
- `sglang`
- `tgi` (alias: `text-generation-inference`)
- `tensorrt-llm`
- `ollama`
- `transformers-library`

### Agents

- `agent`
- `tool-use`
- `function-calling`
- `mcp` (alias: `model-context-protocol`)
- `react-pattern`
- `chain-of-thought` (alias: `cot`)

### Concepts (general)

- `in-context-learning` (alias: `icl`)
- `few-shot`
- `zero-shot`
- `prompt-engineering`

## Tag 목록 — Information Security 및 기존 workspace

아래는 현재 `wiki/` frontmatter에서 실제 사용 중인 canonical tag다. 새 tag는 이 목록에 먼저 등록하고 사람 review를 거친다.

- `answer-template`
- `architecture`
- `certification`
- `cleanup`
- `data-classification`
- `documentation-architecture`
- `draft`
- `endpoint-security`
- `exam-analysis`
- `exam-criteria`
- `exam-pattern`
- `exam-reconstruction`
- `exam-references`
- `exam-strategy`
- `expected-observations`
- `frequency`
- `hands-on`
- `hands-on-lab`
- `high-availability`
- `identity-and-access-management` (alias: `iam`)
- `identity-provider` (alias: `idp`)
- `ids`
- `information-security`
- `integrated-study`
- `isms-p`
- `isolation`
- `lab`
- `lab-safety`
- `labs`
- `law`
- `linux-hardening`
- `log-triage`
- `mapping`
- `migration-plan`
- `multi-factor-authentication` (alias: `mfa`)
- `network-protocol`
- `network-security`
- `pattern`
- `pdf-source`
- `predicted-questions`
- `prediction`
- `privacy-law`
- `prompt-completeness`
- `questions`
- `recurrence`
- `references`
- `risk`
- `roadmap`
- `scaffold`
- `service-config`
- `session-management`
- `session-pattern`
- `significance`
- `single-sign-on` (alias: `sso`)
- `source-index`
- `study`
- `study-cheatsheet`
- `study-guide`
- `study-note`
- `study-roadmap`
- `study-strategy`
- `todo`
- `udemy`
- `verification`
- `web-vulnerability`

## Entity 목록 (LLM/AI 영역)

(초기 시드 — 최소 핵심. 신규 entity 추가 PR 로 확장)

### Organizations

- `openai`
- `anthropic`
- `google-deepmind` (alias: `deepmind`, `google-ai`)
- `meta-ai` (alias: `fair`)
- `mistral-ai`
- `cohere`
- `hugging-face`
- `vercel`

### Models (frontier — 2026-05 기준)

- `gpt-5` (alias: `gpt-5.1`, `gpt-5.2`, `gpt-5.5`)
- `claude-opus-4-7`
- `claude-sonnet-4-6`
- `claude-haiku-4-5`
- `gemini-2`
- `llama-4`
- `mixtral-8x7b`
- `mixtral-8x22b`
- `qwen-2-5` (alias: `qwen-2.5`, `qwen-2.0`)

### Foundational papers (evergreen)

- `attention-is-all-you-need` (Vaswani et al. 2017)
- `bert` (Devlin et al. 2018)
- `gpt-2` (Radford et al. 2019)
- `gpt-3` (Brown et al. 2020)
- `chinchilla` (Hoffmann et al. 2022)
- `instructgpt` (Ouyang et al. 2022)
- `lora-paper` (Hu et al. 2021)

## Tag 목록 — 암호·키 관리 주제

암호·키 관리 주제의 canonical tag다. `load_taxonomy` 는 모든 `## Tag 목록` 구역을 하나의 집합으로 합쳐 읽으므로 구역은 검증 제약이 아니라 사람이 찾기 위한 구분이다. 따라서 이 태그도 domain 과 무관하게 어느 페이지에서나 쓸 수 있다. 신규 tag 는 이 목록에 먼저 등록하고 사람 review 를 거친다.

- `key-management`
- `post-quantum-cryptography` (alias: `pqc`)

## CS 도메인 별 vocabulary (보안 / 암호 / 네트워크 등)

`wiki/domains/information-security/`의 현재 사용 tag는 위 Information Security 및 기존 workspace 목록에 등록했다. cryptography와 network 도메인은 실제 wiki 합성 tag가 생길 때 별도 canonical section을 추가한다.

## Alias 메커니즘

alias 는 같은 개념의 다른 표기를 동일 entity 로 redirect. taxonomy.md canonical, frontmatter `tags:` 는 canonical 만 사용.

예: canonical 작성값은 `tags: [attention]`이다. `tags: [self-attention]`은 저장 목표가 아니지만 checker는 자동 치환하지 않고 MEDIUM 대체 안내를 반환한다.

LLM 이 alias 어휘를 사용하면 canonical checker가 canonical 대체값을 MEDIUM으로 안내한다. 자동 치환은 수행하지 않는다.

## 검증

`scripts/knowledge/check.py`의 `VR-KP-023`이 wiki content page의 `tags`와 entity 경로형 wikilink를 전수 검사한다. canonical tag는 통과하고, alias tag는 canonical 대체값을 MEDIUM으로 안내하며, taxonomy 미등재 tag는 HIGH로 실패한다. entity는 wikilink target 경로가 `.../entities/<slug>`인 경우와 `entities/<slug>.md`의 `<slug>`를 검사하며, canonical이면 통과, alias면 MEDIUM, 미등록이면 HIGH다. 일반 wikilink와 concept 링크는 entity 검사 대상이 아니다. `scripts/knowledge/schema.py`의 taxonomy loader는 canonical 중복·alias 중복·canonical/alias 충돌을 거부한다.

## 참고

- 결정 출처: panel-debate B B7 (vocabulary 갱신 워크플로우)
- 초기 시드는 2026-05-20 기준. dogfood 후 확장.
