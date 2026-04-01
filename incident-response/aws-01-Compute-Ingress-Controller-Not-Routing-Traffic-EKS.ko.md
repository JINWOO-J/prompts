---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/01-Compute/Ingress-Controller-Not-Routing-Traffic-EKS.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudwatch
- compute
- controller
- eks
- incident-response
- ingress
- k8s-deployment
- k8s-ingress
- k8s-pod
- k8s-service
- kubernetes
- networking
- performance
- routing
- sts
- traffic
---

# EKS Ingress Controller 트래픽 라우팅 실패 (Ingress Controller Not Routing Traffic)

## 의미

EKS Ingress Controller가 트래픽을 라우팅하지 않습니다(라우팅 실패 또는 EKSIngressRoutingFailed 알람 트리거). Ingress Controller가 배포되지 않았거나, Ingress 리소스 설정이 잘못되었거나, Ingress Controller 서비스가 노출되지 않았거나, Ingress 규칙이 요청 경로와 일치하지 않거나, Ingress Controller Pod가 실행 중이지 않거나, Ingress Controller 로드 밸런서 설정이 라우팅을 차단하기 때문입니다. EKS Ingress 라우팅이 실패하고, Kubernetes Ingress 리소스가 트래픽을 라우팅하지 않으며, 애플리케이션 Ingress 접근이 실패합니다. 이는 컨테이너 오케스트레이션 및 네트워킹 계층에 영향을 미치며 외부 접근을 차단합니다. 일반적으로 Ingress Controller 배포 이슈, 설정 문제, 또는 로드 밸런서 이슈가 원인이며, AWS Load Balancer Controller와 함께 EKS를 사용하는 경우 Controller 설정이 다를 수 있고 애플리케이션에서 Ingress 라우팅 실패가 발생할 수 있습니다.

## 영향

EKS Ingress 라우팅 실패; Kubernetes Ingress 리소스가 트래픽을 라우팅하지 않음; Ingress Controller 비효과적; 애플리케이션 Ingress 접근 실패; Ingress 규칙 미적용; Ingress Controller 서비스 접근 불가; Kubernetes Ingress 자동화 실패; 서비스에 대한 외부 접근 차단. EKSIngressRoutingFailed 알람 발생 가능; AWS Load Balancer Controller와 함께 EKS를 사용하는 경우 Controller 설정이 다를 수 있음; 차단된 Ingress 접근으로 인해 애플리케이션에 에러 또는 성능 저하 발생 가능; 외부 사용자가 서비스에 접근 불가.

## 플레이북

1. EKS 클러스터 `<cluster-name>`이 존재하고 리전 `<region>`에서 EKS의 AWS 서비스 상태가 정상인지 확인합니다.
2. 클러스터 `<cluster-name>`의 EKS Pod 로그가 포함된 로그 그룹의 CloudWatch Logs를 조회하여 Ingress Controller Pod 로그, Ingress Controller 에러, 또는 라우팅 실패 패턴(Pod 상태 포함)을 필터링합니다.
3. 리전 `<region>`의 EKS 클러스터 `<cluster-name>`을 조회하여 Ingress Controller 배포 상태, Ingress Controller 서비스 설정, Ingress 리소스 설정을 검사하고, Controller가 배포되어 있는지 검증합니다.
4. Ingress Controller 네임스페이스의 EKS Pod를 나열하고 Pod 상태, Pod 로그, Ingress Controller Pod 상태를 확인하여, Pod가 실행 중인지 검증합니다.
5. 애플리케이션 접근 로그가 포함된 로그 그룹의 CloudWatch Logs를 조회하여 Ingress 리소스와 관련된 Ingress 라우팅 실패 또는 404 에러 패턴(라우팅 에러 세부사항 포함)을 필터링합니다.
6. EKS Ingress Controller의 CloudWatch 메트릭(요청 수 및 에러율 포함)을 최근 1시간 동안 조회하여 라우팅 패턴을 파악하고, 트래픽 흐름을 분석합니다.
7. EKS Ingress Controller 서비스 설정을 조회하여 서비스 유형과 로드 밸런서 설정을 확인하고, 로드 밸런서가 올바르게 설정되어 있는지 점검합니다.
8. AWS Load Balancer Controller를 사용하는 경우 EKS 클러스터 `<cluster-name>`의 OIDC 프로바이더 설정을 조회하여 IAM 역할 권한을 확인하고, Controller IAM 역할 설정을 점검합니다.
9. CloudTrail 이벤트가 포함된 로그 그룹의 CloudWatch Logs를 조회하여 최근 24시간 이내 클러스터 `<cluster-name>`과 관련된 EKS Ingress 리소스 또는 서비스 수정 이벤트를 필터링하고, 설정 변경을 확인합니다.

## 진단

1. 플레이북 2단계의 Ingress Controller Pod 로그가 포함된 CloudWatch Logs를 분석하여 라우팅 실패 패턴, 에러 메시지, 또는 연결 이슈를 파악합니다. 로그에 404 또는 503 같은 특정 에러 코드가 표시되면, 이슈가 경로 매칭인지 백엔드 비가용인지를 나타냅니다. 로그에 Controller 시작 에러가 표시되면, Controller 배포 자체에 문제가 있습니다.

2. 플레이북 6단계의 Ingress Controller 요청 수 및 에러율에 대한 CloudWatch 메트릭을 검토하여 기준 트래픽 패턴을 확립합니다. 에러율이 갑자기 증가했다면, 타임스탬프를 최근 설정 변경과 상관 분석합니다. 메트릭에서 Controller에 도달하는 트래픽이 0이면, 이슈는 로드 밸런서 또는 서비스 수준에 있습니다.

3. 플레이북 4단계의 Ingress Controller Pod 상태를 확인하여 Pod가 실행 중이고 정상인지 확인합니다. Pod가 CrashLoopBackOff 또는 ImagePullBackOff 상태를 보이면, Controller가 트래픽을 라우팅할 수 없습니다. Pod가 실행 중이지만 로그에 에러가 표시되면, 설정 분석으로 진행합니다.

4. AWS Load Balancer Controller를 사용하는 경우, 플레이북 8단계의 Controller 서비스 계정에 대한 IAM 역할 권한을 확인합니다. OIDC 프로바이더 설정이 잘못되었거나 IAM 역할 신뢰 정책이 잘못 설정되면, Controller가 로드 밸런서를 프로비저닝하거나 관리할 수 없어 트래픽 라우팅이 방해됩니다.

5. 플레이북 3단계의 Ingress 리소스 설정을 검사하여 경로 규칙, 백엔드 서비스, 어노테이션이 올바르게 정의되어 있는지 확인합니다. Ingress 규칙이 수신 요청 경로와 일치하지 않으면, 요청이 404 에러를 반환합니다. 백엔드 서비스 셀렉터가 실행 중인 Pod와 일치하지 않으면, 트래픽이 애플리케이션에 도달할 수 없습니다.

6. 플레이북 9단계의 CloudTrail 이벤트를 라우팅 실패 타임스탬프와 5분 이내로 상관 분석하여 EKS Ingress 리소스 또는 서비스 수정을 파악합니다. 설정 변경이 라우팅 실패 시작과 일치하면, 해당 변경이 원인일 가능성이 높습니다.

7. 1시간 이내 다른 Ingress 리소스 간 라우팅 실패 패턴을 비교합니다. 실패가 Ingress별인 경우, 해당 Ingress 규칙 설정 문제입니다. 실패가 모든 Ingress 리소스에 영향을 미치는 Controller 전체 문제이면, Ingress Controller 배포 또는 서비스 설정이 근본 원인입니다.

지정된 시간 범위 내에서 상관관계를 찾을 수 없는 경우: 기간을 24시간으로 확장하고, Ingress Controller 배포 설정 및 Ingress 규칙 경로 매칭을 포함한 대안적 증거 소스를 검토하고, Ingress Controller Pod 퇴거 또는 서비스 엔드포인트 변경 같은 점진적 이슈를 확인하고, 로드 밸런서 설정 또는 Ingress Controller 이미지 가용성 같은 외부 의존성을 검증하고, Ingress 라우팅 실패의 과거 패턴을 검사하고, EKS AWS Load Balancer Controller 설정 이슈를 확인하고, EKS Ingress Controller 클래스 어노테이션을 검증합니다. 라우팅 실패는 즉각적인 Ingress 리소스 변경이 아닌 Ingress Controller 배포 이슈, Ingress 규칙 경로 매칭 문제, Ingress Controller 서비스 설정 에러, EKS AWS Load Balancer Controller 잘못된 설정, 또는 Ingress Controller 클래스 어노테이션 이슈로 인해 발생할 수 있습니다.
