---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/KubeAPITerminatedRequests-control-plane.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- control
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- kubeapiterminatedrequests
- kubernetes
- performance
- plane
- scaling
- sts
---

---
title: Kube API Terminated Requests - API 요청 종료
weight: 20
---

# KubeAPITerminatedRequests

## 의미

API Server가 수신 요청의 20% 이상을 종료하고 있으며(KubeAPITerminatedRequests 알림 트리거), API Server Flow Control이 속도 제한, Priority and Fairness 제약 또는 용량 제한으로 인해 요청을 거부하고 있습니다. API Server Flow Control 메트릭에서 높은 종료율이 나타나고, FlowSchema 리소스에서 스로틀링 구성이 표시되며, API Server 로그에 Flow Control 거부 오류가 나타납니다. 이는 Control Plane에 영향을 미치며, API Server 용량이 초과되거나 Flow Control 구성이 너무 제한적임을 나타냅니다. 일반적으로 과도한 클라이언트 요청률, 잘못 구성된 Flow Schema 또는 불충분한 API Server 리소스가 원인이며, Kubernetes API를 사용하는 애플리케이션에서 오류가 발생할 수 있습니다.

## 영향

KubeAPITerminatedRequests 알림이 발생합니다. 클라이언트가 클러스터와 안정적으로 상호작용할 수 없으며, 클러스터 내 서비스가 저하되거나 사용 불가가 될 수 있습니다. API 요청이 종료되고, Flow Control이 요청을 거부합니다. API 작업이 간헐적으로 실패하고, Controller가 조정에 실패할 수 있습니다. Kubernetes API를 사용하는 애플리케이션에서 실패가 발생하고, 클러스터 운영이 스로틀링되며, 사용자 대면 서비스가 응답하지 않을 수 있습니다. 워크로드 스케일링 작업이 차단될 수 있습니다.

## 플레이북

1. kube-system 네임스페이스에서 component=kube-apiserver 레이블을 가진 Pod를 describe하여 상태, 리소스 사용량 및 Flow Control 구성을 포함한 상세 API Server Pod 정보를 확인합니다.

2. kube-system 네임스페이스에서 마지막 타임스탬프 순으로 이벤트를 나열하여 최근 Control Plane 이벤트를 조회하고, Flow Control 거부, 속도 제한 또는 종료된 요청 오류를 필터링합니다.

3. API Server Flow Control 메트릭을 조회하고 어떤 Flow Schema가 트래픽을 스로틀링하는지 식별하여 어떤 요청 유형이 종료되고 있는지 판단합니다.

4. FlowSchema 리소스를 조회하고 Flow Schema 구성과 우선순위 수준을 검사하여 요청 우선순위를 이해하고 잘못된 구성을 식별합니다.

5. API Server 메트릭에서 요청률, 종료된 요청률 및 Flow Control 거부를 조회하여 종료율을 정량화하고 패턴을 식별합니다.

6. API Server 구성을 조회하고 Priority and Fairness 설정을 포함한 API Server Flow Control 구성을 검증하여 제한적인 구성을 식별합니다.

7. 클라이언트 API 요청률 메트릭을 조회하고 Flow Control을 트리거할 수 있는 과도한 API 요청을 하는 클라이언트 또는 Controller를 식별합니다.

## 진단

1. 플레이북의 Flow Control 및 속도 제한 이벤트를 분석하여 요청 종료가 시작된 시점과 활성화된 Flow Schema를 식별합니다. 이벤트에서 Flow Control 거부 또는 스로틀링이 나타나면, 이벤트 타임스탬프를 사용하여 종료 시작을 판단합니다.

2. 이벤트에서 특정 Flow Schema 활성화가 나타나면, 플레이북 4단계의 FlowSchema 구성을 검토합니다. 이벤트에서 특정 우선순위 수준이 스로틀링되고 있으면, 어떤 요청 유형 또는 클라이언트가 영향을 받는지 식별하고 Flow Schema 구성이 적절한지 판단합니다.

3. 이벤트에서 높은 클라이언트 요청률이 나타나면, 플레이북 7단계에서 과도한 API 요청을 생성하는 클라이언트 또는 Controller를 식별합니다. 종료 타임스탬프에서 특정 클라이언트가 높은 요청량을 보이면, 클라이언트 동작이 Flow Control을 트리거하고 있습니다.

4. 이벤트에서 API Server 리소스 압박이 나타나면, 이벤트 타임스탬프에서 Pod 리소스 사용량을 검증합니다. 종료가 증가할 때 CPU 또는 메모리 사용량이 급증했다면, 리소스 제약이 Flow Control 활성화를 강제한 것입니다.

5. 이벤트에서 특정 요청 유형(읽기 vs 쓰기 동사)에 대한 종료가 나타나면, 어떤 작업이 종료되고 있는지 분석합니다. Flow Schema에서 쓰기 작업이 읽기보다 우선시되면, 우선순위 구성을 적절히 조정합니다.

6. 이벤트에서 일관된 종료(간헐적이 아닌)가 나타나면, API Server 용량 구성을 분석합니다. 종료가 버스트가 아닌 안정적이면, API Server 용량이 기본 부하에 불충분할 수 있습니다.

7. 이벤트에서 간헐적 종료가 나타나면, 이벤트 타임스탬프에서 버스트 트래픽 패턴을 식별합니다. 종료가 특정 시간대 또는 작업과 상관관계가 있으면, 대상 트래픽 관리로 문제를 해결할 수 있습니다.

**연관 관계를 찾을 수 없는 경우**: 트래픽 분석을 위해 시간 범위를 1시간으로 확장하고, API Server Flow Control 구성을 검토하며, 과도한 요청을 유발하는 클라이언트 잘못된 구성을 확인하고, API Server 용량 설정을 검증하며, 과거 Flow Control 패턴을 검토합니다. API 종료된 요청은 즉각적인 변경보다 API Server 용량 제한, 잘못 구성된 Flow Control 또는 클라이언트 요청 패턴으로 인해 발생할 수 있습니다.
