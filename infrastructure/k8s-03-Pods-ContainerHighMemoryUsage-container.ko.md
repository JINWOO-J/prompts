---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/ContainerHighMemoryUsage-container.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- container
- containerhighmemoryusage
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- k8s-statefulset
- kubernetes
- pods
- sts
---

---
title: Container High Memory Usage
weight: 21
categories: [kubernetes, container]
---

# ContainerHighMemoryUsage — Container 메모리 사용량 과다

## 의미

Container가 높은 메모리 사용량을 보이고 있습니다(ContainerHighMemoryUsage 또는 ContainerMemoryNearLimit 알림 발생). Container가 limit에 근접하거나 limit만큼의 메모리를 소비하고 있어 OOMKill 위험이 있습니다. Container 메트릭에서 메모리 사용량이 limit의 80-90%를 지속적으로 초과하고, 메모리 working set이 시간이 지남에 따라 증가하며, OOM killer에 의해 종료될 위험이 있습니다. 이는 워크로드 플레인에 영향을 미치며, 메모리 누수, 부족한 메모리 limit, 또는 메모리 집약적 워크로드를 나타냅니다. 애플리케이션이 예기치 않게 크래시될 수 있고, 프로세스가 종료되면 데이터 손실이 발생할 수 있으며, 서비스 가용성이 저하됩니다.

## 영향

ContainerHighMemoryUsage 알림 발생; OOMKill 위험에 처한 Container; 애플리케이션이 예기치 않게 크래시될 수 있음; 메모리 내 데이터 손실 가능; Pod 재시작 증가; 서비스 가용성 저하; 가비지 컬렉션으로 인한 응답 시간 증가 가능; 메모리 집약적 작업 실패; 커넥션 풀 고갈 가능; 파일 디스크립터 누수 가능; Swap 사용량 증가(활성화된 경우); 노드 메모리 압박으로 다른 Pod에 영향 가능.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 조회하고 Container 메모리 limit과 request를 확인하여 현재 리소스 할당량을 파악합니다.

2. Container `<container-name>`의 메모리 메트릭(container_memory_working_set_bytes, container_memory_usage_bytes)을 조회하고 메모리 limit과 비교합니다.

3. 지난 24시간 동안의 메모리 사용량 추이를 조회하고, 메모리가 꾸준히 증가하는지(누수 의심), 부하에 따라 변동하는지(정상 동작) 판단합니다.

4. Container `<container-name>`의 애플리케이션 메트릭 또는 로그를 조회하고 'OutOfMemory', 'heap', 'GC', 'memory pressure' 등 메모리 관련 패턴을 필터링하여 애플리케이션 수준의 메모리 문제를 파악합니다.

5. Namespace `<namespace>`에서 Deployment 또는 StatefulSet `<workload-name>`을 조회하고 request와 limit을 포함한 메모리 리소스 사양을 검토합니다.

6. `kubectl describe pod` 또는 Events API를 사용하여 Pod 이력에서 OOMKilled 이벤트를 확인하고, Container가 이전에 메모리 부족으로 종료된 적이 있는지 확인합니다.

7. 해당되는 경우, JVM 힙 메트릭(jvm_memory_used_bytes, jvm_gc_collection_seconds) 또는 언어별 메모리 메트릭을 조회하여 힙 vs 오프힙 메모리 문제를 파악합니다.

## 진단

메모리 사용량 증가율을 가동 시간과 비교하고, 메모리가 시간에 따라 선형적으로 증가하는지(메모리 누수 의심) 또는 워밍업 후 안정화되는지 확인합니다. 메모리 메트릭과 Pod 재시작 타임스탬프를 근거로 판단합니다.

메모리 급증을 요청 비율이나 특정 작업과 상관 분석하고, 메모리 사용량이 부하에 의존적인지 확인합니다. 요청 메트릭과 메모리 타임라인을 근거로 판단합니다.

가비지 컬렉션 메트릭(해당되는 경우)을 분석하고, GC가 자주 실행되지만 메모리를 회수하지 못하는지(유지된 참조 의심) 확인합니다. GC 메트릭과 힙 사용량을 근거로 판단합니다.

동일 Deployment의 Replica 간 메모리 사용량을 비교하고, 모든 Pod가 유사한 패턴을 보이는지 또는 특정 인스턴스만 메모리 누수가 있는지 확인합니다. Pod별 메트릭을 근거로 판단합니다.

Pod 재시작 후 메모리 사용량이 감소했다가 점진적으로 다시 증가하는지 확인하여 메모리 누수 패턴을 확인합니다. 과거 메모리 메트릭과 재시작 이벤트를 근거로 판단합니다.

지정된 시간 범위 내에서 상관관계를 찾지 못한 경우: 객체 유지에 대한 애플리케이션 코드 검토, 제거 정책 없는 캐싱 확인, 데이터베이스 커넥션 풀이 제한되어 있는지 확인, 파일 핸들 및 소켓 누수 점검, 메모리 누수 조사를 위한 힙 덤프 분석을 고려합니다.
