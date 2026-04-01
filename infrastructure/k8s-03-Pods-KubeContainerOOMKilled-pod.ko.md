---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/KubeContainerOOMKilled-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- kubecontaineroomkilled
- kubernetes
- pods
- sts
---

---
title: Kube Container OOM Killed
weight: 25
categories: [kubernetes, pod]
---

# KubeContainerOOMKilled — Container OOM 종료

## 의미

Container가 OOM(Out of Memory) killer에 의해 종료되었습니다(KubeContainerOOMKilled 알림 발생). Container가 메모리 limit을 초과하여 Linux OOM killer가 프로세스를 종료했습니다. Container 상태에 OOMKilled 사유가 표시되고, 종료 코드 137은 OOM에 의한 SIGKILL을 나타내며,
 Pod가 메모리 관련 종료로 재시작됩니다. 이는 워크로드 플레인에 영향을 미치며, Container에 더 많은 메모리가 필요하거나 메모리 누수가 있음을 나타냅니다. 메모리 내 데이터가 손실되고, 서비스가 중단되며, 근본 문제가 지속되면 Container가 다시 종료될 수 있습니다.

## 영향

KubeContainerOOMKilled 알림 발생; Container가 즉시 종료됨; 메모리 내 데이터 손실; 재시작 중 서비스 다운타임 발생; 진행 중인 요청 실패; 커넥션 풀 초기화; 의존 서비스에서 연결 오류 발생; 재시작 백오프로 복구 지연 가능; 반복적인 OOMKill은 CrashLoopBackOff로 이어짐; 쓰기 작업 중 종료 시 데이터 손상 가능; 사용자가 서비스 불가용을 경험.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 조회하고 Container 종료 사유가 OOMKilled이며 종료 코드가 137인지 확인합니다.

2. OOMKill 이벤트 직전의 Container 메모리 메트릭(container_memory_working_set_bytes)을 조회하여 메모리 사용 패턴을 파악합니다.

3. Pod 사양에서 Container 메모리 limit을 조회하고 최대 메모리 사용량과 비교하여 limit이 부족한지 판단합니다.

4. --previous 플래그를 사용하여 OOMKill 전 애플리케이션 로그를 조회하고 'heap', 'OutOfMemory', 'allocation failed', 'GC overhead' 등 메모리 관련 패턴을 필터링합니다.

5. 지난 24시간 동안의 메모리 사용량 추이를 조회하고, 메모리가 지속적으로 증가하는지(누수) 또는 특정 작업 중 급증하는지(부하 기반) 판단합니다.

6. Java 애플리케이션의 경우 JVM 힙 크기가 Container 메모리 limit 대비 적절하게 구성되어 있는지 확인하고, 오프힙 메모리 요구사항을 고려합니다.

7. Vertical Pod Autoscaler(VPA) 권장 사항이 있는 경우 검토하여 제안된 메모리 limit 조정을 확인합니다.

## 진단

메모리 증가율을 요청 패턴과 비교하고, 메모리 사용량이 부하에 비례하는지(스케일링 필요) 또는 부하와 무관한지(메모리 누수) 확인합니다. 요청 메트릭과 메모리 추이를 근거로 판단합니다.

OOMKill 전 메모리 사용 패턴을 분석하고, 점진적 증가(누수)인지 급격한 급증(특정 작업)인지 확인합니다. 고해상도 메모리 메트릭을 근거로 판단합니다.

OOMKill 타임스탬프를 특정 애플리케이션 작업(배치 작업, 대용량 쿼리, 파일 처리)과 상관 분석하고, 특정 작업이 메모리 급증을 트리거하는지 확인합니다. 애플리케이션 로그와 작업 타임스탬프를 근거로 판단합니다.

애플리케이션이 힙 메트릭에서 추적되지 않지만 Container limit에 포함되는 오프힙 메모리(네이티브 메모리, 메모리 매핑 파일, NIO 버퍼)를 사용하는지 확인합니다. 네이티브 메모리 추적과 프로세스 RSS를 근거로 판단합니다.

메모리 limit이 request보다 현저히 낮은지(비정상적 구성) 또는 request가 limit과 같은지(메모리에 민감한 워크로드에 적합한 Guaranteed QoS) 확인합니다. Pod QoS 클래스와 리소스 사양을 근거로 판단합니다.

지정된 시간 범위 내에서 상관관계를 찾지 못한 경우: 즉각적인 완화 조치로 메모리 limit 증가, 분석을 위한 OOM 시 힙 덤프 활성화, 애플리케이션 메모리 사용량 프로파일링, 객체 유지 및 캐싱 정책 검토, 메모리 집약적 작업을 별도 Pod로 분리하는 것을 고려합니다.
