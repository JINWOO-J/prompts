---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/APIServerHighLatency-control-plane.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- apiserverhighlatency
- control
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- kubernetes
- performance
- plane
- storage
- sts
---

---
title: API Server High Latency - API Server 높은 지연 시간 - Control Plane
weight: 263
categories:
  - kubernetes
  - control-plane
---

# APIServerHighLatency-control-plane

## 의미

Kubernetes API Server가 높은 지연 시간을 경험하고 있으며(KubeAPILatencyHigh 알림 트리거), 이는 과도한 부하, 리소스 제약, 네트워크 문제 또는 스토리지 백엔드 성능 문제로 인해 발생합니다. API Server 메트릭에서 요청 지연 시간이 1초를 초과하고, 요청 큐 깊이 메트릭이 요청 적체를 나타내며, etcd 성능 메트릭에서 지연 문제가 관찰될 수 있습니다. 이는 Control Plane에 영향을 미치며, 클러스터 운영을 지연시키는 API Server 성능 저하를 나타냅니다. 일반적으로 과도한 부하, 리소스 제약, etcd 성능 문제 또는 Admission Webhook 타임아웃이 원인이며, Kubernetes API를 사용하는 애플리케이션에서 오류가 발생할 수 있습니다.

## 영향

API 요청 완료에 1초 이상 소요됩니다. kubectl 명령에 지연이 발생하고, Controller 조정이 느려지며, Deployment 및 업데이트가 지연됩니다. 클러스터 운영이 느려지고 타임아웃이 발생할 수 있습니다. KubeAPILatencyHigh 알림이 발생하며, API Server 메트릭에서 높은 요청 지연 시간이 관찰됩니다. 클러스터 응답성이 저하되고, etcd 성능 메트릭에서 지연 문제가 나타날 수 있으며, Kubernetes API를 사용하는 애플리케이션에서 오류 또는 성능 저하가 발생할 수 있습니다.

## 플레이북

1. kube-system 네임스페이스에서 component=kube-apiserver 레이블을 가진 API Server Pod를 describe하여 상태, 재시작 횟수, 리소스 사용량 및 경고 조건을 포함한 상세 정보를 확인합니다.

2. kube-system 네임스페이스에서 타임스탬프 순으로 이벤트를 조회하여 API Server 오류, 스로틀링 이벤트 또는 성능 관련 문제를 필터링합니다.

3. API Server Pod 메트릭과 로그를 조회하여 높은 지연 패턴을 식별합니다. 요청 지속 시간(apiserver_request_duration_seconds), 큐 깊이(apiserver_request_queue_depth), 오류율에 집중합니다.

4. kube-system 네임스페이스에서 etcd 엔드포인트를 조회하여 etcd 리더 상태를 확인하고, etcd 리더 선출 문제가 발생하고 있는지 검증합니다.

5. API Server가 스토리지 백엔드로 etcd에 의존하므로, etcd 성능 메트릭과 상태를 확인합니다. etcd_request_duration_seconds 및 etcd_leader_changes 메트릭에 집중하여 etcd 지연이 API Server 지연에 기여하는지 검증합니다.

6. API Server Admission Webhook 지연을 확인합니다. Admission Webhook 메트릭(apiserver_admission_webhook_admission_duration_seconds)을 검토하여 Webhook 타임아웃이 지연을 유발하는지 검증합니다.

7. API Server Pod 리소스 사용량(CPU 및 메모리)을 확인하여 리소스 제약이 성능 저하를 유발하는지 검증합니다.

8. API Server 감사 로그 또는 메트릭을 검토하여 높은 부하를 유발하는 요청 유형, 클라이언트 또는 작업 패턴을 확인합니다.

## 진단

1. 플레이북의 API Server Pod 이벤트를 분석하여 API Server가 재시작 중인지, 리소스 제약 상태인지, 오류가 발생하는지 식별합니다. 이벤트에서 Pod 재시작 또는 CrashLoopBackOff가 나타나면, 재시작 타임스탬프와 지연 급증을 연관시켜 불안정성이 근본 원인인지 확인합니다.

2. 이벤트에서 리소스 압박(OOMKilled, CPU 스로틀링)이 나타나면, API Server Pod 리소스 사용량을 설정된 제한과 비교합니다. 이벤트의 지연 급증 타임스탬프에서 CPU 또는 메모리 사용량이 제한에 근접하면, 리소스 제약이 원인일 가능성이 높습니다.

3. 이벤트에서 etcd 연결 문제 또는 타임아웃 오류가 나타나면, etcd Pod 이벤트와 상태를 분석합니다. API Server 지연 이벤트 이전 타임스탬프에서 etcd 이벤트가 리더 선출, 느린 요청 또는 비가용성을 보이면, etcd가 근본 원인입니다.

4. 이벤트에서 Admission Webhook 타임아웃 또는 실패가 나타나면, Admission Webhook 메트릭과 로그를 검토합니다. 이벤트 타임스탬프에서 Webhook 응답 시간이 임계값을 초과하면, Webhook 지연이 API Server 지연에 기여하고 있습니다.

5. 이벤트가 결론적이지 않으면, 이벤트 타임스탬프에서 API Server 요청 큐 깊이 메트릭을 분석합니다. 큐 깊이 증가가 지연 급증에 선행하면, 높은 부하로 인한 요청 적체가 원인일 가능성이 높습니다.

6. Pod 수준 문제가 발견되지 않으면, 클러스터 수준 이벤트에서 스케일링 작업, 대규모 리소스 생성 또는 Controller 조정 폭주를 확인합니다. 지연 문제 이전 타임스탬프에서 클러스터 이벤트가 대량 작업을 보이면, 부하 관련 요인이 원인입니다.

7. 이벤트에서 네트워크 또는 인프라 변경이 나타나면, 이벤트의 인프라 변경 타임스탬프와 지연 시작을 연관시킵니다. 지연 시작 1시간 이내에 변경이 발생했다면, 인프라 수정이 근본 원인일 수 있습니다.

**연관 관계를 찾을 수 없는 경우**: API Server 로그에서 점진적 성능 저하 패턴을 검토하고, 여러 Controller 또는 클라이언트로 인한 누적 리소스 압박을 확인하며, etcd 스토리지 증가 또는 컴팩션 문제를 검토하고, 네트워크 경로 문제가 점진적으로 누적되었는지 확인하며, 인증 또는 권한 부여 처리 지연을 점검합니다. API Server 지연은 즉각적인 변경보다 점진적인 시스템 저하로 인해 발생할 수 있습니다.
