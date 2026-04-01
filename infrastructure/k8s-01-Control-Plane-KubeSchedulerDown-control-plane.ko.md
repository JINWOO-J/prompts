---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/KubeSchedulerDown-control-plane.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- control
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- kubeschedulerdown
- monitoring
- performance
- plane
---

---
title: Kube Scheduler Down - Scheduler 다운
weight: 20
---

# KubeSchedulerDown

## 의미

Kube Scheduler가 Prometheus 타겟 디스커버리에서 사라졌거나 접근할 수 없으며(KubeSchedulerDown 알림 트리거), Scheduler 프로세스가 실패하거나, 네트워크 연결이 끊기거나, 모니터링할 수 없습니다. Scheduler Pod가 kubectl에서 CrashLoopBackOff 또는 Failed 상태를 보이고, 로그에 치명적 오류, panic 메시지 또는 연결 타임아웃 오류가 나타나며, Pod가 스케줄링을 기다리며 Pending 상태로 남아 있습니다. 이는 Control Plane에 영향을 미치며, Scheduler가 Pod를 노드에 할당하는 것을 방해하여 새 Pod가 Pending 상태로 남게 됩니다. 일반적으로 Pod 실패, API Server 연결 문제, 인증서 문제 또는 리소스 제약이 원인이며, 애플리케이션이 새 Pod를 시작할 수 없습니다.

## 영향

KubeSchedulerDown 알림이 발생합니다. 클러스터가 부분적으로 또는 완전히 비기능 상태일 수 있습니다. 새 Pod를 스케줄링할 수 없고, Pod가 Pending 상태로 남습니다. Scheduler가 Pod를 노드에 할당할 수 없으며, Deployment 및 기타 워크로드를 스케일링할 수 없습니다. 클러스터 스케줄링 운영이 차단되고, Prometheus가 Scheduler 타겟을 발견할 수 없습니다. Pod 스케줄링 운영이 완전히 차단됩니다.

## 플레이북

1. kube-system 네임스페이스에서 component=kube-scheduler 레이블을 가진 Pod를 describe하여 상태, 재시작 횟수, 컨테이너 상태 및 오류 조건을 포함한 상세 Scheduler Pod 정보를 확인합니다.

2. kube-system 네임스페이스에서 마지막 타임스탬프 순으로 이벤트를 나열하여 최근 Control Plane 이벤트를 조회하고, Scheduler 실패, CrashLoopBackOff 또는 연결 오류를 필터링합니다.

3. kube-system 네임스페이스의 Pod `<pod-name>`에서 로그를 조회하고 'panic', 'fatal', 'connection refused', 'etcd', 'timeout', 'certificate'를 포함한 오류 패턴을 필터링하여 시작 또는 런타임 실패를 식별합니다.

4. 모니터링 시스템과 Scheduler 엔드포인트 간의 네트워크 연결성을 검증하여 연결 문제가 모니터링을 방해하는지 확인합니다.

5. kube-system 네임스페이스의 Pod `<pod-name>`을 조회하고 Scheduler 리소스 사용량을 확인하여 리소스 제약이 작동에 영향을 미치는지 검증합니다.

6. Scheduler가 API Server에 의존하므로, Scheduler 관점에서 API Server 엔드포인트 접근성을 확인하여 API Server 연결성을 검증합니다.

## 진단

1. 플레이북의 Scheduler Pod 이벤트를 분석하여 실패 모드를 식별합니다. 이벤트에서 CrashLoopBackOff, Failed 또는 Pod 종료가 나타나면, 이벤트 타임스탬프와 오류 메시지를 사용하여 실패 시작 시점과 근본 원인 범주를 판단합니다.

2. 이벤트에서 Scheduler 크래시 또는 panic이 나타나면, 플레이북 3단계의 로그를 검토합니다. 이벤트 타임스탬프에서 로그가 panic 메시지, 치명적 오류 또는 시작 실패를 보이면, 애플리케이션 수준 문제 또는 구성 문제가 크래시를 유발한 것입니다.

3. 이벤트에서 API Server 연결 실패가 나타나면, 플레이북 6단계의 API Server 상태를 검증합니다. Scheduler 실패 이전 타임스탬프에서 API Server 이벤트가 비가용성 또는 연결 오류를 보이면, API Server가 근본 원인입니다.

4. 이벤트에서 인증서 오류 또는 인증 실패가 나타나면, 인증서 만료와 유효성을 검증합니다. 이벤트 타임스탬프에서 인증서 관련 오류가 나타나면, 만료되거나 유효하지 않은 인증서가 Scheduler 실패를 유발한 것입니다.

5. 이벤트에서 리소스 압박(OOMKilled, CPU 스로틀링)이 나타나면, 이벤트 타임스탬프에서 Pod 리소스 사용량을 검증합니다. 실패 시작 시 리소스 사용량이 제한을 초과했다면, 리소스 제약이 실패를 유발한 것입니다.

6. 이벤트에서 Control Plane 노드 문제가 나타나면, 노드 조건 전환을 분석합니다. Scheduler 실패 이전 타임스탬프에서 노드 이벤트가 NotReady, MemoryPressure 또는 DiskPressure를 보이면, 노드 수준 문제가 근본 원인입니다.

7. 이벤트에서 모니터링 연결 문제(Prometheus가 타겟을 발견할 수 없음)가 나타나면, 플레이북 4단계의 모니터링 시스템과 Scheduler 엔드포인트 간의 네트워크 연결성을 검증합니다. 실패 타임스탬프에서 네트워크 문제가 있으면, 모니터링 특정 연결 문제가 존재할 수 있습니다.

**연관 관계를 찾을 수 없는 경우**: 인프라 변경에 대해 시간 범위를 1시간으로 확장하고, Scheduler 구성을 검토하며, API Server 연결 문제를 확인하고, Control Plane 노드 상태를 검증하며, 과거 Scheduler 안정성 패턴을 검토합니다. Scheduler 실패는 즉각적인 구성 변경보다 Control Plane 노드 문제, API Server 문제 또는 리소스 제약으로 인해 발생할 수 있습니다.
