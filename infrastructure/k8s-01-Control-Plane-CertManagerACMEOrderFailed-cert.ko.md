---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/CertManagerACMEOrderFailed-cert.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- acm
- cert
- certmanageracmeorderfailed
- control
- dns
- infrastructure
- k8s-deployment
- k8s-ingress
- kubernetes
- plane
- security
- sts
---

---
title: Cert Manager ACME Order Failed - ACME 주문 실패
weight: 43
categories: [kubernetes, cert-manager]
---

# CertManagerACMEOrderFailed

## 의미

ACME 인증서 주문이 실패했으며(CertManagerACMEOrderFailed 알림 트리거), ACME 챌린지(HTTP-01 또는 DNS-01)를 성공적으로 완료할 수 없습니다. Order 리소스가 Failed 상태를 보이고, 도메인 검증이 통과하지 못했으며, 인증서를 발급할 수 없습니다. Let's Encrypt와 같은 ACME Issuer를 사용하는 인증서에 영향을 미칩니다. 새 인증서 발급이 실패하고, 갱신이 실패하며, HTTPS를 사용할 수 없을 수 있습니다.

## 영향

CertManagerACMEOrderFailed 알림이 발생합니다. 인증서를 발급할 수 없으며, HTTPS 엔드포인트에 유효한 인증서가 없습니다. TLS가 필요한 새 Deployment가 차단되고, 인증서 갱신이 실패합니다. 브라우저에 보안 오류가 표시되고, API 클라이언트가 연결을 거부하며, Ingress가 HTTPS 트래픽을 안전하게 제공할 수 없습니다.

## 플레이북

1. 실패한 Certificate와 연관된 Order 리소스를 조회하고 상태와 실패 사유를 확인합니다.

2. Order 하위의 Challenge 리소스를 조회하고 어떤 도메인이 검증에 실패했는지 식별합니다.

3. HTTP-01 챌린지의 경우: http://domain/.well-known/acme-challenge/<token>에서 챌린지 경로가 인터넷에서 접근 가능한지 검증합니다.

4. DNS-01 챌린지의 경우: _acme-challenge TXT 레코드가 존재하고 올바른 값을 가지고 있는지 검증합니다.

5. Ingress 구성을 확인하여 챌린지 경로가 차단되거나 리다이렉트되지 않는지 확인합니다.

6. 방화벽 및 네트워크 정책이 검증을 위한 수신 HTTP(S)를 허용하는지 검증합니다.

7. cert-manager 로그에서 ACME 서버 응답의 구체적인 오류 세부 정보를 확인합니다.

## 진단

HTTP-01 챌린지의 경우, 외부 인터넷 위치에서 챌린지 URL이 예상 토큰 값을 반환하는지 검증합니다. curl 또는 HTTP 테스트 도구를 근거로 사용합니다.

Ingress Controller에 ACME 챌린지를 방해하는 구성(강제 HTTPS 리다이렉트, 인증 요구사항)이 있는지 확인합니다. Ingress 어노테이션과 라우팅 규칙을 근거로 사용합니다.

DNS-01 챌린지의 경우, DNS 전파가 완료되었고 TXT 레코드가 여러 위치에서 해석 가능한지 검증합니다. DNS 쿼리 도구와 전파 확인기를 근거로 사용합니다.

오류 메시지에서 속도 제한 또는 너무 많은 요청을 언급하는 Let's Encrypt 속도 제한을 확인합니다. 로그의 ACME 서버 응답을 근거로 사용합니다.

도메인 소유권과 DNS 구성이 올바른 Ingress를 가리키는지 검증합니다. DNS 레코드와 도메인 등록을 근거로 사용합니다.

지정된 시간 범위 내에서 연관 관계를 찾을 수 없는 경우: 속도 제한을 피하기 위해 ACME Staging 서버를 테스트에 사용하고, DNS-01의 DNS 자격 증명을 검증하며, 발급을 차단하는 CAA 레코드를 확인하고, 챌린지 중 HTTPS 리다이렉트를 임시로 비활성화하며, 지속적인 실패 시 ACME 제공자에 문의합니다.
