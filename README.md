# 인프라/보안 운영 프롬프트 라이브러리

> **목적**: 인프라/보안 운영팀의 RCA(근본 원인 분석), 장애 대응, 트러블슈팅을 AI 에이전트로 자동화하기 위한 프롬프트 모음  
> **관리 원칙**: PromptOps — 프롬프트를 코드처럼 Git으로 버전 관리  
> **전체 인덱스**: [prompts.meta.yaml](./prompts.meta.yaml) — 431개 프롬프트 자동 색인

---

## 📁 디렉토리 구조

```
prompts/
├── README.md              # 이 파일
├── CONTRIBUTING.md        # 기여 가이드
├── prompts.meta.yaml      # 전체 인덱스 (자동 생성)
├── scripts/
│   └── rebuild-index.py   # 인덱스 재생성 스크립트
│
├── rca/                   # 🔬 근본 원인 분석 방법론 (6개 — 자체 제작)
├── incident-response/     # 🚨 인시던트 대응 에이전트 + AWS 장애 플레이북 (73개)
├── application/           # 🐛 앱 레이어 에러 추적 / Sentry 플레이북 (25개)
├── infrastructure/        # 🏗️ K8s + CI/CD + 인프라 트러블슈팅 (264개)
├── security/              # 🔐 보안 침해 / IAM / WAF / RBAC (29개)
├── data-ai/               # 📊 Data Engineering / MLOps / DB 최적화 (12개)
├── shared/                # 🔧 공통 페르소나 / 가드레일 / 범용 에이전트 (21개)
└── techniques/            # 📚 프롬프트 기법 참고 문서 (1개)
```

---

## 🚦 상황별 선택 가이드

### 📌 RCA (근본 원인 분석) — `rca/`

```
장애 발생
    │
    ├─ 보안 침해 의심?                   → rca/05_security_rca.md
    ├─ 원인 후보 3개+, 복잡한 장애?      → rca/04_advanced_tot.md
    ├─ 멀티 서비스, 로그 소스 다양?      → rca/03_timeline_chain.md
    ├─ 원인 불명확, 데이터 부족?         → rca/02_hypothesis_stepback.md
    └─ 단일 서비스, 명확한 장애?         → rca/01_basic_rca.md

모든 경우 → 최종 보고서는 rca/06_quality_review.md 로 검증
```

| 파일 | 기법 | 난이도 | 상황 |
|------|------|--------|------|
| [01_basic_rca.md](./rca/01_basic_rca.md) | 5-Whys + CoT | 🟢 기본 | 단일 서비스, 선형 인과 관계 |
| [02_hypothesis_stepback.md](./rca/02_hypothesis_stepback.md) | Step-back + 가설 검증 | 🟡 중급 | 원인 불명확 |
| [03_timeline_chain.md](./rca/03_timeline_chain.md) | 프롬프트 체이닝 4단계 | 🟡 중급 | 멀티 시스템, 복잡한 타임라인 |
| [04_advanced_tot.md](./rca/04_advanced_tot.md) | Tree-of-Thoughts | 🔴 고급 | 복수 원인 가설, 위험도 비교 |
| [05_security_rca.md](./rca/05_security_rca.md) | Diamond Model + ATT&CK | 🔴 고급 | 보안 침해, APT, 이상 행위 |
| [06_quality_review.md](./rca/06_quality_review.md) | CoVe + Self-Refinement | ⬜ 공통 | 모든 RCA 보고서 최종 검토 |

---

### 🚨 인시던트 대응 (`incident-response/`) — 73개

AWS 장애 + 인시던트 대응 에이전트. 파일명 패턴으로 빠르게 찾기:

| 파일명 패턴 | 내용 |
|------------|------|
| `agent-incident-responder.md` | 인시던트 초기 평가, 심각도 분류 (커스텀) |
| `agent-sre-engineer.md` | SLO/에러버짓 분석, Blameless 포스트모텀 (커스텀) |
| `agent-devops-incident-responder.md` | DevOps MTTR 개선, 런북 자동화 |
| `aws-01-Compute-*.md` | EC2, Lambda, ECS, EKS, Auto Scaling 장애 (27개) |
| `aws-02-Database-*.md` | RDS, DynamoDB 장애 (8개) |
| `aws-03-Storage-*.md` | S3 장애 (7개) |
| `aws-04-Networking-*.md` | ALB/ELB, Route53, API GW, VPN (17개) |
| `aws-06-Monitoring-*.md` | CloudWatch, CloudTrail, X-Ray (8개) |

---

### 🐛 앱 레이어 에러 (`application/`) — 25개

Sentry 기반 에러 타입별 플레이북:

| 패턴 | 대상 |
|------|------|
| `sentry-ConnectionError-*` | DB/Redis 연결 실패 |
| `sentry-ConsumerError-*` | Kafka Consumer 오류 |
| `sentry-TimeoutError-*` | API/DB/Redis 타임아웃 |
| `sentry-ProgrammingError-*` | DB 쿼리 오류 (컬럼 없음, 제약 위반 등) |
| `sentry-*Exception*` | 미처리 예외 |

---

### 🏗️ 인프라 트러블슈팅 (`infrastructure/`) — 264개

| 패턴 | 내용 |
|------|------|
| `agent-kubernetes.md` | K8s 트러블슈팅 에이전트 (커스텀) |
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
| `aws-07-CI-CD-*.md` | CodePipeline, CloudFormation (9개) |
| `claude-code-commands-*.md` | IaC 리뷰, 파이프라인 스캐폴딩 (shawnewallace) |
| `github-copilot-instructions-*.md` | Terraform/CI-CD/Security 코딩 가이드 |
| `microservices-architect.md` | 마이크로서비스 아키텍처 설계 에이전트 |
| `k8s-13-Proactive-Capacity-Performance-*.md` | 용량/성능 사전 예방 체크 (7개) |
| `k8s-13-Proactive-Security-Compliance-*.md` | 보안/컴플라이언스 사전 점검 (10개) |
| `k8s-13-Proactive-Backup-DR-*.md` | 백업/재해복구 사전 검증 (7개) |
| `k8s-13-Proactive-Cost-Optimization-*.md` | 비용 최적화 사전 분석 (8개) |
| `k8s-13-Proactive-Observability-*.md` | 관측성 커버리지 점검 (7개) |
| `k8s-13-Proactive-Data-Integrity-*.md` | 데이터 무결성 사전 검증 (5개) |
| `k8s-13-Proactive-Operational-Readiness-*.md` | 운영 준비도 사전 점검 (12개) |

---

### 🔐 보안 (`security/`) — 29개

| 패턴 | 내용 |
|------|------|
| `agent-security-engineer.md` | 보안 이상행위 분석, MITRE ATT&CK (커스텀) |
| `agent-penetration-tester.md` | 침투 테스트 에이전트 |
| `agent-compliance-auditor.md` | SOC2/GDPR 감사 |
| `aws-05-Security-*.md` | IAM, WAF, GuardDuty, KMS, Shield (16개) |
| `k8s-07-RBAC-*.md` | K8s RBAC/권한 오류 (6개) |

---

### 📊 Data/AI (`data-ai/`) — 12개

MLOps, 데이터 엔지니어링, DB 최적화 에이전트.

---

### 🔧 공통 (`shared/`) — 21개

| 파일 | 설명 |
|------|------|
| `role-definitions.md` | SRE/SIRT/DevOps/K8s 페르소나 정의 |
| `guardrails.md` | 환각 방지, 보안 격리, HITL 규칙 |
| `architect.agent.md` | 아키텍처 계획 에이전트 |
| `plan.agent.md` | 작업 계획 에이전트 |
| `error-coordinator.md` | 에러 조정 에이전트 |
| `it-ops-orchestrator.md` | IT 운영 오케스트레이터 |
| `multi-agent-coordinator.md` | 멀티 에이전트 조정자 |
| `task-distributor.md` | 작업 분배 에이전트 |
| `workflow-orchestrator.md` | 워크플로우 오케스트레이터 |

---

## 🗺️ 통합 대응 플로우

```
장애/알림 수신
    │
    ├─ 1. 심각도 평가
    │       └─ incident-response/agent-incident-responder.md
    │
    ├─ 2. 영역별 트리아지
    │       ├─ AWS 서비스 장애  → incident-response/aws-{서비스}-*.md
    │       ├─ K8s 장애         → infrastructure/k8s-{섹션}-*.md
    │       ├─ 앱 에러 (Sentry) → application/sentry-*.md
    │       └─ 보안 위협        → security/agent-security-engineer.md
    │
    ├─ 3. RCA 수행
    │       └─ rca/01~05.md (상황별 선택)
    │
    └─ 4. 보고서 검증
            └─ rca/06_quality_review.md
```

---

## ⚡ 빠른 시작

```bash
# 프롬프트 검색 (태그/파일명)
grep -r "crashloop" prompts/ --include="*.md" -l

# 전체 인덱스 재생성
python3 scripts/rebuild-index.py

# 카테고리별 파일 수 확인
for d in rca incident-response application infrastructure security data-ai shared; do
  echo "$d: $(ls $d/*.md | wc -l)개"
done
```

---

## 📚 참고 문서

- [RCA 기법 선택 가이드](./techniques/rca_techniques.md)
- [기법 조사 원본](./found.md)
- [기여 가이드](./CONTRIBUTING.md)
- [소스 레포 목록](./source_git.md)
