---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/01-Compute/Failing-on-EC2-Instances-CodeDeploy.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- codedeploy
- compute
- ec2
- failing
- iam
- incident-response
- instances
- k8s-deployment
- k8s-service
- performance
---

# EC2 인스턴스에서 CodeDeploy 실패 (CodeDeploy Failing on EC2 Instances)

## 의미

CodeDeploy 배포가 EC2 인스턴스에서 실패합니다(배포 실패 또는 CodeDeployDeploymentFailure 알람 트리거). CodeDeploy 에이전트가 실행 중이지 않거나, IAM 인스턴스 프로파일 권한이 부족하거나, 배포 그룹 설정이 잘못되었거나, 애플리케이션 중지 스크립트가 실패하거나, 배포 중 인스턴스 헬스 체크가 실패하거나, CodeDeploy 에이전트 버전이 호환되지 않기 때문입니다. CodeDeploy 배포가 실패하고, 애플리케이션 업데이트를 배포할 수 없으며, EC2 인스턴스가 새 코드를 수신하지 못합니다. 이는 CI/CD 및 배포 계층에 영향을 미치며 애플리케이션 업데이트를 차단합니다. 일반적으로 에이전트 이슈, 권한 문제, 또는 설정 에러가 원인이며, 인스턴스가 컨테이너 워크로드를 호스팅하는 경우 CodeDeploy 동작이 다를 수 있고 애플리케이션에서 배포 실패가 발생할 수 있습니다.

## 영향

CodeDeploy 배포 실패; 애플리케이션 업데이트 배포 불가; EC2 인스턴스가 새 코드를 수신하지 못함; 배포 자동화 차단; 인스턴스 헬스 체크 실패; 배포 롤백 발생; 애플리케이션 버전이 구버전으로 유지; 배포 프로세스 중단. CodeDeployDeploymentFailure 알람 발생 가능; 인스턴스가 컨테이너 워크로드를 호스팅하는 경우 CodeDeploy 동작이 다를 수 있음; 실패한 배포로 인해 애플리케이션에 에러 또는 성능 저하 발생 가능; 애플리케이션 버전이 구버전으로 유지될 수 있음.

## 플레이북

1. CodeDeploy 애플리케이션 `<application-name>`과 배포 그룹 `<deployment-group-name>`이 존재하고, 리전 `<region>`에서 CodeDeploy의 AWS 서비스 상태가 정상인지 확인합니다.
2. 배포 그룹 `<deployment-group-name>`의 CodeDeploy 배포 이력을 조회하여 최근 배포 실패, 배포 상태, 인스턴스 배포 상태를 검사하고, 실패 패턴을 분석합니다.
3. CodeDeploy 에이전트 로그가 포함된 로그 그룹의 CloudWatch Logs를 조회하여 배포 실패 패턴, 에이전트 에러, 또는 헬스 체크 실패(에이전트 에러 메시지 포함)를 필터링합니다.
4. 리전 `<region>`의 CodeDeploy 애플리케이션 `<application-name>`과 배포 그룹 `<deployment-group-name>`을 조회하여 배포 설정, 헬스 체크 설정, 인스턴스 선택 기준을 검사하고, 배포 그룹 설정을 검증합니다.
5. 배포 그룹 `<deployment-group-name>`의 EC2 인스턴스에 연결된 IAM 인스턴스 프로파일 `<instance-profile-name>`을 조회하여 CodeDeploy 작업에 대한 정책 권한을 검사하고, IAM 권한을 검증합니다.
6. 배포 그룹 `<deployment-group-name>`의 EC2 인스턴스를 나열하고 CodeDeploy 에이전트 상태, 인스턴스 상태, 배포 상태를 확인하여 에이전트가 실행 중인지 검증합니다.
7. 배포 그룹 `<deployment-group-name>`의 CodeDeploy 배포 설정을 조회하여 배포 설정을 확인하고, 배포 유형 및 배포 설정을 점검합니다.
8. CloudTrail 이벤트가 포함된 로그 그룹의 CloudWatch Logs를 조회하여 최근 24시간 이내 `<deployment-group-name>`과 관련된 CodeDeploy 배포 그룹 또는 애플리케이션 수정 이벤트를 필터링하고, 설정 변경을 확인합니다.
9. CodeDeploy 애플리케이션 `<application-name>`의 CloudWatch 메트릭(DeploymentFailures 포함)을 최근 24시간 동안 조회하여 배포 실패 패턴을 파악합니다.

## 진단

1. 플레이북 2단계의 CodeDeploy 배포 이력을 분석하여 실패가 처음 나타난 시점을 파악합니다. 배포 ID와 실패 타임스탬프가 상관관계 기준선을 확립합니다.

2. 플레이북 2단계의 인스턴스 배포 상태에서 특정 인스턴스에서만 실패하고 다른 인스턴스는 성공하는 경우, 실패한 인스턴스의 에이전트 상태(플레이북 6단계)를 검사합니다. 에이전트가 실행 중이지 않으면, 에이전트 설치 또는 서비스 이슈가 근본 원인입니다.

3. 플레이북 3단계의 에이전트 로그에서 권한 에러가 표시되면, IAM 인스턴스 프로파일 권한(플레이북 5단계)을 확인합니다. CodeDeploy 또는 S3 권한이 누락되면 아티팩트 다운로드 및 배포 실행이 방해됩니다.

4. 플레이북 8단계의 CloudTrail에서 실패 타임스탬프 전후로 배포 그룹 수정이 표시되면, 설정 변경이 호환되지 않는 설정을 도입했거나 인스턴스 선택 기준을 변경했을 수 있습니다.

5. 플레이북 3단계의 CloudWatch Logs에서 애플리케이션 라이프사이클 스크립트 실패(ApplicationStop, BeforeInstall 등)가 표시되면, 배포가 특정 훅에서 실패하고 있습니다. 커스텀 배포 로직의 에러에 대해 실패하는 스크립트를 검사합니다.

6. 플레이북 7단계의 배포 설정에서 헬스 체크 요구사항이 표시되면, 인스턴스가 헬스 체크를 통과할 수 있는지 확인합니다. 공격적인 헬스 체크 설정이 배포 완료 전에 인스턴스를 실패시킬 수 있습니다.

7. 플레이북 9단계의 배포 메트릭에서 지속적인 실패가 표시되면, 설정 또는 스크립트 관련 이슈입니다. 간헐적이면, 에이전트 연결 또는 일시적 인프라 이슈가 원인입니다.

상관관계를 찾을 수 없는 경우: 분석을 48시간으로 확장하고, CodeDeploy 에이전트 버전 호환성을 확인하고, 배포 설정 유형(인플레이스 vs 블루/그린)을 점검하고, 애플리케이션 스크립트 의존성을 검사하고, 헬스 체크 임계값 설정을 검토합니다.
