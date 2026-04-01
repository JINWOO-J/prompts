---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/05-Networking/IngressSSLTLSConfigurationFails-ingress.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- infrastructure
- ingress
- ingressssltlsconfigurationfails
- k8s-ingress
- k8s-namespace
- k8s-pod
- k8s-secret
- kubernetes
- networking
- performance
---

---
title: Ingress SSL/TLS Configuration Fails - Ingress
weight: 279
categories:
  - kubernetes
  - ingress
---

# IngressSSLTLSConfigurationFails-ingress - Ingress SSL/TLS 설정 실패

## 의미

Ingress SSL/TLS 설정이 실패하고 있으며(KubeIngressNotReady 또는 KubeIngressCertificateExpiring 알림 발생), Ingress TLS 설정에서 참조하는 TLS Secret이 누락되었거나 유효하지 않거나, Ingress 어노테이션(cert-manager.io/issuer)의 인증서 참조가 잘못되었거나, 인증서 발급자(cert-manager)가 사용 불가능하거나, TLS 어노테이션이 잘못 구성된 것이 원인입니다.

## 영향

Ingress Endpoint에서 인증서 오류 반환, TLS Secret이 누락 또는 유효하지 않은 상태 표시 가능, cert-manager Pod에서 장애 표시 가능. 이는 네트워크 계층에 영향을 미치며 애플리케이션에 대한 안전한 외부 접근을 방해하고, 일반적으로 누락된 TLS Secret, 인증서 만료 또는 cert-manager 장애가 원인입니다. 애플리케이션이 사용자에게 접근 불가능해지며 오류가 발생할 수 있습니다.

HTTPS 연결 실패, SSL/TLS 핸드셰이크 오류 발생, 인증서 검증 불가, 보안 트래픽 차단, Ingress Endpoint에서 인증서 오류 반환, Ingress가 TLS 연결을 수립할 수 없을 때 KubeIngressNotReady 알림 발생, 인증서가 만료되었거나 만료 임박 시 KubeIngressCertificateExpiring 알림 발생, 사용자에게 SSL 인증서 경고 표시, Ingress에서 TLS 종료 실패, Ingress 상태에 TLS 설정 오류 표시, 애플리케이션에 대한 안전한 외부 접근 실패. Ingress Endpoint에서 무기한 인증서 오류 반환, TLS Secret이 누락 또는 유효하지 않은 상태 표시 가능, 애플리케이션이 사용자에게 접근 불가능해지며 오류 또는 성능 저하 발생 가능, 애플리케이션에 대한 안전한 외부 접근 실패.

## 플레이북

1. `<namespace>` Namespace에서 `kubectl describe ingress <ingress-name> -n <namespace>`를 사용하여 Ingress `<ingress-name>`을 상세 조회하고, TLS 섹션, 어노테이션, TLS Secret 참조를 포함한 TLS 설정을 검사합니다.

2. `<namespace>` Namespace에서 `kubectl get events -n <namespace> --field-selector involvedObject.name=<ingress-name> --sort-by='.lastTimestamp'`를 사용하여 이벤트를 조회하고, `Failed`, `Sync` 또는 인증서/Secret 문제를 나타내는 메시지에 초점을 맞춰 TLS 관련 이벤트를 필터링합니다.

3. Ingress TLS 설정에서 참조된 Secret `<tls-secret-name>`을 조회하고 존재 여부, 유효한 인증서 및 키 데이터 포함 여부, 만료 여부를 확인합니다.

4. 인증서 발급자 설정에 대한 Ingress 어노테이션(예: `cert-manager.io/issuer`, `cert-manager.io/cluster-issuer`)을 확인하고 인증서 관리가 구성되어 있는지 확인합니다.

5. cert-manager를 사용하는 경우 Certificate 또는 CertificateRequest 리소스를 조회하고 상태를 확인하여 인증서가 발급 또는 갱신되고 있는지 확인합니다.

6. `<namespace>` Namespace에서 Ingress Controller Pod `<controller-pod-name>`의 로그를 조회하고, TLS 오류, 인증서 검증 실패 또는 Secret 접근 오류를 필터링합니다.

## 진단

플레이북 섹션에서 수집한 Ingress 상세 조회 출력, TLS Secret 상태, cert-manager 리소스를 분석하는 것부터 시작합니다. TLS Secret 내용, 인증서 유효성, Issuer 상태가 주요 진단 신호를 제공합니다.

**Ingress에서 참조된 TLS Secret이 존재하지 않는 경우:**
- 인증서 Secret이 누락되었습니다. cert-manager가 이를 생성하도록 구성되어 있는지 확인합니다. Ingress에 올바른 cert-manager 어노테이션이 있는지 확인합니다. 수동으로 인증서를 관리하는 경우 유효한 `tls.crt` 및 `tls.key` 데이터로 Secret을 생성합니다.

**TLS Secret이 존재하지만 유효하지 않거나 만료된 인증서 데이터를 포함하는 경우:**
- 인증서가 만료되었거나 형식이 잘못되었습니다. `openssl x509 -in <cert> -text -noout`을 사용하여 인증서를 디코딩하고 유효 기간과 주체를 확인합니다. 수동으로 인증서를 갱신하거나 cert-manager 갱신을 트리거합니다.

**cert-manager Certificate 리소스가 Ready 이외의 상태를 보이는 경우:**
- 인증서 발급 또는 갱신이 실패하고 있습니다. Certificate 상태 조건에서 오류 메시지를 확인합니다. CertificateRequest 및 Order 리소스에서 상세한 실패 사유를 확인합니다.

**cert-manager 로그에서 ACME 챌린지 실패가 표시되는 경우:**
- Let's Encrypt 검증이 실패하고 있습니다. HTTP-01 챌린지의 경우 Ingress가 `/.well-known/acme-challenge/` 경로로의 트래픽을 허용하는지 확인합니다. DNS-01의 경우 DNS 프로바이더 자격 증명과 권한을 확인합니다.

**Ingress Controller 로그에서 TLS 핸드셰이크 오류가 표시되는 경우:**
- 인증서가 호스트명과 일치하지 않거나 인증서 체인이 불완전할 수 있습니다. 인증서 Subject Alternative Names에 Ingress 호스트명이 포함되어 있는지 확인합니다. `tls.crt`에 중간 인증서가 포함되어 있는지 확인합니다.

**TLS가 일부 호스트명에서는 작동하지만 다른 호스트명에서는 작동하지 않는 경우:**
- 여러 TLS 섹션이 충돌하거나 특정 호스트명에 인증서가 없을 수 있습니다. Ingress의 각 호스트명에 해당하는 TLS 항목이 있거나 와일드카드 인증서로 커버되는지 확인합니다.

**이벤트가 결론적이지 않은 경우, 타임스탬프를 상관 분석합니다:**
1. Secret 리소스 버전을 검사하여 Secret 삭제 또는 수정 후 TLS 실패가 시작되었는지 확인합니다.
2. cert-manager Pod 재시작 또는 Issuer 수정과 실패가 일치하는지 확인합니다.
3. 인증서 만료 날짜와 실패 타임스탬프를 비교합니다.

**명확한 원인이 파악되지 않는 경우:** `openssl s_client -connect <host>:443 -servername <hostname>`을 사용하여 TLS 설정을 테스트하고 Ingress Controller가 반환하는 인증서 체인을 검사합니다.
