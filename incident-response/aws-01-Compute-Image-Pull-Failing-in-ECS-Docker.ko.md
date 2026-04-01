---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/01-Compute/Image-Pull-Failing-in-ECS-Docker.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- compute
- docker
- ecs
- failing
- fargate
- iam
- image
- incident-response
- k8s-deployment
- k8s-service
- performance
- pull
- sts
---

# ECS에서 Docker 이미지 풀 실패 (Docker Image Pull Failing in ECS)

## 의미

ECS에서 Docker 이미지 풀이 실패합니다(이미지 풀 에러 또는 ECSImagePullFailed 알람 트리거). ECR 리포지토리 접근이 거부되거나, IAM 태스크 실행 역할에 ECR 권한이 부족하거나, 이미지가 리포지토리에 존재하지 않거나, 이미지 태그가 잘못되었거나, ECR 리포지토리 정책이 접근을 제한하거나, ECS 태스크 네트워크 설정이 ECR 접근을 방해하기 때문입니다. ECS 태스크가 Docker 이미지를 풀할 수 없고, 컨테이너 이미지 풀 에러가 발생하며, 태스크 시작이 실패합니다. 이는 컨테이너 오케스트레이션 계층에 영향을 미치며 컨테이너 배포를 차단합니다. 일반적으로 ECR 권한 이슈, 이미지 가용성 문제, 또는 네트워크 설정 에러가 원인이며, Fargate와 함께 ECS를 사용하는 경우 ECR 접근 동작이 다를 수 있고 애플리케이션에서 이미지 풀 실패가 발생할 수 있습니다.

## 영향

ECS 태스크가 Docker 이미지를 풀할 수 없음; 컨테이너 이미지 풀 에러 발생; 태스크 시작 실패; ECR 이미지 접근 거부; 컨테이너 배포 차단; 이미지 풀 자동화 실패; 태스크 정의가 컨테이너를 시작할 수 없음; 애플리케이션 컨테이너 시작 불가. ECSImagePullFailed 알람 발생 가능; Fargate와 함께 ECS를 사용하는 경우 ECR 접근 동작이 다를 수 있음; 실패한 컨테이너 시작으로 인해 애플리케이션에 에러 또는 성능 저하 발생 가능; 컨테이너 워크로드 배포 불가.

## 플레이북

1. ECS 태스크 정의 `<task-definition-arn>`이 존재하고 리전 `<region>`에서 ECS 및 ECR의 AWS 서비스 상태가 정상인지 확인합니다.
2. ECS 태스크 정의 `<task-definition-arn>`을 조회하여 컨테이너 이미지 설정, 이미지 URI, ECR 리포지토리 참조를 검사하고, 이미지 URI 형식을 검증합니다.
3. ECS 태스크 실행에 사용되는 IAM 역할 `<role-name>`을 조회하여 GetAuthorizationToken, BatchGetImage, GetDownloadUrlForLayer를 포함한 ECR 작업에 대한 정책 권한을 검사하고, IAM 권한을 검증합니다.
4. ECS 태스크 로그가 포함된 로그 그룹의 CloudWatch Logs를 조회하여 이미지 풀 실패 패턴, ECR 접근 거부 에러, 또는 Docker 풀 에러(에러 메시지 세부사항 포함)를 필터링합니다.
5. 태스크 정의에서 참조하는 ECR 리포지토리 `<repository-name>`을 조회하여 리포지토리 정책, 이미지 태그, 리포지토리 접근 설정을 검사하고, 이미지 존재 여부를 확인합니다.
6. 클러스터 `<cluster-name>`의 ECS 태스크 실패를 나열하고 이미지 풀 에러 패턴과 태스크 실패 원인을 확인하여, 실패 패턴을 분석합니다.
7. VPC를 사용하는 경우 ECS 태스크 정의 `<task-definition-arn>`의 네트워크 설정을 조회하여 ECR로의 네트워크 연결을 확인하고, VPC 설정이 ECR 접근을 차단하는지 점검합니다.
8. ECR 리포지토리 `<repository-name>`의 CloudWatch 메트릭(가용한 경우 ImagePullCount 포함)을 조회하여 리포지토리 활동을 확인하고, 리포지토리가 접근 가능한지 점검합니다.
9. CloudTrail 이벤트가 포함된 로그 그룹의 CloudWatch Logs를 조회하여 최근 24시간 이내 태스크 실행 역할 `<role-name>`과 관련된 ECR 리포지토리 정책 또는 IAM 역할 정책 수정 이벤트를 필터링하고, 권한 변경을 확인합니다.

## 진단

1. 플레이북 4단계의 ECS 태스크 로그가 포함된 CloudWatch Logs를 분석하여 구체적인 이미지 풀 에러 메시지를 파악합니다. 에러가 "AccessDeniedException" 또는 "authorization token"을 나타내면, 즉시 IAM 권한 검증으로 진행합니다. 에러가 "CannotPullContainerError"와 "not found"를 나타내면, 이미지 또는 태그가 존재하지 않습니다. 에러가 네트워크 타임아웃을 나타내면, VPC 또는 엔드포인트 설정이 문제입니다.

2. 접근 거부 에러의 경우, 플레이북 3단계의 IAM 태스크 실행 역할 권한을 확인하여 역할에 ecr:GetAuthorizationToken, ecr:BatchGetImage, ecr:GetDownloadUrlForLayer 권한이 있는지 확인합니다. 이 권한 중 하나라도 누락되면 이미지 풀이 실패합니다. 또한 역할이 특정 ECR 리포지토리에 접근할 수 있는지 확인합니다.

3. 플레이북 5단계의 ECR 리포지토리 설정을 검토하여 올바른 태그로 이미지가 존재하는지 확인합니다. 태스크 정의에서 참조하는 이미지 태그가 리포지토리에 존재하지 않으면 풀이 실패합니다. 라이프사이클 정책이 이미지를 삭제했을 수 있는지 확인합니다.

4. 플레이북 2단계의 태스크 정의 이미지 URI 설정을 검사하여 ECR 리포지토리 URI와 이미지 태그가 올바른 형식인지 확인합니다. 리포지토리 URI가 잘못되었거나 존재하지 않는 리포지토리를 가리키면 이미지 풀이 실패합니다.

5. Fargate 태스크의 경우, 플레이북 7단계의 VPC 네트워크 설정을 확인하여 태스크가 ECR에 접근할 수 있는지 확인합니다. NAT Gateway 또는 ECR VPC 엔드포인트 없이 프라이빗 서브넷을 사용하는 경우, 태스크가 ECR에서 이미지를 풀할 수 없습니다.

6. 플레이북 9단계의 CloudTrail 이벤트를 이미지 풀 실패 타임스탬프와 5분 이내로 상관 분석하여 ECR 리포지토리 정책 또는 IAM 역할 정책 수정을 파악합니다. 권한 변경이 이미지 풀 실패 시작 시점과 일치하면, 해당 변경이 원인일 가능성이 높습니다.

7. 1시간 이내 다른 태스크 정의 간 이미지 풀 실패 패턴을 비교합니다. 실패가 태스크 정의별인 경우, 해당 태스크의 이미지 URI 또는 설정 문제입니다. 실패가 동일한 실행 역할을 사용하는 모든 태스크에 영향을 미치면, IAM 권한이 근본 원인입니다.

8. 가용한 경우 플레이북 8단계의 ECR 리포지토리 메트릭을 검토하여 리포지토리 활동과 접근성을 확인합니다. 리포지토리에 최근 이미지 풀 활동이 없으면, 더 광범위한 접근 이슈가 있을 수 있습니다.

지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우: 기간을 48시간으로 확장하고, ECR 리포지토리 이미지 가용성 및 이미지 태그 존재를 포함한 대안적 증거 소스를 검토하고, ECR 리포지토리 정책 변경 또는 이미지 라이프사이클 정책 삭제 같은 점진적 이슈를 확인하고, ECR 서비스 가용성 또는 ECR로의 네트워크 연결 같은 외부 의존성을 검증하고, 이미지 풀 실패의 과거 패턴을 검사하고, ECS Fargate ECR 접근 VPC 엔드포인트 요구사항을 확인하고, ECR 이미지 스캐닝이 풀을 차단하는지 검증합니다. 이미지 풀 실패는 즉각적인 태스크 정의 변경이 아닌 이미지 태그 삭제, ECR 리포지토리 라이프사이클 정책 액션, ECR 서비스 이슈, ECS Fargate ECR VPC 엔드포인트 요구사항, 또는 ECR 이미지 스캐닝 실패로 인해 발생할 수 있습니다.
