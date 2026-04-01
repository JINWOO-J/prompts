---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/04-Cost-Optimization/Idle-Resource-Detection-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- cost
- detection
- idle
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-pvc
- k8s-service
- kubernetes
- monitoring
- optimization
- resource
- sts
---

# Idle Resource Detection (유휴 리소스 감지)

## 의미

유휴 리소스 감지 알림은 Kubernetes 리소스가 실행 중이지만 실제로 활용되지 않아 가치 없이 비용을 소비하는 상황(IdleResourceDetected 또는 UnusedResourceDetected 같은 알림 발생)을 나타냅니다. Pod의 낮은 CPU 사용률, Deployment의 최소 트래픽, PVC의 I/O 작업 없음, Service 미접근, 또는 리소스 메트릭의 최소 사용 표시 등이 원인입니다.
 리소스가 낮은 사용률 메트릭을 보이고, 리소스 활동 로그가 최소 사용을 나타내며, 비용 메트릭이 활동 없이 비용을 소비하는 리소스를 보이고, 리소스 모니터링이 유휴 상태를 나타냅니다. 이는 비용 관리 계층과 리소스 최적화에 영향을 미치며, 주로 과다 프로비저닝, 방치된 리소스, 또는 리소스 수명주기 관리 실패가 원인입니다. 유휴 리소스가 컨테이너 워크로드인 경우, 컨테이너 리소스가 낭비되고 애플리케이션이 불필요한 비용 오버헤드를 겪을 수 있습니다.

## 영향

IdleResourceDetected 알림 발생, UnusedResourceDetected 알림 발생, 불필요한 비용 누적, 리소스가 가치 없이 비용 소비, 비용 최적화 기회 미활용, 리소스 사용률 비효율. 낮은 사용률 메트릭이 유휴 리소스를 나타냅니다. 유휴 리소스가 컨테이너 워크로드인 경우, 컨테이너 리소스가 낭비되고, Pod 리소스가 과다 프로비저닝되며, 컨테이너 애플리케이션이 불필요한 비용 오버헤드를 겪을 수 있습니다. 애플리케이션이 비용 비효율이나 리소스 낭비를 경험할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 Pod, Deployment, Service, PVC를 wide 출력으로 조회하고 Deployment <deployment-name>을 describe하여 현재 리소스 상태와 설정을 파악합니다.

2. namespace <namespace>에서 최근 이벤트를 타임스탬프 순으로 조회하여 리소스 사용을 나타내는 최근 활동이나 상태 변경을 확인합니다.

3. namespace <namespace>에서 Pod를 조회하고 CPU 사용률과 메모리 사용률의 Prometheus 메트릭을 최근 30일 동안 조회하여 지속적으로 낮은 사용률을 가진 Pod를 식별합니다.

4. namespace <namespace>에서 Deployment를 조회하고 요청 수와 트래픽 메트릭의 Prometheus 메트릭을 최근 30일 동안 조회하여 최소 활동을 가진 Deployment를 식별합니다.

5. namespace <namespace>에서 PVC를 조회하고 볼륨 I/O 작업의 Prometheus 메트릭을 최근 30일 동안 조회하여 I/O 작업이 없는 PVC를 식별합니다.

6. namespace <namespace>에서 Service를 조회하고 서비스 요청 수와 엔드포인트 활동의 Prometheus 메트릭을 최근 30일 동안 조회하여 접근 패턴이 없는 Service를 식별합니다.

7. namespace <namespace>에서 Pod의 로그를 조회하고 최근 30일 동안 리소스 비활동이나 최소 사용을 나타내는 패턴을 필터링합니다.

8. 리소스 생성 타임스탬프와 마지막 활동 타임스탬프를 비교하여 리소스가 생성 이후 유휴 상태인지 확인하고, 리소스 활동 로그를 보조 증거로 활용합니다.

9. namespace <namespace>의 리소스 쿼터 사용량을 조회하고 리소스 사용률 메트릭과 비교하여 비용-사용률 불일치를 식별합니다.

10. namespace <namespace>에서 Job과 CronJob을 조회하고 실행 빈도를 확인하여 실행되지 않거나 실행률이 낮은 Job을 식별합니다.

## 진단

1. 3단계의 CPU 및 메모리 사용률 메트릭을 검토합니다. Pod가 30일 동안 지속적으로 10% 미만의 사용률을 보이면 유휴 리소스 정리나 적정 규모 조정의 강력한 대상입니다.

2. 4단계의 Deployment 트래픽 메트릭을 분석합니다. 30일 동안 요청 수가 0이거나 거의 0이면 Deployment가 방치되었거나 잘못 설정되었을 가능성이 높습니다. 트래픽이 있지만 최소이면 Deployment가 과다 프로비저닝되었을 수 있습니다.

3. 5단계의 PVC I/O 메트릭에서 생성 이후 작업이 없으면 스토리지가 가치 없이 소비되고 있습니다. I/O가 있지만 최소이면 정리보다 스토리지 티어 최적화를 고려합니다.

4. 6단계의 Service 접근 패턴을 검토합니다. Service가 엔드포인트 활동이 없으면 비활성 애플리케이션의 일부인지 설정 오류인지 확인합니다. Service는 접근되지만 뒤의 Pod가 유휴이면 스케일링 설정이 문제일 수 있습니다.

5. 8단계의 생성 타임스탬프를 비교합니다. 리소스가 최근 생성되었고 활동이 없으면 배포 단계일 수 있습니다. 리소스가 생성 이후 30일 이상 유휴이면 방치된 것일 가능성이 높습니다.

분석이 결론에 이르지 못하면: 10단계의 Job/CronJob 실행을 검토하여 실행 간에 유휴로 보일 수 있는 배치 워크로드를 식별합니다. 리소스 레이블에서 소유권 정보를 확인하여 담당 팀을 식별합니다. 9단계의 리소스 쿼터 사용률을 검토하여 상당한 쿼터 할당을 소비하는 유휴 리소스의 정리를 우선합니다.
