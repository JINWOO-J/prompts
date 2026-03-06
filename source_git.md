아래의 내용들을 추가하고 싶어.
잘 알려진 아래의 github을 clone하고 각각을 분석해서, 우리만의 방식으로 분류하고 저장하자.

> https://github.com/VoltAgent/awesome-claude-code-subagents
> https://github.com/Scoutflo/Scoutflo-SRE-Playbooks
> https://github.com/shawnewallace/prompt-library
> https://github.com/cremich/promptz
> https://github.com/codingthefuturewithai/software-dev-prompt-library


1. 대표적인 GitHub 레포지토리 예시
VoltAgent/awesome-claude-code-subagents: 인프라 전문가들을 위한 가장 구체적인 라이브러리 중 하나입니다. azure-infra-engineer, cloud-architect, incident-responder, kubernetes-specialist, security-engineer, sre-engineer, terraform-engineer 등 역할별로 특화된 프롬프트와 서브에이전트 정의를 포함하고 있습니다.

Scoutflo/Scoutflo-SRE-Playbooks: 414개 이상의 포괄적인 인시던트 대응 플레이북을 포함하고 있습니다. AWS, Kubernetes, Sentry 환경에서의 장애 진단 및 해결을 위한 체계적인 절차를 담고 있으며, AI 에이전트가 해석하여 실행할 수 있는 자연어 지침을 제공합니다.

shawnewallace/prompt-library: Claude Code 및 GitHub Copilot을 위한 개인용 라이브러리로, 'DevOps Infrastructure' 카테고리 내에서 Terraform, CI/CD 파이프라인, 컨테이너 설정용 프롬프트를 시나리오별로 관리합니다.

cremich/promptz: Amazon Q Developer 및 Kiro CLI 환경에서 사용 가능한 라이브러리입니다. 아키텍처 설계, 보안 분석, 코드 리뷰 등 소프트웨어 개발 생명주기(SDLC) 전반의 프롬프트를 관리합니다.

codingthefuturewithai/software-dev-prompt-library: 아키텍처 설계, 인프라 스캐폴딩, 보안 감사 등 공통 엔지니어링 작업을 위한 구조화된 프롬프트 체인을 제공합니다.

2. 프롬프트 라이브러리의 표준 파일 구조 (Prompt-as-Code)
프롬프트는 단순한 텍스트 파일이 아니라, Terraform 모듈이나 Helm 차트처럼 버전 관리가 가능한 자산으로 저장되어야 합니다. 일반적인 레포지토리 구조는 다음과 같습니다.

prompt-library/
├── infrastructure/
│   ├── aws-iam-security.prompt.md    # IAM 정책 감사용
│   ├── k8s-hpa-optimization.md       # 쿠버네티스 자원 최적화용
│   └── terraform-refactor.md         # IaC 코드 개선용
├── incident-response/
│   ├── rca-5whys-template.md         # 근본 원인 분석 템플릿
│   └── log-anomaly-detector.md       # 로그 이상 징후 분석
├── shared/
│   ├── role-definitions.yaml         # 공통 페르소나 정의
│   └── guardrails.md                 # 환각 방지 공통 규칙
└── prompts.meta.yaml                 # 프롬프트 검색을 위한 메타데이터

3. 라이브러리에 저장될 개별 프롬프트의 구성 요소 (템플릿)
재사용 가능한 엔터프라이즈 프롬프트를 만들 때는 다음 5가지 핵심 요소를 포함하여 마크다운(.md) 형식으로 작성하는 것이 권장됩니다.

Role (역할): "당신은 10년 경력의 시니어 SRE입니다."

Task (작업): 수행할 구체적인 목표 (예: "로그에서 5xx 에러 패턴 식별") 

Context (문맥): 분석할 데이터의 위치나 환경 정보 (로그, 메트릭, 설정 파일 등)

Grounding Rule (접지 규칙): "제공된 데이터 내에서만 답변하고, 모르면 '데이터 부족'이라 답할 것" 

Output Format (출력 형식): 기대하는 결과 구조 (예: JSON, 테이블, 4단계 요약 보고서)