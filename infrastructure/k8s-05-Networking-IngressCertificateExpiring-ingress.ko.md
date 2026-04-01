---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/IngressCertificateExpiring-ingress.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- infrastructure
- ingress
- ingresscertificateexpiring
- k8s-ingress
- k8s-secret
- k8s-service
- kubernetes
- networking
- security
---

---
title: Ingress Certificate Expiring
weight: 55
categories: [kubernetes, ingress]
---

# IngressCertificateExpiring - Ingress 인증서 만료 임박

## 의미

Ingress에서 사용하는 TLS 인증서가 만료에 임박하고 있으며(IngressCertificateExpiring 알림 발생), 자동 갱신이 이루어지지 않았거나 수동 갱신이 필요한 상태입니다. Ingress TLS Secret에 만료 예정인 인증서가 포함되어 있으며, 만료 후 HTTPS 연결이 실패합니다. 이 Ingress를 통한 모든 HTTPS 트래픽에 영향을 미치며, 사용자에게 인증서 경고 후 오류가 표시되고, API 클라이언트가 연결을 거부합니다.

## 영향

IngressCertificateExpiring 알림 발생, HTTPS 중단 임박 경고, 인증서 만료 시 브라우저 보안 경고 발생, API 클라이언트 연결 실패, 모바일 앱 인증서 거부, mTLS 인증 중단, Ingress 트래픽 영향, 고객 대면 서비스 영향, SEO 순위 영향 가능.

## 플레이북

1. Ingress에서 참조하는 TLS Secret을 확인하고 인증서 만료 날짜를 조회합니다.

2. cert-manager가 이 인증서를 관리하는지 확인하기 위해 이 Secret을 참조하는 Certificate 리소스를 확인합니다.

3. cert-manager 관리인 경우: Certificate 리소스 상태와 갱신 조건을 확인합니다.

4. 수동 관리인 경우: CA에서 새 인증서를 준비하고 Secret을 업데이트합니다.

5. Secret 업데이트 시 Ingress Controller가 리로드되는지 확인합니다.

6. 이 인증서에 대한 의존성(동일 인증서를 사용하는 다른 서비스)을 확인합니다.

7. Ingress Controller 리로드 동작을 고려하여 최소한의 중단으로 갱신을 계획합니다.

## 진단

cert-manager가 관리하는 경우 Certificate 리소스 상태를 확인하고, Certificate 조건과 이벤트를 근거로 갱신이 이루어지지 않은 이유를 파악합니다.

cert-manager 관리 인증서의 경우, Issuer 상태와 최근 발급 이력을 근거로 Issuer가 정상이고 새 인증서를 발급할 수 있는지 확인합니다.

수동 관리 인증서의 경우, 인증서 메타데이터와 소유권 문서를 근거로 인증서 갱신을 위한 조직 프로세스를 확인하고 담당 팀을 파악합니다.

Secret 구조와 Ingress 요구사항을 근거로 Secret 형식(tls.crt, tls.key)이 올바르고 업데이트 시 Ingress Controller에서 수락되는지 확인합니다.

클러스터 전체의 Secret 참조를 근거로 인증서가 여러 Ingress 또는 서비스에서 사용되어 조율된 갱신이 필요한지 확인합니다.

지정된 시간 범위 내에서 상관관계가 발견되지 않으면: CA에서 즉시 새 인증서를 발급받고, 새 인증서로 Secret을 업데이트하고, Ingress Controller가 새 인증서를 로드하는지 확인하고, 모니터링 및 자동 갱신을 설정하고, 자동화를 위해 cert-manager로의 마이그레이션을 고려합니다.
