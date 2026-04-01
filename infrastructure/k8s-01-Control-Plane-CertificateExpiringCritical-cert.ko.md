---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/CertificateExpiringCritical-cert.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- acm
- cert
- certificateexpiringcritical
- compliance
- control
- dns
- infrastructure
- k8s-secret
- k8s-service
- kubernetes
- plane
---

---
title: Certificate Expiring Critical - 인증서 만료 임박 (긴급)
weight: 45
categories: [kubernetes, cert-manager]
---

# CertificateExpiringCritical

## 의미

인증서가 만료에 매우 근접한 상태이며(CertificateExpiringCritical, CertManagerCertExpiryCritical 알림 트리거, 일반적으로 만료 7일 이내), 자동 갱신이 반복적으로 실패하여 즉각적인 조치가 필요합니다. 인증서가 곧 만료되어 서비스 중단이 발생하며, 모든 갱신 시도가 실패한 상태입니다. 이는 즉각적인 주의가 필요한 긴급 문제이며, 인증서 만료 시 HTTPS 서비스가 실패합니다. 고객 영향이 임박한 상태입니다.

## 영향

CertificateExpiringCritical 알림이 발생합니다. 서비스 중단이 임박하며, 수일 내에 HTTPS가 실패합니다. 긴급 조치가 필요합니다. 브라우저가 접근을 차단하고, API 연동이 중단되며, 모바일 앱이 실패합니다. 컴플라이언스 위반이 임박하고, 개입 없이는 고객 대면 서비스 중단이 거의 확실합니다. 비즈니스 영향이 심각합니다.

## 플레이북

1. 즉시 인증서 만료 날짜를 확인하고 만료까지 정확한 시간을 계산합니다.

2. Certificate 리소스 상태를 조회하고 조건에서 모든 실패 사유를 식별합니다.

3. 모든 CertificateRequest 리소스를 확인하여 상세한 실패 정보를 파악합니다.

4. Issuer 또는 ClusterIssuer가 새 인증서로 테스트하여 인증서를 발급할 수 있는지 검증합니다.

5. Certificate의 Secret을 삭제하여 재발급을 강제하는 방식으로 수동 인증서 갱신을 시도합니다.

6. ACME인 경우: 모든 챌린지 요구사항(DNS, HTTP 연결성)이 충족되는지 확인합니다.

7. 대비 계획 준비: 자동화를 시간 내에 수정할 수 없는 경우 CA에서 수동으로 인증서를 획득합니다.

## 진단

이것은 긴급 알림입니다 - 초기에는 근본 원인 분석보다 해결을 우선시합니다. 먼저 인증서를 갱신한 후, 자동 갱신이 실패한 이유를 조사합니다.

Issuer 자격 증명(ACME 계정, CA 자격 증명, Vault 토큰)이 만료되어 발급이 차단되었는지 확인합니다. Issuer 상태와 자격 증명 검증을 근거로 사용합니다.

ACME 챌린지를 위한 네트워크 연결이 방화벽 또는 인프라 변경으로 중단되지 않았는지 검증합니다. 연결 테스트와 최근 인프라 변경을 근거로 사용합니다.

이전 실패 시도로 인해 Let's Encrypt 속도 제한이 발급을 차단하고 있는지 확인합니다. ACME 서버 응답과 속도 제한 상태를 근거로 사용합니다.

도메인의 DNS 구성이 올바르고 해석 가능한지 검증합니다. DNS 쿼리와 전파 확인을 근거로 사용합니다.

자동 갱신을 수정할 수 없는 경우의 긴급 조치: certbot 또는 다른 ACME 클라이언트를 사용하여 Let's Encrypt에서 수동으로 인증서 획득, 유료 CA에서 수동으로 인증서 획득, 클라이언트 측 신뢰를 통한 자체 서명 인증서 임시 사용(공개 서비스에는 권장하지 않음).
