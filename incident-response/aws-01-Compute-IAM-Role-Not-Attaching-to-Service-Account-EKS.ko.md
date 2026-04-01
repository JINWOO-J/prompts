---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/01-Compute/IAM-Role-Not-Attaching-to-Service-Account-EKS.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- account
- attaching
- cloudwatch
- compute
- eks
- iam
- incident-response
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- performance
- role
- security
- service
- sts
---

# EKS IAM 역할이 서비스 계정에 연결되지 않음 (IAM Role Not Attaching to Service Account)

## 의미

EKS IAM 역할이 서비스 계정에 연결되지 않습니다(권한 실패 또는 EKSServiceAccountIRSAFailure 알람 트리거). IAM 역할 신뢰 정책이 서비스 계정을 허용하지 않거나, 서비스 계정 어노테이션이 잘못되었거나, IAM 역할 ARN이 틀리거나, OIDC 프로바이더가 설정되지 않았거나, 서비스 계정과 IAM 역할이 다른 계정에 있거나, EKS 클러스터 OIDC 프로바이더가 누락되었기 때문입니다. EKS 서비스 계정이 IAM 역할을 수임할 수 없고, Pod 권한이 부족하며, 애플리케이션 Pod가 AWS 서비스에 접근할 수 없습니다. 이는 컨테이너 오케스트레이션 및 보안 계층에 영향을 미치며 서비스 접근을 차단합니다. 일반적으로 IRSA(IAM Roles for Service Accounts) 설정 이슈, OIDC 프로바이더 문제, 또는 신뢰 정책 에러가 원인이며, 여러 네임스페이스를 사용하는 EKS의 경우 서비스 계정 설정이 다를 수 있고 애플리케이션에서 권한 실패가 발생할 수 있습니다.

## 영향

EKS 서비스 계정이 IAM 역할을 수임할 수 없음; Pod 권한 부족; 서비스 계정 IAM 통합 실패; Pod IAM 역할 연결 에러 발생; 애플리케이션 Pod가 AWS 서비스에 접근 불가; IAM 역할 기반 접근 실패; Kubernetes 서비스 계정 자동화 비효과적. EKSServiceAccountIRSAFailure 알람 발생 가능; 여러 네임스페이스를 사용하는 EKS의 경우 서비스 계정 설정이 다를 수 있음; AWS 서비스 권한 누락으로 인해 애플리케이션에 에러 또는 성능 저하 발생 가능; Pod가 필요한 AWS 리소스에 접근 불가.

## 플레이북

1. EKS 클러스터 `<cluster-name>`이 존재하고 리전 `<region>`에서 EKS 및 IAM의 AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 EKS 클러스터 `<cluster-name>`을 조회하여 OIDC 프로바이더 설정, OIDC 프로바이더 URL, IAM 역할 신뢰 관계를 검사하고, OIDC 프로바이더가 설정되어 있는지 검증합니다.
3. EKS Pod 로그가 포함된 로그 그룹의 CloudWatch Logs를 조회하여 IAM 역할 연결 실패 패턴, 권한 에러, 또는 서비스 계정 어노테이션 에러(Pod 에러 메시지 포함)를 필터링합니다.
4. 서비스 계정에 연결되어야 하는 IAM 역할 `<role-arn>`을 조회하여 신뢰 정책, 서비스 계정 신뢰 관계, OIDC 프로바이더 설정을 검사하고, 신뢰 정책 형식을 검증합니다.
5. 클러스터 `<cluster-name>`의 EKS 서비스 계정을 나열하고 서비스 계정 어노테이션, IAM 역할 어노테이션, 서비스 계정 설정을 확인하여, 어노테이션 형식을 검증합니다.
6. CloudTrail 이벤트가 포함된 로그 그룹의 CloudWatch Logs를 조회하여 EKS 서비스 계정 IAM 역할 수임 실패 또는 권한 거부 이벤트(AssumeRole 실패 포함)를 필터링합니다.
7. EKS 클러스터 `<cluster-name>`의 OIDC 프로바이더 발급자 URL을 조회하여 OIDC 프로바이더가 접근 가능한지 확인하고, OIDC 프로바이더 상태를 점검합니다.
8. IAM 역할 `<role-arn>`의 신뢰 정책을 조회하여 신뢰 정책 조건이 서비스 계정 네임스페이스 및 이름과 일치하는지 확인하고, 신뢰 정책 조건 형식을 점검합니다.
9. CloudTrail 이벤트가 포함된 로그 그룹의 CloudWatch Logs를 조회하여 최근 24시간 이내 클러스터 `<cluster-name>`과 관련된 EKS 클러스터 OIDC 프로바이더 또는 IAM 역할 신뢰 정책 수정 이벤트를 필터링하고, 설정 변경을 확인합니다.

## 진단

1. 플레이북 3단계와 6단계의 EKS Pod 로그 및 CloudTrail 이벤트가 포함된 CloudWatch Logs를 분석하여 구체적인 권한 에러 메시지를 파악합니다. 에러가 "AccessDenied" 또는 "AssumeRoleWithWebIdentity failed"를 표시하면, IAM 역할 신뢰 정책 또는 OIDC 설정 이슈를 나타냅니다. 에러가 "InvalidIdentityToken"을 표시하면, OIDC 프로바이더 설정이 잘못되었습니다.

2. 플레이북 2단계의 EKS 클러스터 OIDC 프로바이더 설정을 확인하여 OIDC 프로바이더가 클러스터에 올바르게 연결되어 있는지 확인합니다. OIDC 프로바이더 URL이 누락되었거나 잘못된 경우, IRSA(IAM Roles for Service Accounts)가 작동할 수 없습니다. OIDC 프로바이더 발급자 URL이 클러스터의 OIDC 엔드포인트와 일치해야 합니다.

3. 플레이북 4단계와 8단계의 IAM 역할 신뢰 정책을 검사하여 신뢰 정책이 EKS 클러스터의 OIDC 프로바이더를 올바르게 참조하고 서비스 계정에 대한 적절한 조건을 포함하는지 확인합니다. 신뢰 정책 조건이 서비스 계정 네임스페이스 및 이름 형식 "system:serviceaccount:NAMESPACE:SERVICE_ACCOUNT_NAME"과 일치하지 않으면, 역할 수임이 실패합니다.

4. 플레이북 5단계의 서비스 계정 어노테이션을 검토하여 `eks.amazonaws.com/role-arn` 어노테이션에 올바른 IAM 역할 ARN이 포함되어 있는지 확인합니다. 어노테이션이 누락되었거나, 형식이 잘못되었거나, 존재하지 않는 역할을 참조하면, Pod가 IAM 역할을 수임할 수 없습니다.

5. 플레이북 9단계의 CloudTrail 이벤트를 IAM 역할 연결 실패 타임스탬프와 5분 이내로 상관 분석하여 OIDC 프로바이더, IAM 역할 신뢰 정책, 또는 서비스 계정 설정에 대한 최근 수정을 파악합니다.

6. 1시간 이내 다른 서비스 계정 간 연결 실패 패턴을 비교합니다. 실패가 서비스 계정별인 경우, 해당 서비스 계정의 어노테이션 및 네임스페이스 설정을 확인합니다. 실패가 동일한 IAM 역할을 사용하는 모든 서비스 계정에 영향을 미치면, 신뢰 정책이 잘못 설정되었습니다. 실패가 모든 IRSA 설정에 영향을 미치는 클러스터 전체 문제이면, OIDC 프로바이더 연결이 문제입니다.

7. 플레이북 7단계의 OIDC 프로바이더 접근성을 확인하여 OIDC 엔드포인트가 접근 가능하고 인증서가 유효한지 확인합니다. OIDC 프로바이더 인증서가 만료되었거나 엔드포인트에 접근할 수 없으면, 모든 IRSA 작업이 실패합니다.

지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우: 기간을 48시간으로 확장하고, 서비스 계정 네임스페이스 설정 및 IAM 역할 ARN 형식을 포함한 대안적 증거 소스를 검토하고, OIDC 프로바이더 인증서 만료 또는 신뢰 정책 조건 변경 같은 점진적 이슈를 확인하고, OIDC 프로바이더 가용성 또는 IAM 서비스 상태 같은 외부 의존성을 검증하고, IAM 역할 연결 실패의 과거 패턴을 검사하고, EKS 클러스터 OIDC 프로바이더 연결 이슈를 확인하고, EKS 서비스 계정 어노테이션 네임스페이스 형식을 검증합니다. 연결 실패는 즉각적인 서비스 계정 설정 변경이 아닌 OIDC 프로바이더 설정 이슈, 서비스 계정 어노테이션 형식 에러, IAM 역할 신뢰 정책 조건 문제, EKS 클러스터 OIDC 프로바이더 연결 이슈, 또는 서비스 계정 어노테이션 네임스페이스 형식 에러로 인해 발생할 수 있습니다.
