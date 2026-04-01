---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/04-Cost-Optimization/Unused-Resource-Cleanup-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- cleanup
- cost
- infrastructure
- k8s-configmap
- k8s-namespace
- k8s-pod
- k8s-pvc
- k8s-secret
- k8s-service
- kubernetes
- optimization
- resource
- sts
- unused
---

# Unused Resource Cleanup (미사용 리소스 정리)

## 의미

미사용 리소스 정리 알림은 Kubernetes 리소스가 더 이상 필요하지 않지만 프로비저닝된 상태로 유지되어 가치 없이 비용을 소비하는 상황(UnusedResourceDetected 또는 OrphanedResourceDetected 같은 알림 발생)을 나타냅니다. Pod가 중지되었지만 삭제되지 않음, PVC가 미연결, Service가 미접근, ConfigMap과 Secret이 미사용, 또는 리소스가 장기간 활동 없음 등이 원인입니다.
 리소스가 활동 메트릭 없음을 보이고, 리소스가 중지 또는 분리 상태이며, 리소스가 활성 워크로드와 연결되지 않고, 리소스 생성 타임스탬프가 방치를 나타냅니다. 이는 비용 관리 계층과 리소스 수명주기 관리에 영향을 미치며, 주로 리소스 수명주기 관리 실패, 방치된 리소스 감지 공백, 또는 리소스 정리 자동화 문제가 원인입니다. 미사용 리소스가 컨테이너 워크로드인 경우, 컨테이너 리소스가 고아 상태가 되고 애플리케이션이 불필요한 비용 오버헤드를 겪을 수 있습니다.

## 영향

UnusedResourceDetected 알림 발생, OrphanedResourceDetected 알림 발생, 불필요한 비용 누적, 리소스가 가치 없이 비용 소비, 리소스 수명주기 관리 실패, 방치된 리소스 미정리. 리소스가 활동 없음 또는 미사용 상태를 보입니다. 미사용 리소스가 컨테이너 워크로드인 경우, 컨테이너 리소스가 고아 상태가 되고, Pod 리소스가 방치되며, 컨테이너 애플리케이션이 불필요한 비용 오버헤드를 겪을 수 있습니다. 애플리케이션이 비용 비효율이나 리소스 낭비를 경험할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 상태가 Succeeded 또는 Failed인 Pod를 wide 출력으로 조회하여 정리가 필요할 수 있는 완료 또는 실패 Pod를 식별합니다.
2. namespace <namespace>에서 최근 이벤트를 타임스탬프 순으로 조회하여 리소스 수명주기 문제, 고아 리소스, 정리 관련 경고를 확인합니다.
3. namespace <namespace>에서 PVC를 조회하여 정리 대상이 될 수 있는 미연결 또는 해제된 PVC를 식별합니다.
4. namespace <namespace>에서 Service를 조회하고 서비스 엔드포인트 접근 패턴을 확인하여 접근이 없는 Service를 식별합니다.
5. namespace <namespace>에서 ConfigMap과 Secret을 조회하고 Pod의 사용 여부를 확인하여 미사용 ConfigMap과 Secret을 식별합니다.
6. 리소스 모니터링 Pod의 로그를 조회하고 최근 90일 동안 리소스 비활동이나 방치를 나타내는 패턴을 필터링합니다.
7. 리소스 생성 타임스탬프와 마지막 활동 타임스탬프를 비교하여 리소스가 생성 이후 비활성 상태인지 확인하고, 리소스 활동 로그를 보조 증거로 활용합니다.
8. namespace <namespace>에서 상태가 'Complete' 또는 'Failed'인 Job과 CronJob을 조회하고 완료된 Job이 정리되는지 확인하여 Job 수명주기 관리를 점검합니다.
9. namespace <namespace>에서 레플리카가 0인 Deployment와 StatefulSet을 조회하고 0 레플리카 워크로드가 여전히 필요한지 확인하여 워크로드 수명주기 관리를 점검합니다.

## 진단

1. 1단계의 완료/실패 Pod를 검토합니다. Pod가 장기간 Succeeded 또는 Failed 상태이면 정리 대상입니다. 완료된 Job에 대한 정리 자동화가 존재하는지 확인합니다.

2. 3단계의 PVC 상태를 분석합니다. PVC가 Released 또는 Unbound 상태이면 Pod에 연결되지 않아 정리 대상일 수 있습니다. 삭제 전에 관련 데이터가 여전히 필요한지 확인합니다.

3. 4단계의 Service 접근 분석에서 90일 동안 엔드포인트 활동이 없는 Service가 있으면 고아 Service일 가능성이 높습니다. 5단계의 ConfigMap/Secret 분석에서 어떤 Pod에서도 참조되지 않는 리소스가 있으면 정리 대상입니다.

4. 8단계의 Job/CronJob 상태를 검토합니다. 완료된 Job이 자동으로 정리되지 않으면 Job TTL이나 정리 자동화가 잘못 설정된 것입니다. 9단계에서 0 레플리카 Deployment가 있으면 의도적으로 축소된 것인지 방치된 것인지 확인합니다.

5. 7단계에서 리소스가 생성 이후 90일 이상 비활성이면 방치된 리소스 정리의 강력한 대상입니다. 리소스 레이블을 확인하여 확인을 위한 소유권을 식별합니다.

분석이 결론에 이르지 못하면: 2단계의 이벤트에서 리소스 수명주기 문제를 확인합니다. 6단계의 리소스 활동 로그를 검토하여 한때 활성이었다가 비활성이 된 리소스(애플리케이션 변경 시사)와 한 번도 사용되지 않은 리소스(배포 오류 시사)를 식별합니다. 리소스 소유권을 식별하기 위한 리소스 레이블링 표준이 존재하는지 확인합니다.
