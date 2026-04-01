---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/07-CI-CD/Stack-Failing-to-Create-CloudFormation.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- ci-cd
- cloudformation
- cloudwatch
- create
- failing
- iam
- infrastructure
- k8s-deployment
- k8s-service
- performance
- stack
- sts
---

# CloudFormation 스택 생성 실패

## 의미

CloudFormation 스택이 생성에 실패(스택 생성 실패 또는 CloudFormationStackCreationFailed 알람 트리거)하는 이유는 템플릿 구문 오류가 존재하거나, IAM 역할 권한이 부족하거나, 리소스 제한이 초과되었거나, 리소스 의존성을 해결할 수 없거나, 스택 생성 중 템플릿 검증이 실패하거나, CloudFormation 서비스 할당량에 도달했기 때문입니다. CloudFormation 스택을 생성할 수 없고, 인프라 배포가 실패하며, 스택 생성이 차단됩니다. 이는 Infrastructure as Code 계층에 영향을 미치며 배포를 차단합니다. 일반적으로 템플릿 오류, 권한 문제 또는 리소스 제약으로 인해 발생합니다. 중첩 스택 또는 스택 세트와 함께 CloudFormation을 사용하는 경우 구성이 다를 수 있으며 애플리케이션에서 배포 실패가 발생할 수 있습니다.

## 영향

CloudFormation 스택 생성 불가; 인프라 배포 실패; 스택 생성 차단; 템플릿 검증 오류 발생; 리소스 프로비저닝 실패; 인프라 자동화 중단; 스택 롤백 발생; 배포 프로세스 완료 불가. CloudFormationStackCreationFailed 알람이 발생할 수 있으며, 중첩 스택 또는 스택 세트와 함께 CloudFormation을 사용하는 경우 구성이 다를 수 있고, 실패한 인프라 배포로 인해 애플리케이션에서 오류 또는 성능 저하가 발생할 수 있으며, 인프라가 배포되지 않은 상태로 남을 수 있습니다.

## 플레이북

1. CloudFormation 스택 `<stack-name>`이 존재하고 리전 `<region>`에서 CloudFormation의 AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`에서 CloudFormation 스택 `<stack-name>`을 조회하고 스택 상태, 스택 이벤트, 실패 이유를 검사하여 실패 세부 정보를 분석합니다.
3. CloudFormation 이벤트가 포함된 CloudWatch Logs 로그 그룹을 쿼리하고 스택 `<stack-name>`과 관련된 스택 생성 실패 이벤트, 검증 오류 또는 리소스 생성 오류를 필터링하여 오류 메시지를 포함합니다.
4. 스택 `<stack-name>`의 CloudFormation 스택 이벤트를 조회하고 리소스 생성 실패, 의존성 해결 오류 또는 검증 오류를 확인하여 이벤트 연대기를 분석합니다.
5. CloudFormation 스택 `<stack-name>`에서 사용하는 IAM 역할 `<role-name>`을 조회하고 리소스 생성 작업에 대한 정책 권한을 검사하여 IAM 권한을 확인합니다.
6. 스택 `<stack-name>`의 CloudFormation 스택 리소스를 조회하고 리소스 생성 상태 및 실패 이유를 확인하여 어떤 리소스가 실패했는지 확인합니다.
7. CloudFormation 스택 `<stack-name>` 템플릿을 조회하고 템플릿 구문을 확인하여 템플릿 검증 오류를 확인합니다.
8. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 쿼리하고 지난 24시간 이내 스택 `<stack-name>`과 관련된 CloudFormation 스택 템플릿 또는 파라미터 수정 이벤트를 필터링하여 템플릿 변경을 확인합니다.
9. 지난 24시간 동안 StackCreationFailures를 포함한 CloudFormation의 CloudWatch 메트릭을 조회하여 스택 생성 실패 패턴을 식별합니다.

## 진단

1. CloudFormation 스택 이벤트(플레이북 2단계 및 4단계)를 분석하여 어떤 리소스가 먼저 실패했는지와 정확한 실패 이유를 식별합니다. 첫 번째 리소스 실패 타임스탬프와 오류 메시지가 근본 원인을 수립합니다.

2. 스택 이벤트가 "Resource handler returned message" 오류와 함께 CREATE_FAILED를 표시하면 특정 리소스(플레이북 6단계)를 검사합니다. 리소스 수준 실패는 유효하지 않은 리소스 속성 또는 서비스별 제약을 나타냅니다.

3. 템플릿 검사(플레이북 7단계) 또는 CloudFormation 이벤트(플레이북 3단계)가 검증 오류를 표시하면 템플릿 구문 문제가 리소스 프로비저닝 시작 전에 스택 생성을 방해하고 있습니다.

4. IAM 역할 권한(플레이북 5단계)이 실패 타임스탬프 전후로 수정된 경우(플레이북 8단계의 CloudTrail 확인) 특정 리소스 유형 생성에 대한 누락된 권한이 원인입니다.

5. 스택 이벤트가 의존성 해결 실패를 표시하면 템플릿의 리소스 의존성 체인을 검사합니다. 순환 의존성 또는 누락된 DependsOn 선언이 순서 실패를 유발합니다.

6. CloudFormation 메트릭(플레이북 9단계) 또는 스택 이벤트가 리소스 제한 오류를 표시하면 실패하는 리소스 유형에 대한 서비스 할당량을 확인합니다. 계정 제한이 리소스 생성을 방해할 수 있습니다.

7. 실패가 지속적이지 않고 간헐적인 경우(플레이북 4단계 패턴 분석) 리소스 이름 충돌 또는 리전 용량 제약과 같은 일시적 문제가 원인일 수 있습니다.

상관관계를 찾을 수 없는 경우: 분석을 48시간으로 확장하고, 템플릿 파라미터 검증을 검토하고, 중첩 스택 구성 문제를 확인하고, 스택 세트 배포 충돌을 확인하고, 리소스 이름 고유성 요구사항을 검사하고, 서비스 할당량 제한을 검토합니다.
