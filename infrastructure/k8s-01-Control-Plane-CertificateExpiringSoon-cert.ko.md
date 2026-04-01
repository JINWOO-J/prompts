---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/CertificateExpiringSoon-cert.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- acm
- cert
- certificateexpiringsoon
- compliance
- control
- dns
- infrastructure
- k8s-ingress
- k8s-namespace
- k8s-secret
- k8s-service
- kubernetes
- plane
- sts
---

---
title: Certificate Expiring Soon - 인증서 만료 예정
weight: 41
categories: [kubernetes, cert-manager]
---

# CertificateExpiringSoon

## 의미

인증서가 만료에 근접하고 있으며(CertificateExpiringSoon, CertManagerCertExpirySoon 알림 트리거, 일반적으로 만료 30일 이내), 자동 갱신이 이루어지지 않아 인증서가 곧 만료될 예정입니다. Certificate 리소스에서 다가오는 만료 날짜가 표시되고, 갱신이 조용히 실패하고 있을 수 있으며, 인증서 만료 시 서비스가 실패합니다. 이 인증서를 사용하는 모든 서비스에 영향을 미치며, 서비스 중단을 방지하기 위해 사전 갱신이 필요합니다. 만료 후 HTTPS가 실패합니다.

## 영향

CertificateExpiringSoon 알림이 발생합니다. 임박한 서비스 중단 경고이며, 해결되지 않으면 만료 시 HTTPS가 실패합니다. 브라우저가 접근을 차단하고, API 연결이 실패하며, 모바일 앱이 인증서를 거부합니다. mTLS가 중단되고, Ingress가 유효하지 않은 인증서를 제공하며, 컴플라이언스 위반이 발생합니다. 고객 대면 서비스에 영향을 미칩니다.

## 플레이북

1. `<namespace>` 네임스페이스에서 Certificate `<certificate-name>`을 조회하여 만료 날짜와 갱신 상태를 확인합니다.

2. renewBefore 설정을 확인하고 cert-manager가 갱신을 시도했어야 하는 시점을 계산합니다.

3. CertificateRequest 리소스를 조회하여 갱신 요청이 생성되고 있는지와 그 상태를 확인합니다.

4. Issuer 또는 ClusterIssuer가 여전히 작동하고 새 인증서를 발급할 수 있는지 검증합니다.

5. cert-manager Controller 로그에서 갱신 시도 실패를 확인합니다.

6. Let's Encrypt를 사용하는 경우 DNS 및 Ingress 구성이 여전히 ACME 챌린지를 허용하는지 검증합니다.

7. 자동 갱신이 중단된 경우 Certificate의 Secret을 삭제하여 수동으로 갱신을 트리거합니다.

## 진단

현재 시간과 renewBefore 임계값을 비교하여 cert-manager가 이미 갱신했어야 하는지 검증합니다. 인증서 스펙과 현재 타임스탬프를 근거로 사용합니다.

갱신이 시도되었지만 실패했음을 나타내는 실패한 CertificateRequest 리소스를 확인합니다. CertificateRequest 상태와 이벤트를 근거로 사용합니다.

Issuer 구성이 변경되지 않았고 자격 증명이 여전히 유효한지(API 키, 서비스 계정 권한) 검증합니다. Issuer 상태와 자격 증명 유효성을 근거로 사용합니다.

ACME 검증을 차단할 수 있는 네트워크 변경(방화벽 규칙, Ingress 변경, DNS 변경)을 확인합니다. 연결 테스트와 구성 이력을 근거로 사용합니다.

cert-manager Controller 로그에서 갱신 프로세스 중 오류를 분석합니다. 로그 분석과 오류 패턴을 근거로 사용합니다.

지정된 시간 범위 내에서 연관 관계를 찾을 수 없는 경우: Secret을 수동으로 삭제하여 재발급을 트리거하고, 테스트 인증서로 Issuer가 작동하는지 검증하며, cert-manager Webhook 문제를 확인하고, 임시 수정으로 수동 인증서 발급을 고려하며, Issuer가 영구적으로 손상된 경우 에스컬레이션합니다.
