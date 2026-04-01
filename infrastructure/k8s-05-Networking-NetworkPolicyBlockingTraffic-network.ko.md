---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/NetworkPolicyBlockingTraffic-network.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- infrastructure
- k8s-ingress
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- network
- networking
- networkpolicyblockingtraffic
- performance
---

---
title: Network Policy Blocking Traffic - Network
weight: 295
categories:
  - kubernetes
  - network
---

# NetworkPolicyBlockingTraffic-network - NetworkPolicy 트래픽 차단

## 의미

NetworkPolicy 리소스가 의도치 않게 트래픽을 차단하고 있으며(KubePodNotReady 또는 KubeServiceNotReady 알림 발생), 정책 규칙이 너무 제한적이거나, Ingress 또는 Egress 규칙이 필요한 트래픽을 허용하지 않거나, 정책 Pod 셀렉터가 의도한 Pod와 일치하지 않거나, 기본 거부 정책이 정당한 트래픽을 차단하고 있는 것이 원인입니다.

## 영향

정당한 트래픽 차단, Pod 간 필요한 통신 불가, 네트워크 제한으로 인한 애플리케이션 장애, Service 간 통신 차단, Ingress 또는 Egress 트래픽 거부, Pod가 통신할 수 없어 Unready 상태가 되면 KubePodNotReady 알림 발생, NetworkPolicy 차단으로 Service가 트래픽을 라우팅할 수 없으면 KubeServiceNotReady 알림 발생, NetworkPolicy가 필요한 연결을 방해, 애플리케이션이 의존성에 접근 불가, Pod 간 통신 실패, Service Endpoint 접근 불가. Pod에서 무기한 연결 실패 표시, NetworkPolicy 리소스에 제한적 규칙 표시, 애플리케이션이 의존성에 접근할 수 없어 오류 또는 성능 저하 발생 가능, Service 간 통신 차단.

## 플레이북

1. `<namespace>` Namespace에서 NetworkPolicy `<policy-name>`을 상세 조회하여 Ingress 및 Egress 규칙, Pod 셀렉터, Namespace 셀렉터를 포함한 상세 정보를 확인합니다.

2. `<namespace>` Namespace에서 이벤트를 타임스탬프 순으로 조회하고 NetworkPolicyDenied 사유를 필터링하여 네트워크 관련 문제와 정책 차단 이벤트를 파악합니다.

3. `<namespace>` Namespace에서 NetworkPolicy 리소스를 조회하고 규칙, 셀렉터, 정책 유형을 검토하여 어떤 정책이 트래픽을 차단하는지 파악합니다.

4. `<namespace>` Namespace에서 Pod `<pod-name>`을 상세 조회하고 레이블을 확인하여 레이블이 NetworkPolicy 셀렉터와 일치하는지 확인합니다.

5. 테스트 Pod에서 Pod Exec 도구를 사용하여 연결 테스트를 실행하고, 어떤 트래픽이 차단되고 어떤 정책이 차단을 적용하는지 확인합니다.

6. `<namespace>` Namespace에서 NetworkPolicy 리소스를 조회하고, 명시적으로 허용하지 않는 한 모든 트래픽을 차단할 수 있는 기본 거부 정책(빈 규칙과 함께 Ingress 또는 Egress를 포함하는 policyTypes)을 확인합니다.

## 진단

1. 플레이북에서 NetworkPolicy 이벤트와 Pod 이벤트를 분석하여 NetworkPolicyDenied 오류 또는 연결 실패를 파악합니다. 이벤트에서 명시적 정책 거부 메시지가 표시되면, 차단 정책이 이벤트 세부 정보에서 확인됩니다.

2. 이벤트에서 정책 차단이 표시되면, 플레이북 데이터에서 NetworkPolicy Pod 셀렉터와 Pod 레이블을 비교합니다. Pod 레이블이 정책 셀렉터와 일치하지 않으면, Pod는 명시적 허용 규칙 없이 기본 거부 동작의 대상이 됩니다.

3. Pod 레이블이 정책 셀렉터와 일치하면, 플레이북에서 NetworkPolicy의 Ingress 및 Egress 규칙을 검토합니다. 규칙에 필요한 포트, 프로토콜 또는 소스/대상 셀렉터가 포함되지 않으면, 과도하게 제한적인 규칙에 의해 트래픽이 차단됩니다.

4. Ingress/Egress 규칙이 올바르게 보이면, 플레이북 데이터에서 기본 거부 정책(Ingress 또는 Egress policyTypes가 있지만 빈 규칙)을 확인합니다. 해당 허용 정책 없이 기본 거부가 존재하면 모든 트래픽이 차단됩니다.

5. 기본 거부가 차단하지 않으면, 플레이북에서 NetworkPolicy 규칙의 Namespace 셀렉터를 확인합니다. Namespace 셀렉터가 소스/대상 Namespace 레이블과 일치하지 않으면 크로스 Namespace 트래픽이 차단됩니다.

6. NetworkPolicy 설정이 올바르게 보이면, 플레이북 데이터에서 kube-system의 네트워크 플러그인 Pod 상태를 확인합니다. 네트워크 플러그인 Pod에서 장애 또는 재시작이 표시되면, 정책 적용이 일관되지 않거나 지연될 수 있습니다.

**정책 설정 오류가 발견되지 않는 경우**: 정책 동기화 문제에 대해 네트워크 플러그인 로그를 검토하고, 여러 겹치는 정책이 의도치 않은 제한을 생성하는지 확인하고, Namespace 셀렉터에 영향을 미치는 Namespace 레이블 변경이 있었는지 확인하고, 네트워크 플러그인 버전 또는 설정 변경이 정책 적용 동작에 영향을 미쳤는지 검사합니다.
