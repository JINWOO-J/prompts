---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/07-Operational-Readiness/Certificate-Expiration-Monitoring-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- certificate
- expiration
- infrastructure
- k8s-ingress
- k8s-namespace
- k8s-pod
- k8s-service
- monitoring
- operational
- readiness
- security
---

# Certificate Expiration Monitoring — 인증서 만료 모니터링

## 의미

인증서 만료 모니터링은 SSL/TLS 인증서가 만료에 근접하거나 이미 만료되어 서비스 중단을 유발할 수 있음을 나타냅니다(CertificateExpiring 또는 CertificateExpired 같은 알림 발생).
 인증서 만료일이 경고 임계값 이내이거나, 인증서가 만료되었거나, 인증서 갱신이 이루어지지 않았거나, 인증서 상태에서 만료 경고가 나타나거나, 인증서 모니터링에서 다가오는 만료가 감지되는 것이 원인입니다. 인증서가 경고 기간 내의 만료일을 보이고, 인증서 상태에서 만료가 표시되며, 인증서 갱신 상태에서 실패가 나타나고, 인증서 모니터링 알림이 다가오는 만료에 대해 발생합니다. 이는 보안 계층과 서비스 가용성에 영향을 미치며, 일반적으로 인증서 수명 주기 관리 실패, 인증서 갱신 자동화 문제, 또는 인증서 모니터링 설정 오류로 인해 발생합니다. 인증서가 컨테이너 워크로드를 보호하는 경우, 컨테이너 Ingress 인증서가 만료되고 애플리케이션에서 TLS 연결 실패가 발생할 수 있습니다.

## 영향

CertificateExpiring 알림 발생, CertificateExpired 알림 발생, SSL/TLS 연결 실패 가능, 서비스 비가용 가능, 인증서 갱신 미수행, 인증서 수명 주기 관리 실패. 인증서 만료일이 경고 임계값 이내이며, 인증서가 컨테이너 워크로드를 보호하는 경우 컨테이너 Ingress 인증서가 만료되고, Pod TLS 연결이 실패하며, 컨테이너 애플리케이션에서 TLS 연결 실패가 발생할 수 있습니다. 애플리케이션에서 서비스 비가용 또는 TLS 핸드셰이크 실패가 발생할 수 있습니다.

## 플레이북

1. 네임스페이스 <namespace>의 Certificate를 조회하여 모든 인증서와 만료일을 포함한 현재 상태를 확인합니다.

2. 네임스페이스 <namespace>의 최근 이벤트를 타임스탬프 순으로 조회하여 최근 인증서 갱신 문제나 만료 경고를 확인합니다.

3. 네임스페이스 <namespace>의 Certificate <certificate-name>을 상세 조회하여 만료일, 상태, 갱신 구성을 확인합니다.

4. 네임스페이스 <namespace>의 Ingress 리소스를 YAML 출력으로 조회하여 Ingress 인증서 구성과 다가오는 만료를 확인합니다.

5. cert-manager 네임스페이스에서 app=cert-manager 레이블의 cert-manager Pod 로그를 조회하고 만료 경고 또는 인증서 갱신 실패를 필터링합니다.

6. 네임스페이스 <namespace>에서 kubernetes.io/tls 유형으로 필터링된 Secret을 조회하여 인증서 만료일을 확인합니다.

7. 지난 30일 동안의 인증서 서비스에 대한 Prometheus 메트릭(certificate_expiration_time, certificate_status 포함)을 조회하여 만료에 근접한 인증서를 확인합니다.

8. Certificate 리소스 갱신 상태와 cert-manager 구성을 확인하여 인증서 갱신 자동화를 검증합니다.

## 진단

1. 1단계와 3단계의 인증서 상태를 검토합니다. 인증서가 경고 임계값(예: 30일 미만) 이내의 만료를 보이면 갱신 조치가 필요합니다. 인증서가 이미 만료되었으면 즉각적인 갱신이 중요합니다.

2. 5단계의 cert-manager 로그를 분석합니다. 로그에서 갱신 실패가 나타나면 실패 원인(ACME 챌린지, DNS 검증, 권한, 또는 인증 기관 문제)을 확인합니다. 로그에서 갱신 시도가 없으면 스케줄링이 문제입니다.

3. 4단계의 Ingress 인증서에서 다가오는 만료가 나타나면 cert-manager가 해당 인증서를 관리하도록 구성되어 있는지 확인합니다. cert-manager가 관리하지 않으면 수동 갱신 프로세스가 필요합니다.

4. 7단계의 인증서 메트릭을 검토합니다. certificate_expiration_time에서 갱신 활동 없이 만료에 근접한 인증서가 나타나면 갱신 자동화가 실패하고 있습니다.

5. 6단계의 TLS Secret에서 최근 업데이트 없이 오래된 생성 타임스탬프가 나타나면 인증서 로테이션이 이루어지지 않고 있습니다. Secret에서 최근 업데이트가 나타나면 인증서가 갱신되고 있습니다.

분석이 결론에 도달하지 못하는 경우: 2단계의 이벤트에서 인증서 갱신 문제나 만료 경고를 확인합니다. 8단계의 인증서 갱신 자동화를 검토하여 cert-manager 구성을 확인합니다. 만료 문제가 특정 인증서에 영향을 미치는지(인증서별 구성 문제 시사) 또는 모든 인증서에 영향을 미치는지(cert-manager 인프라 문제 시사) 판단합니다.
