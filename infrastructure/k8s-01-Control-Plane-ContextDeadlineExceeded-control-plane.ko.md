---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/ContextDeadlineExceeded-control-plane.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- contextdeadlineexceeded
- control
- infrastructure
- k8s-deployment
- k8s-helm
- k8s-namespace
- k8s-pod
- kubernetes
- performance
- plane
- sts
---

---
title: Context Deadline Exceeded - 컨텍스트 데드라인 초과 - Control Plane
weight: 246
categories:
  - kubernetes
  - control-plane
---

# ContextDeadlineExceeded-control-plane

## 의미

Kubernetes API 요청이 컨텍스트 데드라인에 도달하고 있으며, 이는 현재 부하, 경합 또는 네트워크 조건에서 API Server 또는 다운스트림 의존성이 응답하기에 너무 느리기 때문입니다(KubeAPILatencyHigh 또는 KubeAPIErrorsHigh 알림 트리거 가능). 이는 API Server 성능 저하, etcd 지연 또는 과도한 API 요청률이 Control Plane을 압도하고 있음을 나타냅니다.

## 영향

API 요청이 타임아웃됩니다. kubectl 명령이 멈추거나 실패하고, Controller 조정에 지연이 발생하며, Deployment 및 업데이트가 지연됩니다. 클러스터 운영이 불안정해지고, KubeAPILatencyHigh 알림이 발생합니다. KubeAPIErrorsHigh 알림이 발생할 수 있으며, 로그에 context deadline exceeded 오류가 나타납니다. API 요청 타임아웃이 발생하고, etcd 성능 저하가 관찰될 수 있습니다.

## 플레이북

1. kube-system 네임스페이스에서 component=kube-apiserver 레이블을 가진 API Server Pod를 describe하여 상태, 리소스 사용량 및 타임아웃 구성을 포함한 상세 정보를 확인합니다.

2. kube-system 네임스페이스에서 타임스탬프 순으로 이벤트를 조회하여 타임아웃 오류, "too many requests" 오류 또는 context deadline exceeded 메시지를 필터링합니다.

3. kube-system 네임스페이스의 API Server Pod에서 로그를 조회하고 "context deadline exceeded" 또는 "request timeout"을 포함한 타임아웃 오류를 필터링합니다.

4. 클러스터 내 Pod에서 API Server 엔드포인트에 대한 네트워크 연결성을 검증합니다.

5. kube-system 네임스페이스에서 etcd Pod 정보를 조회하고 etcd 성능 메트릭과 리소스 사용량을 확인합니다.

## 진단

1. 플레이북의 타임아웃 및 스로틀링 이벤트를 분석하여 context deadline exceeded 오류의 패턴을 식별합니다. 이벤트에서 "too many requests" 또는 스로틀링 메시지가 나타나면, 높은 API 요청량이 원인일 가능성이 높습니다.

2. 이벤트에서 API Server 리소스 압박이 나타나면, 이벤트 타임스탬프에서 API Server Pod 리소스 사용량을 검증합니다. 타임아웃 이벤트 발생 시 CPU 또는 메모리 사용량이 제한에 근접하면, 리소스 제약이 타임아웃을 유발하고 있습니다.

3. 이벤트에서 etcd 연결 문제 또는 느린 응답이 나타나면, etcd Pod 이벤트와 상태를 분석합니다. 타임아웃 이벤트 이전 타임스탬프에서 etcd 이벤트가 지연 급증 또는 리더 선출 문제를 보이면, etcd 성능이 근본 원인입니다.

4. 이벤트에서 Controller 또는 Operator 스케일링 활동이 나타나면, 스케일링 이벤트 타임스탬프와 타임아웃 시작을 연관시킵니다. 스케일링 작업 직후 타임아웃이 시작되었다면, 증가된 Controller 조정 부하가 API Server를 압도하고 있습니다.

5. 이벤트에서 대규모 목록 작업 또는 Watch 폭주가 나타나면, 높은 요청량을 생성하는 클라이언트 또는 Controller를 식별합니다. 타임아웃 타임스탬프에서 특정 리소스 또는 네임스페이스에 높은 활동이 나타나면, 대상 최적화로 문제를 해결할 수 있습니다.

6. 이벤트에서 kube-system 네임스페이스의 구성 변경이 나타나면, 변경 타임스탬프와 타임아웃 시작을 연관시킵니다. 타임아웃 시작 전에 구성 수정이 발생했다면, 최근 변경이 문제를 도입했을 수 있습니다.

7. 이벤트에서 네트워크 문제 또는 연결 실패가 나타나면, 이벤트 타임스탬프에서 네트워크 경로 상태를 검증합니다. 타임아웃과 동시에 네트워크 이벤트가 실패 또는 지연을 보이면, 네트워크 문제가 기여 요인입니다.

**연관 관계를 찾을 수 없는 경우**: API Server 로그에서 이전 경고 징후를 검토하고, etcd 성능 메트릭에서 점진적 저하를 확인하며, API 요청 패턴에서 누적 부하 증가를 검토하고, API Server 리소스 제한이 너무 제한적인지 확인하며, 네트워크 지연 문제를 점검합니다. 타임아웃 문제는 점진적 성능 저하 또는 누적 부하로 인해 발생할 수 있습니다.
