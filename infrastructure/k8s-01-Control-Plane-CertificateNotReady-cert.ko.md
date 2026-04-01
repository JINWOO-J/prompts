---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/CertificateNotReady-cert.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- acm
- cert
- certificatenotready
- compliance
- control
- dns
- infrastructure
- k8s-ingress
- k8s-namespace
- k8s-service
- kubernetes
- plane
- security
- sts
---

---
title: Certificate Not Ready - 인증서 준비 안 됨
weight: 40
categories: [kubernetes, cert-manager]
---

# CertificateNotReady

## 의미

Certificate 리소스가 Ready 상태가 아니며(CertificateNotReady, CertManagerCertNotReady 알림 트리거), cert-manager가 구성 문제, Issuer 문제 또는 ACME 챌린지 실패로 인해 TLS 인증서를 발급하거나 갱신할 수 없습니다. Certificate 리소스에서 Ready=False 조건이 표시되고, HTTPS 엔드포인트가 만료되거나 유효하지 않은 인증서를 사용하고 있을 수 있으며, 보안 연결이 실패합니다. 이 인증서에 의존하는 모든 서비스에 영향을 미칩니다. HTTPS 연결이 실패하고, TLS 핸드셰이크 오류가 발생하며, 사용자에게 인증서 경고가 표시되고, 서비스 간 mTLS가 중단됩니다.

## 영향

CertificateNotReady 알림이 발생합니다. HTTPS 엔드포인트가 유효하지 않거나 만료된 인증서를 사용합니다. 브라우저에 보안 경고가 표시되고, API 클라이언트가 연결을 거부하며, 모바일 앱이 연결에 실패합니다. Webhook 호출이 실패하고, mTLS 인증이 중단되며, Ingress가 HTTPS를 제공할 수 없습니다. 보안 통신이 손상되고 컴플라이언스 요구사항이 위반됩니다.

## 플레이북

1. `<namespace>` 네임스페이스에서 Certificate `<certificate-name>`을 조회하고 Ready 조건과 메시지를 확인합니다.

2. Certificate 리소스의 이벤트를 조회하여 특정 발급 실패를 식별합니다.

3. 연관된 CertificateRequest 리소스의 상세 상태와 실패 사유를 확인합니다.

4. 인증서가 참조하는 Issuer 또는 ClusterIssuer가 존재하고 Ready 상태인지 검증합니다.

5. ACME Issuer의 경우, Order 및 Challenge 리소스에서 도메인 검증 상태를 확인합니다.

6. HTTP-01 또는 DNS-01 챌린지를 위한 DNS가 올바르게 구성되어 있는지 검증합니다.

7. cert-manager Controller 로그에서 상세한 오류 메시지를 확인합니다.

## 진단

Certificate 상태 조건과 이벤트를 분석하여 실패 유형(Issuer 미발견, 챌린지 실패, 속도 제한, 잘못된 구성)을 분류합니다. 리소스 상태를 근거로 사용합니다.

ACME HTTP-01 챌린지의 경우, 챌린지 경로가 인터넷에서 접근 가능하고 Ingress가 챌린지 트래픽을 올바르게 라우팅하는지 검증합니다. 연결 테스트와 Ingress 구성을 근거로 사용합니다.

ACME DNS-01 챌린지의 경우, DNS 자격 증명이 올바르고 DNS 전파가 작동하는지 검증합니다. DNS 쿼리 결과와 자격 증명 구성을 근거로 사용합니다.

많은 인증서를 발급하는 경우 Let's Encrypt의 속도 제한을 확인합니다. ACME 서버 응답과 인증서 이력을 근거로 사용합니다.

인증서 사양이 Issuer 기능(허용된 도메인, 키 유형, 기간)과 일치하는지 검증합니다. Issuer 정책과 인증서 스펙을 근거로 사용합니다.

지정된 시간 범위 내에서 연관 관계를 찾을 수 없는 경우: DNS 레코드가 올바른 엔드포인트를 가리키는지 확인하고, 방화벽 규칙이 ACME 검증을 허용하는지 확인하며, Issuer 자격 증명을 갱신하고, Let's Encrypt 속도 제한을 확인하며, 테스트를 위해 Staging Issuer 사용을 고려합니다.
