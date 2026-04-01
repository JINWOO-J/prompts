---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/CertManagerControllerHighError-cert.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- cert
- certmanagercontrollerhigherror
- control
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-rbac
- k8s-service
- kubernetes
- plane
- security
- sts
---

---
title: Cert Manager Controller High Error Rate - cert-manager Controller 높은 오류율
weight: 44
categories: [kubernetes, cert-manager]
---

# CertManagerControllerHighError

## 의미

cert-manager Controller가 높은 오류율을 경험하고 있으며(CertManagerControllerHighError 알림 트리거), 인증서 작업이 빈번하게 실패하여 Issuer, 구성 또는 클러스터 연결에 체계적인 문제가 있음을 나타냅니다. Controller 메트릭에서 오류 수가 증가하고, 인증서 작업이 성공적으로 완료되지 않으며, 인증서 관리가 저하된 상태입니다. 클러스터 전체의 인증서 발급 및 갱신에 영향을 미칩니다. 인증서가 발급되거나 갱신되지 않을 수 있으며, 수동 개입이 더 많이 필요합니다.

## 영향

CertManagerControllerHighError 알림이 발생합니다. 인증서 작업이 빈번하게 실패하고, 새 인증서 요청이 실패할 수 있으며, 갱신이 지연될 수 있습니다. 인증서 상태가 신뢰할 수 없고, 수동 개입이 더 자주 필요합니다. 인증서에 의존하는 Deployment가 지연되며, 갱신 실패로 보안 상태에 영향을 미칠 수 있습니다.

## 플레이북

1. cert-manager Controller 로그를 조회하고 ERROR 수준 메시지를 필터링하여 일반적인 실패 패턴을 식별합니다.

2. Controller 메트릭에서 작업 유형별(발급, 갱신, 동기화) 오류율 분석을 확인합니다.

3. 가장 많은 실패가 발생하는 Issuer 또는 ClusterIssuer를 식별합니다.

4. cert-manager의 API Server 연결성과 RBAC 권한을 검증합니다.

5. 오류 상태에 머물러 있는 Certificate 또는 CertificateRequest 리소스를 확인합니다.

6. Webhook 서비스가 정상이고 올바르게 응답하는지 검증합니다.

7. Controller 작업에 영향을 미치는 리소스 경합 또는 스로틀링을 확인합니다.

## 진단

오류를 유형별로 분류하고 특정 Issuer, 네임스페이스 또는 인증서 유형에 오류가 집중되어 있는지 식별합니다. 오류 로그와 메트릭 분석을 근거로 사용합니다.

cert-manager가 리소스를 읽거나 업데이트하는 것을 방해하는 API Server 연결 문제를 확인합니다. API Server 지연 메트릭과 오류 로그를 근거로 사용합니다.

Issuer 자격 증명(ACME 계정, CA Secret, Vault 토큰)이 유효하고 만료되지 않았는지 검증합니다. Issuer 상태와 자격 증명 검증을 근거로 사용합니다.

외부 ACME 제공자의 속도 제한으로 인한 작업 실패를 확인합니다. 로그의 ACME 응답을 근거로 사용합니다.

Controller 재시작 이력을 분석하고 재시작이 오류 급증과 상관관계가 있는지(Controller 불안정성 시사) 검증합니다. Pod 재시작 타임스탬프와 오류 메트릭을 근거로 사용합니다.

지정된 시간 범위 내에서 연관 관계를 찾을 수 없는 경우: 최근 cert-manager 또는 클러스터 업그레이드를 검토하고, CRD 호환성을 검증하며, 메모리 또는 CPU 제약을 확인하고, RBAC 변경을 검토하며, Controller가 손상된 경우 cert-manager 재설치를 고려합니다.
