---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/Timeout-control-plane.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- control
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- performance
- plane
- sts
- timeout
---

---
title: Timeout - API Server 타임아웃
weight: 237
categories:
  - kubernetes
  - control-plane
---

# Timeout-control-plane

## 의미

API Server가 요청을 타임아웃하고 있으며(KubeAPILatencyHigh 알림 트리거), API Server 또는 etcd와 같은 백엔드 서비스 또는 중요 네트워크 경로가 구성된 타임아웃 기간 내에 작업을 처리할 수 없습니다. API Server 지연이 임계값을 초과하여 context deadline exceeded 오류와 요청 타임아웃이 발생합니다.

## 영향

API 요청이 타임아웃됩니다. kubectl 명령이 멈추거나 실패하고, Controller에 지연이 발생하며, Deployment 및 업데이트가 지연됩니다. 클러스터 운영이 불안정해지고, etcd가 과부하될 수 있습니다. KubeAPILatencyHigh 알림이 발생하고, API Server 응답 시간이 증가합니다. TooManyRequests 스로틀링이 발생하며, Control Plane 컴포넌트가 응답하지 않게 됩니다.

## 플레이북

1. kube-system 네임스페이스에서 component=kube-apiserver 레이블을 가진 Pod를 describe하여 상태, 리소스 사용량 및 타임아웃 구성을 포함한 상세 API Server Pod 정보를 확인합니다.

2. kube-system 네임스페이스에서 마지막 타임스탬프 순으로 이벤트를 나열하여 최근 Control Plane 이벤트를 조회하고, 타임아웃 오류, 스로틀링(TooManyRequests) 또는 context deadline exceeded 메시지를 필터링합니다.

3. kube-system의 API Server Pod에서 로그를 조회하고 `context deadline exceeded` 또는 `request timeout`과 같은 타임아웃 관련 메시지를 필터링합니다.

4. 모든 노드를 나열하고 Control Plane 노드의 리소스 사용량 메트릭을 조회하여 타임아웃 기간 동안 CPU 또는 메모리 압박이 있는지 확인합니다.

5. 테스트 Pod에서 `telnet`, `nc` 또는 `curl`과 같은 도구를 사용하여 API Server 포트 6443에 대한 기본 TCP 연결성을 검증하여 네트워크 경로 문제를 배제합니다.

6. kube-system에서 etcd Pod를 조회하고 상태와 성능 메트릭(지연, 디스크 I/O, 리더 선출)을 검토하여 백엔드 느림을 감지합니다.

## 진단

1. 플레이북의 타임아웃 및 스로틀링 이벤트를 분석하여 타임아웃 오류의 패턴을 식별합니다. 이벤트에서 "context deadline exceeded", "TooManyRequests" 또는 스로틀링 메시지가 나타나면, 이벤트 타임스탬프를 사용하여 타임아웃 시작을 판단합니다.

2. 이벤트에서 API Server 리소스 압박이 나타나면, 플레이북 4단계의 API Server Pod 리소스 사용량을 검증합니다. 타임아웃 이벤트 타임스탬프에서 CPU 또는 메모리 사용량이 높았다면, 리소스 제약이 타임아웃을 유발하고 있습니다.

3. 이벤트에서 etcd 성능 문제가 나타나면, 플레이북 6단계의 etcd Pod 상태와 메트릭을 분석합니다. 타임아웃 이전 타임스탬프에서 etcd 이벤트가 지연 급증, 느린 요청 또는 리더 선출을 보이면, etcd가 근본 원인입니다.

4. 이벤트에서 스케일링 작업 또는 높은 Controller 활동이 나타나면, 부하를 생성한 작업을 식별합니다. 타임아웃 타임스탬프에서 이벤트가 대규모 스케일링 작업 또는 Controller 조정을 보이면, 부하 관련 요인이 타임아웃을 유발하고 있습니다.

5. 이벤트에서 API Server 재시작 또는 불안정성이 나타나면, 재시작 타임스탬프와 타임아웃 패턴을 연관시킵니다. 타임아웃 급증 직전 또는 시점에 API Server 재시작이 발생했다면, Pod 불안정성이 타임아웃 문제에 기여하고 있습니다.

6. 이벤트에서 네트워크 정책 또는 방화벽 변경이 나타나면, 변경 타임스탬프와 타임아웃 시작을 연관시킵니다. 타임아웃 시작 전에 네트워크 구성 수정이 발생했다면, 네트워크 변경이 지연 또는 연결 문제를 도입했을 수 있습니다.

7. 이벤트에서 스로틀링(TooManyRequests)이 나타나면, 높은 요청량을 생성하는 클라이언트 또는 Controller를 식별합니다. 스로틀링 이벤트에 특정 클라이언트가 나타나면, 대상 최적화로 문제를 해결할 수 있습니다.

**연관 관계를 찾을 수 없는 경우**: 검색 범위를 확장하고, 더 긴 기간에 걸친 etcd 성능 메트릭에서 점진적 저하를 검토하며, 누적 API 요청률 증가를 확인하고, Control Plane 노드 리소스 사용량 추세를 검토하며, 타임아웃 임계값이 최근 수정되었는지 확인합니다. API 타임아웃은 즉각적인 이벤트보다 점진적 리소스 고갈 또는 누적 부하로 인해 발생할 수 있습니다.
