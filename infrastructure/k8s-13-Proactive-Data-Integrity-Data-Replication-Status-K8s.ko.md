---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/06-Data-Integrity/Data-Replication-Status-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- data
- infrastructure
- integrity
- k8s-namespace
- k8s-pod
- k8s-pvc
- k8s-service
- replication
- status
- storage
---

# Data Replication Status — 데이터 복제 상태

## 의미

데이터 복제 상태는 클러스터 간 또는 네임스페이스 간 데이터 복제가 동기화되지 않거나 복제 작업이 실패했음을 나타냅니다(ReplicationLagHigh 또는 ReplicationFailed 같은 알림 발생). 복제 지연이 임계값을 초과하거나, 복제 작업이 실패하거나, 복제 상태에서 오류가 나타나거나, 복제 메트릭에서 실패가 감지되거나, 복제 상태 점검이 실패하는 것이 원인입니다. 복제 지연 메트릭이 임계값을 초과하고, 복제 작업이 실패 상태를 보이며, 복제 상태에서 오류가 나타나고, 복제 상태 점검에서 비정상 상태가 표시됩니다. 이는 스토리지 계층과 데이터 동기화 인프라에 영향을 미치며, 일반적으로 복제 서비스 문제, 네트워크 연결 문제, 복제 작업 실패, 또는 복제 구성 오류로 인해 발생합니다. 복제가 컨테이너 워크로드를 보호하는 경우, 컨테이너 데이터가 동기화되지 않고 애플리케이션에서 데이터 일관성 문제가 발생할 수 있습니다.

## 영향

ReplicationFailed 알림 발생, ReplicationLagHigh 알림 발생, 데이터 일관성 보장 불가, 클러스터 간 데이터 동기화 실패, 복제 작업 실패, 복제 지연이 허용 임계값 초과. 복제 작업이 실패 또는 대기 상태로 유지되며, 복제 지연 메트릭에서 증가하는 지연이 나타납니다. 복제가 컨테이너 워크로드를 보호하는 경우, 컨테이너 데이터가 동기화되지 않고, Persistent Volume 복제가 실패하며, 컨테이너 애플리케이션에서 데이터 일관성 문제가 발생할 수 있습니다. 애플리케이션에서 데이터 불일치 또는 복제 실패가 발생할 수 있습니다.

## 플레이북

1. 네임스페이스 <namespace>의 Persistent Volume Claim을 조회하여 모든 PVC와 복제 상태를 확인합니다.

2. 네임스페이스 <namespace>의 최근 이벤트를 타임스탬프 순으로 조회하여 최근 복제 실패나 지연 문제를 확인합니다.

3. 네임스페이스 <namespace>의 PVC <pvc-name>을 상세 조회하여 복제 상태, 지연 메트릭, 상태 점검 결과를 확인합니다.

4. 네임스페이스 <namespace>에서 app=replication 레이블의 복제 Pod 로그를 조회하고 'replication failed', 'replication lag high', 'replication error' 등의 오류 패턴을 필터링합니다.

5. 지난 1시간 동안의 복제 서비스에 대한 Prometheus 메트릭(replication_lag, replication_lag_seconds 포함)을 조회하여 복제 지연 패턴을 확인합니다.

6. 지난 24시간 동안의 복제 서비스에 대한 Prometheus 메트릭(replication_latency, replication_success_rate 포함)을 조회하여 복제 실패 패턴을 확인합니다.

7. 네임스페이스 <namespace>의 소스 PVC <source-pvc-name>을 상세 조회하여 소스 PVC 상태 및 복제 가용성을 확인합니다.

8. 소스 클러스터와 대상 클러스터에서 복제 관련 활성 Prometheus 알림(firing 상태)을 조회하여 클러스터 복제 상태 차이를 확인합니다.

## 진단

1. 3단계의 PVC 복제 상태를 검토합니다. 지연 메트릭이 높으면 지연이 일정한지(용량 또는 성능 문제 시사) 또는 급증하는지(간헐적 연결 문제 시사) 확인합니다.

2. 4단계의 복제 Pod 로그를 분석합니다. 로그에서 복제 실패 또는 오류 패턴이 나타나면 실패 원인(네트워크, 권한, 스토리지, 소스 가용성)을 확인합니다.

3. 5단계의 복제 지연 메트릭이 증가하고 있으면 복제가 뒤처지고 있는 것입니다. 6단계에서 성공률이 낮으면 복제 작업이 단순 지연이 아닌 실패하고 있는 것입니다.

4. 7단계의 소스 PVC 상태를 검토합니다. 소스 PVC에 문제가 있으면 복제 지연이 소스 비가용성으로 인한 것일 수 있습니다. 소스가 정상이면 복제 인프라가 문제입니다.

5. 8단계의 클러스터 알림에서 소스와 대상 간 차이가 나타나면 어느 클러스터에 복제에 영향을 미치는 문제가 있는지 확인합니다.

분석이 결론에 도달하지 못하는 경우: 2단계의 이벤트에서 복제 실패나 지연 문제를 확인합니다. 복제 문제가 모든 복제 볼륨에 영향을 미치는지(인프라 문제 시사) 또는 특정 볼륨에만 영향을 미치는지(볼륨별 구성 문제 시사) 판단합니다. 소스와 대상 클러스터 또는 네임스페이스 간 네트워크 연결을 확인합니다.
