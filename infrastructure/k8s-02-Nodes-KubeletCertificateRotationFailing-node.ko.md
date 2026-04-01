---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/KubeletCertificateRotationFailing-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-node
- k8s-pod
- k8s-rbac
- kubeletcertificaterotationfailing
- kubernetes
- node
- nodes
- sts
---

---
title: Kubelet Certificate Rotation Failing — Kubelet 인증서 갱신 실패
weight: 257
categories:
  - kubernetes
  - node
---

# KubeletCertificateRotationFailing-node

## 의미

Kubelet 인증서 갱신이 실패하고 있습니다(KubeletDown 또는 인증서 관련 알림 발생). 인증서가 만료되었거나, 인증서 서명 요청을 승인할 수 없거나, 인증 기관을 사용할 수 없거나, RBAC 권한이 인증서 갱신을 방해하고 있습니다. Kubelet 로그에 인증서 갱신 오류나 만료 경고가 표시되고, CertificateSigningRequest 리소스가 승인 대기 상태이며, 인증 기관 상태가 비가용을 나타낼 수 있습니다.
 이는 데이터 플레인에 영향을 미치며, 만료된 인증서로 인해 Kubelet이 API 서버에 인증할 수 없어 Node 통신 장애가 발생합니다. 영향받는 Node에서 실행 중인 애플리케이션에 오류가 발생할 수 있습니다.

## 영향

Kubelet이 API 서버에 인증할 수 없고, Node가 NotReady 상태가 됩니다. Pod 상태를 보고할 수 없으며, 새로운 Pod를 스케줄링할 수 없습니다. KubeletDown 알림이 발생하고, KubeNodeNotReady 알림이 발생합니다. 인증서 만료 오류가 발생하고, TLS 핸드셰이크가 실패하며, Node가 Control Plane 연결을 잃습니다. Kubelet 로그에 인증서 갱신 오류나 만료 경고가 표시되고, CertificateSigningRequest 리소스가 무기한 승인 대기 상태로 남으며, Node가 NotReady 상태를 유지합니다. 영향받는 Node에서 실행 중인 애플리케이션에 오류가 발생하거나 접근이 불가능해질 수 있습니다.

## 플레이북

1. Node <node-name>을 describe하여 다음을 확인합니다:
   - Conditions 섹션에서 Ready 상태 및 인증서 관련 조건 확인
   - Events 섹션에서 인증서 만료 또는 갱신 실패 확인
   - System Info에서 Kubelet 버전 및 인증서 세부 정보 확인

2. Node <node-name>의 이벤트를 타임스탬프 순으로 조회하여 인증서 관련 문제의 순서를 확인합니다.

3. Node에서 Pod Exec 도구 또는 SSH(Node 접근 가능 시)를 사용하여 인증서 파일이나 Kubelet 로그를 검사하여 Kubelet 인증서 만료를 확인합니다.

4. Node에서 Kubelet 로그를 조회하고 인증서 갱신 오류, 만료 경고 또는 인증서 서명 요청 실패를 필터링합니다.

5. 클러스터의 CertificateSigningRequest 오브젝트를 조회하고 Kubelet 인증서 서명 요청이 승인 대기 중인지 확인합니다.

6. 인증 기관(CA) 상태를 확인하고 CA가 사용 가능하며 인증서에 서명할 수 있는지 검증합니다.

7. Kubelet이 인증서 서명 요청을 생성하고 승인할 수 있는 RBAC 권한을 확인합니다.

## 진단

1. 플레이북 1-2단계의 Node 이벤트를 분석하여 인증서 관련 문제를 파악합니다. "CertificateRotationFailed", "TLSHandshakeError" 또는 인증 실패를 보여주는 이벤트는 인증서 문제를 나타냅니다. 이벤트 타임스탬프를 기록하여 갱신 실패가 시작된 시점을 파악합니다.

2. Node 이벤트가 인증서 만료를 나타내는 경우, 플레이북 3단계에서 Kubelet 인증서 만료를 확인합니다. 인증서 만료 타임스탬프를 현재 시간 및 Kubelet 인증 실패 시작 시점과 비교합니다.

3. 플레이북 4단계의 Kubelet 로그에서 CSR(CertificateSigningRequest) 생성 또는 제출 오류가 나타나는 경우, 플레이북 5단계에서 대기 중인 CSR을 확인합니다. "Pending" 상태에 머무는 CSR은 승인 프로세스 문제를 나타냅니다.

4. CSR이 대기 중인 경우, 플레이북 6단계에서 인증 기관 상태를 확인합니다. CA 비가용 또는 과부하는 CSR 승인 및 인증서 발급을 방해합니다.

5. Kubelet 로그에서 CSR 생성 또는 승인 시 권한 거부 오류가 나타나는 경우, 플레이북 7단계에서 RBAC 권한을 확인합니다. 불충분한 권한은 Kubelet이 인증서 갱신을 요청하는 것을 방해합니다.

6. Kubelet 로그에서 CSR 제출을 위해 CA 또는 API 서버에 연결할 때 연결 오류가 나타나는 경우, Kubelet과 Control Plane 구성 요소 간의 네트워크 연결을 확인합니다.

7. 인증서 갱신이 이전에 정상 작동했다가 최근 실패한 경우, 갱신 프로세스에 영향을 줄 수 있는 클러스터 업그레이드, CA 인증서 갱신 또는 RBAC 정책 변경을 확인합니다.

**이벤트에서 근본 원인을 파악할 수 없는 경우**: Kubelet 구성에서 인증서 갱신 설정을 검토하고, 자동 갱신이 활성화되어 있는지 확인하며, CA 인증서 체인 유효성을 검증하고, 인증서 갱신이 조용히 실패하다가 인증서가 최종 만료되면서 비로소 가시적인 문제가 발생한 것은 아닌지 확인합니다.
