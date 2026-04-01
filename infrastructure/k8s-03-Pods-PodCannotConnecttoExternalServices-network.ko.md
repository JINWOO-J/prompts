---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/PodCannotConnecttoExternalServices-network.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- database
- dns
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- network
- podcannotconnecttoexternalservices
- pods
- sts
---

---
title: Pod Cannot Connect to External Services - Network
weight: 234
categories:
  - kubernetes
  - network
---

# PodCannotConnecttoExternalServices-network — 외부 서비스 연결 불가

## 의미

Pod가 외부 서비스에 연결할 수 없습니다(외부 연결 실패로 Pod가 응답하지 않을 때 KubePodNotReady 알림 발생). NetworkPolicy가 이그레스 트래픽을 차단하거나, 클러스터의 이그레스 게이트웨이가 잘못 구성되었거나,
 DNS가 외부 도메인을 해석할 수 없거나, 방화벽 규칙이 아웃바운드 연결을 차단합니다. Pod 로그에 연결 타임아웃 또는 거부 오류가 표시되고, NetworkPolicy 리소스에 이그레스 차단 규칙이 표시될 수 있으며, 외부 도메인에 대한 DNS 해석 테스트가 실패할 수 있습니다. 이는 네트워크 플레인에 영향을 미치며, NetworkPolicy 제한 또는 DNS 문제로 인해 Pod가 외부 서비스에 도달하지 못합니다.

## 영향

Pod가 외부 API 또는 서비스에 도달 불가; 아웃바운드 인터넷 연결 실패; 외부 서비스 통합 중단; 이그레스 트래픽 차단; NetworkPolicy가 외부 접근을 방해; 외부 연결 실패로 Pod가 응답하지 않을 때 KubePodNotReady 알림 발생; 애플리케이션이 외부 리소스를 가져올 수 없음; 외부 데이터베이스 또는 API 연결 실패; Pod 로그에 연결 타임아웃 또는 거부 오류 표시; 애플리케이션이 시작되지 않거나 올바르게 작동하지 않음.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 describe하여 네트워크 구성과 DNS 설정을 포함한 상세 정보를 조회합니다.

2. Namespace `<namespace>`에서 Pod `<pod-name>`의 이벤트를 타임스탬프 순으로 조회하여 네트워크 관련 문제와 이그레스 차단 이벤트를 파악합니다.

3. Namespace `<namespace>`의 NetworkPolicy 객체를 나열하고 이그레스 규칙을 검토하여 정책이 외부 트래픽을 차단하는지 확인합니다.

4. Pod `<pod-name>`에서 외부 서비스 URL로 curl 또는 wget을 실행하여 아웃바운드 연결을 테스트하고 외부 연결이 차단되는지 확인합니다.

5. Pod `<pod-name>`에서 외부 도메인에 대해 nslookup 또는 dig를 실행하여 외부 서비스에 대한 DNS 해석을 테스트합니다.

6. 클러스터 이그레스 게이트웨이 또는 네트워크 플러그인 구성을 확인하여 이그레스 트래픽 라우팅이 올바르게 구성되어 있는지 확인합니다.

## 진단

1. 플레이북의 Pod 이벤트를 분석하여 네트워크 관련 오류 또는 이그레스 차단 이벤트를 파악합니다. 이벤트에서 외부 서비스로의 연결 타임아웃 또는 거부 오류가 표시되면, 실패하는 구체적인 외부 엔드포인트를 기록합니다.

2. 이벤트에서 연결 실패가 확인되면, 플레이북의 DNS 해석 테스트 결과를 확인합니다. 외부 도메인에 대한 nslookup 또는 dig가 실패하면, 네트워크 연결이 아닌 DNS 해석 문제입니다.

3. DNS 해석이 작동하면, 플레이북 데이터에서 NetworkPolicy 이그레스 규칙을 확인합니다. 외부 트래픽을 허용하는 규칙(0.0.0.0/0 또는 특정 외부 CIDR) 없이 이그레스 정책이 존재하면, 정책에 의해 이그레스 트래픽이 차단됩니다.

4. NetworkPolicy가 이그레스를 허용하면, 플레이북의 연결 테스트 결과(curl/wget)를 검토합니다. 연결이 거부가 아닌 타임아웃되면, 아웃바운드 트래픽을 차단하는 방화벽 규칙 또는 보안 그룹을 확인합니다.

5. 방화벽 규칙이 차단하지 않으면, 플레이북에서 Pod 네트워크 구성과 DNS 설정을 확인합니다. dnsPolicy가 잘못되었거나 네임서버 구성이 누락되면, DNS 기반 외부 서비스 해석이 실패합니다.

6. Pod 네트워크 구성이 올바르면, 플레이북 데이터에서 네트워크 플러그인과 이그레스 게이트웨이 상태를 확인합니다. 이그레스 라우팅이 잘못 구성되었거나 NAT가 작동하지 않으면, Pod가 외부 네트워크에 도달할 수 없습니다.

**이그레스 구성 문제를 찾지 못한 경우**: 외부 서비스 가용성을 독립적으로 확인, 외부 접근에 프록시 또는 이그레스 게이트웨이가 필요한지 확인, 클라우드 제공자 NAT 게이트웨이 또는 인터넷 게이트웨이 구성 검토, 특정 외부 IP 또는 도메인이 조직 방화벽 정책에 의해 차단되는지 점검합니다.
