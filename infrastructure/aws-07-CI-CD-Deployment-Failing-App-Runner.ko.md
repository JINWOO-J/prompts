---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/07-CI-CD/Deployment-Failing-App-Runner.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- ci-cd
- cloudwatch
- deployment
- failing
- iam
- infrastructure
- k8s-deployment
- k8s-service
- performance
- runner
- sts
---

# AWS App Runner 배포 실패

## 의미

AWS App Runner 배포가 실패(배포 실패 또는 AppRunnerDeploymentFailed 알람 트리거)하는 이유는 소스 코드 저장소 접근이 거부되었거나, 빌드 구성에 오류가 있거나, IAM 역할 권한이 부족하거나, 빌드 프로세스에서 오류가 발생하거나, 배포 구성이 유효하지 않거나, App Runner 서비스 구성이 잘못되었기 때문입니다. App Runner 배포가 실패하고, 애플리케이션 업데이트를 배포할 수 없으며, 배포 자동화가 차단됩니다. 이는 서버리스 컨테이너 배포 계층에 영향을 미치며 애플리케이션 업데이트를 차단합니다. 일반적으로 소스 접근 문제, 빌드 구성 문제 또는 권한 실패로 인해 발생합니다. 다른 소스 유형으로 App Runner를 사용하는 경우 구성이 다를 수 있으며 애플리케이션에서 배포 실패가 발생할 수 있습니다.

## 영향

App Runner 배포 실패; 애플리케이션 업데이트 배포 불가; 배포 자동화 차단; 빌드 프로세스 오류 발생; 소스 코드 접근 거부; 배포 구성 무효; 애플리케이션 버전 구식 유지; 배포 프로세스 완료 불가. AppRunnerDeploymentFailed 알람이 발생할 수 있으며, 다른 소스 유형으로 App Runner를 사용하는 경우 구성이 다를 수 있고, 실패한 배포로 인해 애플리케이션에서 오류 또는 성능 저하가 발생할 수 있으며, 애플리케이션 버전이 구식으로 유지될 수 있습니다.

## 플레이북

1. App Runner 서비스 `<service-name>`이 존재하고 리전 `<region>`에서 App Runner의 AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`에서 App Runner 서비스 `<service-name>`을 조회하고 소스 구성, 빌드 구성, 배포 상태, 서비스 상태를 검사하여 소스 및 빌드 구성을 확인합니다.
3. App Runner 빌드 로그가 포함된 CloudWatch Logs 로그 그룹을 쿼리하고 배포 실패 패턴, 빌드 오류 또는 소스 접근 오류를 필터링하여 오류 메시지 세부 정보를 포함합니다.
4. App Runner 서비스에서 사용하는 IAM 역할 `<role-name>`을 조회하고 소스 저장소 접근 및 빌드 작업에 대한 정책 권한을 검사하여 IAM 권한을 확인합니다.
5. 지난 24시간 동안 App Runner 서비스 `<service-name>`의 DeploymentCount 및 FailedDeploymentCount를 포함한 CloudWatch 메트릭을 조회하여 배포 실패 패턴을 식별하고 실패 빈도를 분석합니다.
6. 서비스 `<service-name>`의 App Runner 서비스 배포를 나열하고 배포 상태, 실패 이유, 배포 타임스탬프를 확인하여 배포 이력을 분석합니다.
7. App Runner 서비스 `<service-name>` 소스 구성을 조회하고 소스 저장소 접근을 확인하며, 소스 유형(GitHub, CodeCommit 또는 소스 이미지)이 구성에 영향을 미치는지 확인합니다.
8. CloudTrail 이벤트가 포함된 CloudWatch Logs 로그 그룹을 쿼리하고 지난 24시간 이내 서비스 `<service-name>`과 관련된 App Runner 서비스 구성 수정 이벤트를 필터링하여 구성 변경을 확인합니다.
9. App Runner 서비스 `<service-name>` 빌드 구성을 조회하고 buildspec 또는 빌드 명령을 확인하여 빌드 구성이 실패를 유발하는지 확인합니다.

## 진단

1. App Runner 빌드 로그가 포함된 CloudWatch Logs(플레이북 3단계)를 분석하여 특정 배포 실패 오류 메시지를 식별합니다. 오류가 소스 저장소에 대한 "AccessDenied"를 나타내면 IAM 권한 확인으로 진행합니다. 오류가 빌드 실패를 나타내면 빌드 명령 출력에서 특정 오류를 검사합니다. 오류가 이미지 풀 실패를 나타내면 소스 이미지 인증을 확인합니다.

2. 접근 거부 오류의 경우, App Runner 서비스와 연결된 IAM 역할 권한(플레이북 4단계)을 검토합니다. IAM 역할에 소스 저장소(CodeCommit, GitHub 또는 ECR) 접근 권한이 없으면 배포를 진행할 수 없습니다. 사용 중인 소스 유형에 필요한 권한이 역할에 있는지 확인합니다.

3. DeploymentCount 및 FailedDeploymentCount에 대한 CloudWatch 메트릭(플레이북 5단계)을 검토하여 배포 패턴을 수립합니다. 실패한 배포가 갑자기 증가한 경우 타임스탬프를 최근 구성 변경과 상관시킵니다. 실패가 지속적인 경우 지속적인 구성 문제일 가능성이 높습니다.

4. App Runner 서비스 구성(플레이북 2단계)을 검사하여 소스 및 빌드 설정을 확인합니다. 소스 저장소 URL이 잘못되었거나, 브랜치 이름이 틀리거나, 빌드 명령에 구문 오류가 있으면 배포가 지속적으로 실패합니다.

5. 배포 이력(플레이북 6단계)을 검토하여 실패 패턴과 특정 실패 이유를 식별합니다. 동일한 빌드 단계에서 지속적으로 실패가 발생하면 해당 단계에 구성 문제가 있습니다. 무작위로 실패가 발생하면 일시적인 연결 또는 리소스 가용성 문제일 수 있습니다.

6. CloudTrail 이벤트(플레이북 8단계)를 배포 실패 타임스탬프와 30분 이내로 상관시켜 배포가 실패하기 시작한 시점과 일치하는 서비스 구성 수정을 식별합니다.

7. 1시간 이내에 다른 App Runner 서비스 간의 배포 실패 패턴을 비교합니다. 실패가 서비스별인 경우 해당 서비스의 구성 문제입니다. 실패가 여러 서비스에 영향을 미치는 계정 전체인 경우 IAM 권한 또는 서비스 수준 문제일 가능성이 높습니다.

8. 소스 이미지 배포의 경우, 소스 이미지 인증 및 ECR 저장소 접근(플레이북 7단계)을 확인합니다. 이미지 풀 자격 증명이 만료되었거나 ECR 저장소 정책이 접근을 제한하면 이미지 풀 중 배포가 실패합니다.

지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우: 시간 범위를 30일로 확장하고, 소스 저장소 연결 및 빌드 프로세스 로그를 포함한 대체 증거 소스를 검토하고, 소스 저장소 접근 변경 또는 빌드 의존성 업데이트와 같은 점진적 문제를 확인하고, 소스 저장소 가용성 또는 빌드 서비스 상태와 같은 외부 의존성을 확인하고, 배포 실패의 과거 패턴을 검사하고, App Runner 소스 이미지 인증 문제를 확인하고, App Runner 빌드 타임아웃 설정을 확인합니다. 배포 실패는 즉각적인 서비스 구성 변경이 아닌 소스 저장소 접근 문제, 빌드 구성 오류, App Runner 서비스 문제, App Runner 소스 이미지 인증 실패 또는 App Runner 빌드 타임아웃 설정으로 인해 발생할 수 있습니다.
