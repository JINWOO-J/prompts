---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/ContainerMemoryNearLimit-container.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- container
- containermemorynearlimit
- infrastructure
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- pods
---

---
title: Container Memory Near Limit
weight: 23
categories: [kubernetes, container]
---

# ContainerMemoryNearLimit — Container 메모리 Limit 임박

## 의미

Container 메모리 사용량이 limit에 근접하고 있습니다(ContainerMemoryNearLimit 알림 발생, 일반적으로 사용량이 limit의 80-90%를 초과할 때 트리거). Container가 할당된 메모리의 대부분을 소비하고 있어 사용량이 더 증가하면 OOMKill될 위험이 있습니다. Container 메트릭에서 메모리 working set이 설정된 limit에 근접하고, OOM killer가 곧 트리거될 수 있으며, Container가 위험 구간에서 운영되고 있습니다. 이는 워크로드 플레인에 영향을 미치며, Container 종료의 임박한 위험을 나타냅니다. 애플리케이션이 예기치 않게 크래시될 수 있으며, 서비스 중단을 방지하기 위한 사전 조치가 필요합니다.

## 영향

ContainerMemoryNearLimit 알림 발생; OOMKill의 임박한 위험에 처한 Container; 메모리 급증 시 즉시 종료됨; 애플리케이션 안정성 저하; 가비지 컬렉션이 공격적으로 동작; 응답 시간 증가 가능; 메모리 할당 실패 가능; 애플리케이션에서 Out-of-Memory 예외 발생 가능; 서비스 저하 가능성 높음; 트랜잭션 중 Container가 종료되면 데이터 손실 위험; 워크로드가 지속적으로 더 많은 메모리를 필요로 하면 재시작 루프 시작 가능.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 조회하고 Container 메모리 limit과 현재 사용률을 확인합니다.

2. 메모리 여유 공간을 계산합니다: (limit - working_set) / limit * 100으로 Container가 OOMKill 임계값에 얼마나 가까운지 판단합니다.

3. 지난 6시간 동안의 메모리 사용량 추이를 조회하고, 메모리가 증가하는지(누수), 안정적인지(정상), 급증하는지(부하 기반) 판단합니다.

4. Container `<container-name>`의 애플리케이션 로그를 조회하고 'heap', 'memory', 'GC overhead', 'allocation failed' 등 메모리 경고 패턴을 필터링합니다.

5. `kubectl describe pod`를 사용하여 OOMKilled 이력을 확인하고, Container가 이전에 종료된 적이 있는지 확인합니다.

6. 노드 메모리 메트릭을 조회하여 limit을 증가시킬 경우 노드에 가용 메모리가 있는지 확인합니다.

7. 메모리 request가 limit과 같은지(Guaranteed QoS) 또는 request가 더 낮은지(Burstable QoS) 평가하여 축출 우선순위에 미치는 영향을 확인합니다.

## 진단

현재 메모리 사용량을 과거 기준선과 비교하고, 현재 사용량이 이상 현상인지 또는 새로운 정상 운영 수준인지 확인합니다. 과거 메트릭과 배포 변경 사항을 근거로 판단합니다.

메모리 증가를 24시간 이내의 최근 배포 또는 구성 변경과 상관 분석하고, 코드 변경이 메모리 회귀를 유발했는지 확인합니다. 배포 타임스탬프와 메모리 추이를 근거로 판단합니다.

메모리 사용량이 부하에 비례하는지(예상됨) 또는 부하와 무관한지(잠재적 누수) 분석합니다. 요청 비율 메트릭과 메모리 상관관계를 근거로 판단합니다.

Container가 외부 캐시(Redis, Memcached)로 오프로드할 수 있는 데이터를 캐싱하고 있어 메모리 압박을 줄일 수 있는지 확인합니다. 애플리케이션 아키텍처와 캐싱 패턴을 근거로 판단합니다.

메모리 limit이 최근 감소되었는지 또는 부적절한 초기 사이징의 새 워크로드인지 확인합니다. 리소스 이력과 워크로드 특성을 근거로 판단합니다.

지정된 시간 범위 내에서 상관관계를 찾지 못한 경우: 즉각적인 완화 조치로 메모리 limit 증가, 메모리 프로파일링 분석 예약, 메모리 최적화 기회에 대한 애플리케이션 검토, 메모리 부하 분산을 위한 수평 확장 고려, 자동 스케일링을 위한 메모리 기반 HPA 구현을 검토합니다.
