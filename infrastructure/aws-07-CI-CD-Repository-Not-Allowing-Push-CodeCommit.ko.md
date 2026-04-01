---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/07-CI-CD/Repository-Not-Allowing-Push-CodeCommit.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- allowing
- ci-cd
- cloudwatch
- codecommit
- iam
- infrastructure
- k8s-service
- performance
- push
- repository
- sts
---

# CodeCommit 저장소 Push 허용 불가

## 의미

CodeCommit 저장소가 Push 작업을 허용하지 않는(접근 거부 오류 또는 CodeCommitPushDenied 알람 트리거) 이유는 IAM 권한이 부족하거나, 저장소 브랜치 보호 규칙이 Push를 차단하거나, 저장소 접근 정책이 작업을 제한하거나, Git 자격 증명이 유효하지 않거나, 저장소 상태가 쓰기를 방해하거나, CodeCommit 저장소 브랜치가 잠겨 있기 때문입니다. CodeCommit Push 작업이 실패하고, 코드 변경을 커밋할 수 없으며, 저장소 접근이 거부됩니다. 이는 소스 제어 및 CI/CD 계층에 영향을 미치며 코드 업데이트를 차단합니다. 일반적으로 권한 문제, 브랜치 보호 문제 또는 자격 증명 실패로 인해 발생합니다. Pull Request 워크플로우와 함께 CodeCommit을 사용하는 경우 브랜치 보호가 다를 수 있으며 애플리케이션에서 Push 실패가 발생할 수 있습니다.

## 영향

CodeCommit Push 작업 실패; 코드 변경 커밋 불가; 저장소 접근 거부; Git Push 오류 발생; 소스 제어 작업 차단; 저장소 쓰기 권한 부족; 개발 워크플로우 중단; 코드 업데이트 Push 불가. CodeCommitPushDenied 알람이 발생할 수 있으며, Pull Request 워크플로우와 함께 CodeCommit을 사용하는 경우 브랜치 보호가 다를 수 있고, 차단된 코드 업데이트로 인해 애플리케이션에서 오류 또는 성능 저하가 발생할 수 있으며, 개발 워크플로우가 완전히 차단될 수 있습니다.

## 플레이북

1. CodeCommit 저장소 `<repository-name>`이 존재하고 리전 `<region>`에서 CodeCommit의 AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`에서 CodeCommit 저장소 `<repository-name>`을 조회하고 저장소 접근 정책, 브랜치 보호 규칙, 저장소 상태를 검사하여 저장소 상태를 확인합니다.
3. Push를 시도하는 IAM 사용자 `<user-name>` 또는 IAM 역할 `<role-name>`을 조회하고 CodeCommit 저장소 작업에 대한 정책 권한을 검사하여 IAM 권한을 확인합니다.
4. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 쿼리하고 저장소 `<repository-name>`과 관련된 CodeCommit API 호출 실패 또는 접근 거부 이벤트를 필터링하여 접근 거부 세부 정보를 포함합니다.
5. 지난 24시간 동안 CodeCommit 저장소 `<repository-name>`의 RepositoryTriggersFailed를 포함한 CloudWatch 메트릭을 조회하여 접근 관련 오류 패턴을 식별하고 오류 메트릭을 분석합니다.
6. 저장소 `<repository-name>`의 CodeCommit 저장소 브랜치를 나열하고 브랜치 보호 규칙 및 Push 권한 설정을 확인하여 브랜치 보호 구성을 확인합니다.
7. CodeCommit 저장소 `<repository-name>` Git 자격 증명 구성을 조회하고 Git 자격 증명이 유효한지 확인하여 자격 증명 만료가 접근에 영향을 미치는지 확인합니다.
8. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 쿼리하고 지난 24시간 이내 저장소 `<repository-name>`과 관련된 CodeCommit 저장소 접근 정책 또는 브랜치 보호 수정 이벤트를 필터링하여 구성 변경을 확인합니다.
9. API 호출 오류를 포함한 CodeCommit의 CloudWatch 메트릭을 조회하고 CodeCommit 서비스 상태를 확인하여 서비스 문제가 Push 작업에 영향을 미치는지 확인합니다.

## 진단

1. CloudTrail 이벤트가 포함된 CloudWatch Logs(플레이북 4단계)를 분석하여 특정 Push 실패 오류 메시지를 식별합니다. 오류가 "AccessDenied" 또는 "GitPush failed"를 나타내면 즉시 IAM 권한 확인으로 진행합니다. 오류가 "Branch is locked" 또는 "Protected branch"를 나타내면 브랜치 보호 규칙이 Push를 차단하고 있습니다.

2. 접근 거부 오류의 경우, Push를 시도하는 사용자 또는 역할에 대한 IAM 권한(플레이북 3단계)을 확인합니다. IAM 엔티티에 저장소에 대한 codecommit:GitPush 권한이 있어야 합니다. 권한이 최근 수정된 경우 해당 변경이 원인일 가능성이 높습니다.

3. 브랜치 보호 규칙(플레이북 6단계)을 검토하여 대상 브랜치에 직접 Push를 차단하는 보호 규칙이 있는지 확인합니다. 브랜치 보호가 Pull Request를 요구하거나 특정 사용자에게 Push 접근을 제한하면 직접 Push가 거부됩니다.

4. 저장소 접근 정책(플레이북 2단계)을 확인하여 저장소 정책이 Push 작업을 제한하지 않는지 확인합니다. 저장소 수준 정책이 특정 IAM 엔티티에 대한 Push 접근을 거부하면 Push가 실패합니다.

5. Git 자격 증명 구성(플레이북 7단계)을 확인하여 자격 증명이 유효하고 만료되지 않았는지 확인합니다. HTTPS Git 자격 증명을 사용하는 경우 토큰에 만료 날짜가 있을 수 있습니다. SSH 키를 사용하는 경우 키가 IAM에 올바르게 구성되었는지 확인합니다.

6. CloudTrail 이벤트(플레이북 8단계)를 Push 실패 타임스탬프와 5분 이내로 상관시켜 IAM 정책, 브랜치 보호 또는 저장소 접근 정책 수정을 식별합니다. 권한 변경이 Push가 실패하기 시작한 시점과 일치하면 해당 변경이 원인일 가능성이 높습니다.

7. 1시간 이내에 다른 브랜치 간의 Push 실패 패턴을 비교합니다. 실패가 브랜치별인 경우 해당 브랜치의 브랜치 보호 규칙이 원인일 가능성이 높습니다. 실패가 저장소의 모든 브랜치에 영향을 미치면 IAM 권한 또는 저장소 전체 접근 정책이 문제입니다.

8. CodeCommit의 CloudWatch 메트릭(플레이북 5단계 및 9단계)을 검토하여 저장소에 영향을 미치는 더 넓은 서비스 문제가 있는지 확인합니다. 메트릭이 높은 오류율을 표시하면 CodeCommit 서비스 문제가 있을 수 있습니다.

9. 지난 24시간 동안의 Push 실패 빈도를 분석합니다. 실패가 지속적이면 권한 또는 브랜치 보호가 원인일 가능성이 높습니다. 실패가 간헐적이면 자격 증명 또는 서비스 가용성이 원인일 수 있습니다.

지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우: 시간 범위를 7일로 확장하고, Git 자격 증명 만료 및 저장소 트리거 구성을 포함한 대체 증거 소스를 검토하고, IAM 권한 드리프트 또는 브랜치 보호 규칙 업데이트와 같은 점진적 문제를 확인하고, Git 자격 증명 서비스 가용성 또는 저장소 서비스 상태와 같은 외부 의존성을 확인하고, Push 실패의 과거 패턴을 검사하고, CodeCommit 저장소 브랜치 잠금 상태를 확인하고, CodeCommit Git 자격 증명 서비스 토큰 만료를 확인합니다.
