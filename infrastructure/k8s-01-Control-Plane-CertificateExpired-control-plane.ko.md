---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/CertificateExpired-control-plane.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- certificateexpired
- control
- infrastructure
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-secret
- k8s-service
- kubernetes
- plane
- sts
---

---
title: Certificate Expired - 인증서 만료 - Control Plane
weight: 249
categories:
  - kubernetes
  - control-plane
---

# CertificateExpired-control-plane

## 의미

하나 이상의 클러스터 X.509 인증서(API Server, kubelet 또는 etcd용)가 유효 기간을 초과하여 핵심 Kubernetes 컴포넌트 간의 TLS 핸드셰이크 및 인증된 요청이 실패하기 시작합니다. 인증서 만료는 x509 인증서 오류, 인증 실패 및 컴포넌트 통신 장애를 유발합니다.

## 영향

모든 API 작업이 실패합니다. 클러스터가 완전히 비기능 상태가 되며, 노드가 Control Plane과 통신할 수 없고, kubectl 명령이 실패합니다. Controller가 조정을 중단하고 클러스터가 사실상 다운됩니다. 로그에 인증서 만료 오류가 나타나고, TLS 핸드셰이크 실패가 발생하며, KubeAPIDown 또는 KubeletDown 알림이 발생할 수 있습니다. 인증 오류로 인해 클러스터 운영이 차단됩니다.

## 플레이북

1. kube-system 네임스페이스에서 component=kube-apiserver 레이블을 가진 API Server Pod를 나열하여 인증서 관련 실패를 겪고 있는 Pod를 확인합니다.

2. kube-system 네임스페이스에서 타임스탬프 순으로 이벤트를 조회하여 인증서 오류 또는 TLS 핸드셰이크 실패를 필터링합니다.

3. Control Plane 노드에서 모든 Control Plane, kubelet 및 etcd 인증서의 만료 날짜를 확인합니다.

4. kube-system의 API Server Pod에서 로그를 조회하고(또는 서비스로 실행 중인 경우 시스템 로그), x509: certificate has expired 또는 TLS 핸드셰이크 실패와 같은 인증서 오류를 필터링합니다.

5. 모든 노드를 나열하고 Ready 상태와 조건을 검사하여 인증서 오류 발생 시점에 Control Plane과의 연결이 끊긴 노드를 식별합니다.

6. 인증서 갱신 자동화(cert-manager 또는 external-secrets Operator 등)의 상태를 확인하여 해당 Pod가 오류 없이 실행 중인지 검증합니다.

7. 인증서 검사 출력과 저장된 CA 파일을 사용하여 클러스터 CA 인증서가 여전히 유효하고 만료 날짜에 도달하거나 초과하지 않았는지 확인합니다.

## 진단

1. 플레이북의 인증서 관련 이벤트를 분석하여 어떤 인증서가 만료되었고 만료가 언제 발생했는지 식별합니다. 이벤트에서 x509 인증서 오류 또는 TLS 핸드셰이크 실패가 나타나면, 이벤트 타임스탬프를 사용하여 인증 실패가 시작된 시점을 정확히 파악합니다.

2. 이벤트에서 인증서 만료가 나타나면, 플레이북 3단계의 인증서 만료 날짜를 검증합니다. `kubeadm certs check-expiration`의 인증서 만료 타임스탬프가 인증 오류 이벤트 타임스탬프와 일치하면, 인증서 만료가 근본 원인으로 확인됩니다.

3. 이벤트에서 Control Plane 컴포넌트 재시작 또는 실패가 나타나면, 이벤트의 컴포넌트 재시작 타임스탬프와 인증서 만료 시간을 연관시킵니다. 인증서 만료 직후 또는 만료 시점에 재시작이 시작되었다면, 만료된 인증서가 컴포넌트 실패를 유발한 것입니다.

4. 이벤트에서 CSR 승인 실패 또는 kubelet 통신 문제가 나타나면, 인증서 만료 타임스탬프 전후로 CSR 관련 이벤트가 실패하기 시작했는지 확인합니다. CSR 이벤트가 거부 또는 보류 상태를 보이면, 인증서 갱신 프로세스가 실패한 것입니다.

5. 이벤트에서 최근 클러스터 업그레이드 활동이 나타나면, 인증서 오류 24시간 이내에 업그레이드 관련 이벤트가 발생했는지 확인합니다. 업그레이드 이벤트가 발견되면, 업그레이드 프로세스가 인증서를 제대로 갱신하지 못했을 수 있습니다.

6. 이벤트가 결론적이지 않으면, kube-system 네임스페이스의 구성 변경 이벤트를 검토합니다. 만료 오류 전에 인증서 관련 ConfigMap 또는 Deployment 변경이 발생했다면, 구성 문제가 인증서 갱신을 방해했을 수 있습니다.

**연관 관계를 찾을 수 없는 경우**: 검색 범위를 확장하고, 기록되지 않은 변경에 대해 인프라 로그와 변경 관리 시스템을 확인하며, 과거 인증서 갱신 패턴을 검토하고, 관련 컴포넌트(etcd, kubelet)에서 지연된 오류 발현을 검토합니다. 인증서 관련 문제는 초기 만료 후 수 시간 뒤에 나타나는 연쇄 효과를 가질 수 있습니다.
