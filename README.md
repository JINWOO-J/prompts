# 인프라/보안 운영 프롬프트 라이브러리

> SRE, DevOps, 보안 운영팀을 위한 AI 프롬프트 모음.
> RCA(근본 원인 분석), 장애 대응, 트러블슈팅을 AI 에이전트로 자동화한다.

- 관리 원칙: PromptOps -- 프롬프트를 코드처럼 Git으로 버전 관리
- 전체 인덱스: [prompts.meta.yaml](./prompts.meta.yaml) -- 461개 프롬프트 자동 색인

---

## 디렉토리 구조

```
├── rca/                   # 근본 원인 분석 방법론 (6개)
├── incident-response/     # 인시던트 대응 + AWS 장애 플레이북 (73개)
├── application/           # 앱 레이어 에러 추적 / Sentry 플레이북 (25개)
├── infrastructure/        # K8s + CI/CD + 인프라 트러블슈팅 (264개)
├── security/              # 보안 침해 / IAM / WAF / RBAC (29개)
├── data-ai/               # Data Engineering / MLOps / DB 최적화 (12개)
├── shared/                # 공통 페르소나 / 가드레일 / 범용 에이전트 (21개)
├── techniques/            # 프롬프트 기법 참고 문서 (31개)
├── scripts/               # CLI, MCP 서버, 인덱스 도구
├── web/                   # 웹 뷰어 (SPA)
└── prompts.meta.yaml      # 전체 인덱스 (자동 생성)
```

---

## 빠른 시작

### 의존성

- Python 3.10+
- PyYAML (`pip install pyyaml`)
- (선택) fzf -- 인터랙티브 선택용

### CLI 도구

```bash
# 키워드 검색
python3 scripts/prompt-cli.py search crashloop

# 카테고리별 목록
python3 scripts/prompt-cli.py list --cat infrastructure

# 프롬프트 본문 출력
python3 scripts/prompt-cli.py get rca-01_basic_rca

# 클립보드에 복사
python3 scripts/prompt-cli.py copy rca-01_basic_rca

# fzf 인터랙티브 선택 → 복사
python3 scripts/prompt-cli.py fzf

# 프롬프트 + 로그 컨텍스트 결합
kubectl logs pod/my-app | python3 scripts/prompt-cli.py pipe rca-01_basic_rca

# 여러 프롬프트 결합
python3 scripts/prompt-cli.py compose rca-01_basic_rca shared-guardrails --copy

# 라이브러리 통계
python3 scripts/prompt-cli.py stats
```

### MCP 서버 (AI 에이전트 연동)

프롬프트를 AI 에이전트에서 직접 검색/조회할 수 있는 MCP 서버를 제공한다.

제공 도구:
- `search_prompts` -- 키워드/카테고리로 프롬프트 검색
- `get_prompt` -- 프롬프트 본문 조회

Kiro 설정 (`.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "prompt-library": {
      "command": "python3",
      "args": ["scripts/prompt-mcp-server.py"],
      "autoApprove": ["search_prompts", "get_prompt"]
    }
  }
}
```

### 웹 뷰어

`web/` 폴더의 SPA를 로컬에서 열어 프롬프트를 브라우징할 수 있다.

```bash
# 웹 데이터 생성 후 브라우저에서 열기
python3 scripts/rebuild-index.py
open web/index.html
```

기능: 카테고리/태그 필터, 키워드 검색 (Cmd+K), 마크다운 렌더링, 코드 블록 복사

---

## 카테고리 상세

### RCA (근본 원인 분석) -- `rca/`

```
장애 발생
    |
    +-- 보안 침해 의심?                  -> rca/05_security_rca.md
    +-- 원인 후보 3개+, 복잡한 장애?     -> rca/04_advanced_tot.md
    +-- 멀티 서비스, 로그 소스 다양?     -> rca/03_timeline_chain.md
    +-- 원인 불명확, 데이터 부족?        -> rca/02_hypothesis_stepback.md
    +-- 단일 서비스, 명확한 장애?        -> rca/01_basic_rca.md

모든 경우 -> 최종 보고서는 rca/06_quality_review.md 로 검증
```

| 파일 | 기법 | 난이도 | 상황 |
|------|------|--------|------|
| [01_basic_rca.md](./rca/01_basic_rca.md) | 5-Whys + CoT | 기본 | 단일 서비스, 선형 인과 관계 |
| [02_hypothesis_stepback.md](./rca/02_hypothesis_stepback.md) | Step-back + 가설 검증 | 중급 | 원인 불명확 |
| [03_timeline_chain.md](./rca/03_timeline_chain.md) | 프롬프트 체이닝 4단계 | 중급 | 멀티 시스템, 복잡한 타임라인 |
| [04_advanced_tot.md](./rca/04_advanced_tot.md) | Tree-of-Thoughts | 고급 | 복수 원인 가설, 위험도 비교 |
| [05_security_rca.md](./rca/05_security_rca.md) | Diamond Model + ATT&CK | 고급 | 보안 침해, APT, 이상 행위 |
| [06_quality_review.md](./rca/06_quality_review.md) | CoVe + Self-Refinement | 공통 | 모든 RCA 보고서 최종 검토 |


### 인시던트 대응 -- `incident-response/` (73개)

AWS 장애 플레이북 + 인시던트 대응 에이전트.

| 파일명 패턴 | 내용 |
|------------|------|
| `agent-incident-responder.md` | 인시던트 초기 평가, 심각도 분류 |
| `agent-sre-engineer.md` | SLO/에러버짓 분석, Blameless 포스트모텀 |
| `agent-devops-incident-responder.md` | DevOps MTTR 개선, 런북 자동화 |
| `aws-01-Compute-*.md` | EC2, Lambda, ECS, EKS, Auto Scaling (27개) |
| `aws-02-Database-*.md` | RDS, DynamoDB (8개) |
| `aws-03-Storage-*.md` | S3 (7개) |
| `aws-04-Networking-*.md` | ALB/ELB, Route53, API GW, VPN (17개) |
| `aws-06-Monitoring-*.md` | CloudWatch, CloudTrail, X-Ray (8개) |

### 앱 레이어 에러 -- `application/` (25개)

Sentry 기반 에러 타입별 플레이북.

| 패턴 | 대상 |
|------|------|
| `sentry-ConnectionError-*` | DB/Redis 연결 실패 |
| `sentry-ConsumerError-*` | Kafka Consumer 오류 |
| `sentry-TimeoutError-*` | API/DB/Redis 타임아웃 |
| `sentry-ProgrammingError-*` | DB 쿼리 오류 (컬럼 없음, 제약 위반 등) |
| `sentry-*Exception*` | 미처리 예외 |

### 인프라 트러블슈팅 -- `infrastructure/` (264개)

| 패턴 | 내용 |
|------|------|
| `agent-kubernetes.md` | K8s 트러블슈팅 에이전트 |
| `agent-docker-expert.md` | 컨테이너 빌드/런타임 |
| `agent-terraform-engineer.md` | IaC 관리 |
| `agent-deployment-engineer.md` | CI/CD 배포 |
| `k8s-01-Control-Plane-*.md` | Control Plane 장애 (24개) |
| `k8s-02-Nodes-*.md` | Node 장애 (24개) |
| `k8s-03-Pods-*.md` | Pod 장애 (41개) |
| `k8s-04-Workloads-*.md` | Deployment, DaemonSet, Job, HPA (25개) |
| `k8s-05-Networking-*.md` | Ingress, DNS, Service 장애 (24개) |
| `k8s-06-Storage-*.md` | PVC, 볼륨 마운트 |
| `k8s-08-Configuration-*.md` | ConfigMap, Secret |
| `k8s-09-Resource-Management-*.md` | CPU/Memory Overcommit |
| `k8s-13-Proactive-*.md` | 사전 예방 점검 (용량, 보안, 백업, 비용, 관측성, 데이터 무결성, 운영 준비도) |
| `aws-07-CI-CD-*.md` | CodePipeline, CloudFormation (9개) |

### 보안 -- `security/` (29개)

| 패턴 | 내용 |
|------|------|
| `agent-security-engineer.md` | 보안 이상행위 분석, MITRE ATT&CK |
| `agent-penetration-tester.md` | 침투 테스트 에이전트 |
| `agent-compliance-auditor.md` | SOC2/GDPR 감사 |
| `aws-05-Security-*.md` | IAM, WAF, GuardDuty, KMS, Shield (16개) |
| `k8s-07-RBAC-*.md` | K8s RBAC/권한 오류 (6개) |

### Data/AI -- `data-ai/` (12개)

MLOps, 데이터 엔지니어링, DB 최적화 에이전트.

### 공통 -- `shared/` (21개)

| 파일 | 설명 |
|------|------|
| `role-definitions.md` | SRE/SIRT/DevOps/K8s 페르소나 정의 |
| `guardrails.md` | 환각 방지, 보안 격리, HITL 규칙 |
| `error-coordinator.md` | 에러 조정 에이전트 |
| `it-ops-orchestrator.md` | IT 운영 오케스트레이터 |
| `multi-agent-coordinator.md` | 멀티 에이전트 조정자 |
| `architect.agent.md` | 아키텍처 계획 에이전트 |
| `plan.agent.md` | 작업 계획 에이전트 |

### 프롬프트 기법 -- `techniques/` (31개)

Chain-of-Thought, Tree-of-Thoughts, Self-Refinement, Few-shot, MECE, OODA Loop 등 30개 프롬프트 기법 참고 문서 + RCA 기법 선택 가이드.

---

## 통합 대응 플로우

```
장애/알림 수신
    |
    +-- 1. 심각도 평가
    |       +-- incident-response/agent-incident-responder.md
    |
    +-- 2. 영역별 트리아지
    |       +-- AWS 서비스 장애  -> incident-response/aws-{서비스}-*.md
    |       +-- K8s 장애         -> infrastructure/k8s-{섹션}-*.md
    |       +-- 앱 에러 (Sentry) -> application/sentry-*.md
    |       +-- 보안 위협        -> security/agent-security-engineer.md
    |
    +-- 3. RCA 수행
    |       +-- rca/01~05.md (상황별 선택)
    |
    +-- 4. 보고서 검증
            +-- rca/06_quality_review.md
```

---

## 도구 목록

| 스크립트 | 설명 |
|----------|------|
| `scripts/prompt-cli.py` | CLI (search, list, get, copy, fzf, pipe, compose, stats) |
| `scripts/prompt-mcp-server.py` | MCP 서버 (search_prompts, get_prompt) |
| `scripts/rebuild-index.py` | prompts.meta.yaml 인덱스 재생성 |
| `scripts/validate-index.py` | 인덱스 무결성 검증 |
| `scripts/gen_techniques_v2.py` | 프롬프트 기법 문서 생성기 (30개) |

---

## 인덱스 관리

```bash
# 인덱스 재생성 (프롬프트 추가/삭제 후)
python3 scripts/rebuild-index.py

# 인덱스 검증 (파일 누락, 메타데이터 오류 확인)
python3 scripts/validate-index.py
```
