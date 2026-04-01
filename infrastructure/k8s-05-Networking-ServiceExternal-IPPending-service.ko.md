---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/ServiceExternal-IPPending-service.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- infrastructure
- ippending
- k8s-ingress
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- networking
- service
- serviceexternal
---

---
title: Service External-IP Pending - Service
weight: 241
categories:
  - kubernetes
  - service
---

# ServiceExternal-IPPending-service - Service External-IP Pending 상태

## 의미

LoadBalancer Service가 External-IP Pending 상태에 멈춰 있으며(Service 관련 알림 발생), 클라우드 프로바이더의 로드 밸런서 프로비저닝이 실패하거나, 클라우드 프로바이더 연동이 잘못 구성되었거나, 권한 부족으로 로드 밸런서 생성이 불가하거나, 클라우드 프로바이더 API가 사용 불가능한 것이 원인입니다.

## 영향

LoadBalancer Service에 외부 IP 없음, 외부 트래픽이 Service에 도달 불가, Service가 Pending 상태 유지, 로드 밸런서 프로비저닝 실패, KubeServiceNotReady 알림 발생 가능, Service 상태에 External-IP Pending 표시, 클러스터 외부에서 애플리케이션 접근 불가, 클라우드 프로바이더 연동 문제로 Service 노출 불가. Service에서 무기한 External-IP Pending 표시, Service 이벤트에 FailedToCreateLoadBalancer 오류 표시, Cloud Controller Manager Pod에서 장애 표시 가능, 클러스터 외부에서 애플리케이션 접근 불가능하며 오류 발생 가능.

## 플레이북

1. `<namespace>` Namespace에서 Service `<service-name>`을 상세 조회하여 상태, `status.loadBalancer.ingress`, 조건을 검사하고 External-IP Pending 상태를 확인합니다.

2. `<namespace>` Namespace에서 Service `<service-name>`의 이벤트를 타임스탬프 순으로 조회하여 로드 밸런서 프로비저닝 실패를 파악합니다.

3. 노드를 조회하고 클라우드 프로바이더 레이블과 어노테이션을 확인하여 클러스터가 클라우드 프로바이더와 올바르게 연동되어 있는지 확인합니다.

4. 노드 프로바이더 ID, Cloud Controller Manager Pod 상태 또는 클라우드 프로바이더 Service Account 권한을 확인하여 클라우드 프로바이더 연동을 검증합니다.

5. `kube-system` Namespace에서 Service Controller 또는 Cloud Controller Manager Pod의 로그를 조회하고 로드 밸런서 프로비저닝 오류를 필터링합니다.

6. 클라우드 프로바이더 계정 권한과 할당량을 확인하여 로드 밸런서 생성이 허용되고 할당량 제한이 초과되지 않았는지 확인합니다.

## 진단

1. 플레이북에서 Service 이벤트를 분석하여 로드 밸런서 프로비저닝 오류를 파악합니다. 이벤트에서 FailedToCreateLoadBalancer 또는 유사한 오류가 표시되면, 이벤트 메시지에 구체적인 프로비저닝 실패 사유가 나타납니다.

2. 이벤트에서 프로비저닝 실패가 표시되면, 플레이북에서 Cloud Controller Manager Pod 상태를 확인합니다. Cloud Controller Manager Pod가 실행되지 않거나, 크래시하거나, 오류를 보이면, 로드 밸런서 프로비저닝 요청이 처리되지 않습니다.

3. Cloud Controller Manager가 정상이면, 플레이북에서 Cloud Controller Manager 로그의 API 오류를 검토합니다. 로그에서 인증 실패, 권한 거부 또는 API 할당량 초과 오류가 표시되면, 클라우드 프로바이더 자격 증명 또는 권한이 부족합니다.

4. 자격 증명이 유효하면, 플레이북에서 Service 설정을 확인합니다. Service에 클라우드 프로바이더에 필요한 어노테이션(예: 로드 밸런서 유형, 서브넷 선택)이 없으면, 불완전한 설정으로 프로비저닝이 실패합니다.

5. 설정이 완전하면, 플레이북에서 노드 클라우드 프로바이더 레이블을 확인합니다. 노드에 필요한 프로바이더 ID 또는 클라우드 레이블이 없으면, Cloud Controller가 로드 밸런서를 프로비저닝할 위치를 결정할 수 없습니다.

6. 노드 레이블이 올바르면, 클라우드 프로바이더 할당량과 제한을 확인합니다. 로드 밸런서 할당량이 소진되었거나 계정 제한에 도달하면, 리소스가 해제될 때까지 새 로드 밸런서를 생성할 수 없습니다.

**프로비저닝 문제가 발견되지 않는 경우**: 클러스터에서 클라우드 프로바이더 API Endpoint에 접근 가능한지 확인하고, VPC 또는 서브넷 설정이 로드 밸런서 생성을 지원하는지 확인하고, 필요한 IAM 역할/Service Account에 로드 밸런서 관리 권한이 있는지 검토하고, 클라우드 프로바이더가 리전 장애 또는 서비스 저하를 겪고 있는지 검사합니다.
