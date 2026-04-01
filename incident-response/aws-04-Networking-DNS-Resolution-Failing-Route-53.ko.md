---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/04-Networking/DNS-Resolution-Failing-Route-53.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudfront
- dns
- failing
- incident-response
- k8s-service
- networking
- performance
- rds
- resolution
- route
- route53
- sts
---

# Route 53 DNS Resolution Failing - Route 53 DNS 해석 실패

## 의미

Route 53 DNS 해석이 실패하거나 잘못된 결과를 반환하는 현상(DNS 해석 오류 또는 Route53DNSResolutionFailed 경보 트리거)은 호스팅 영역이 잘못 구성되었거나, DNS 레코드(A, AAAA, CNAME)가 잘못 설정되었거나, 네임 서버가 도메인에 대해 잘못 구성되었거나, DNS 해석 테스트가 실패하거나, Route 53 상태 확인이 문제를 나타내거나, TTL 설정이 전파에 영향을 미치거나, 라우팅 정책이 잘못 구성되었을 때 발생합니다.
 DNS 쿼리가 실패하고, 도메인 이름을 해석할 수 없으며, DNS 해석 오류가 발생합니다. 이는 DNS 및 서비스 디스커버리 계층에 영향을 미치며 도메인 해석을 차단합니다. 일반적으로 DNS 구성 문제, 상태 확인 실패 또는 라우팅 정책 문제가 원인이며, CloudFront 또는 Global Accelerator와 함께 Route 53을 사용하는 경우 DNS 구성이 다를 수 있고 애플리케이션에서 도메인 해석 실패가 발생할 수 있습니다.

## 영향

DNS 쿼리가 실패합니다. 도메인 이름을 해석할 수 없습니다. 애플리케이션이 서비스에 연결할 수 없습니다. DNS 해석 오류가 발생합니다. 서비스 엔드포인트에 접근할 수 없게 됩니다. DNS 전파 문제가 발생할 수 있습니다. 상태 확인 실패가 트리거될 수 있습니다. 사용자 대면 서비스에 접근할 수 없게 됩니다. 서비스 디스커버리가 실패합니다.

## 플레이북

1. Route 53 호스팅 영역 `<hosted-zone-id>`가 존재하고 도메인이 등록되어 있으며, 리전 `<region>`의 Route 53 AWS 서비스 상태가 정상인지 확인합니다.
2. Route 53 호스팅 영역 `<hosted-zone-id>`를 조회하여 호스팅 영역이 올바르게 구성되어 있고 DNS 레코드(A, AAAA, CNAME)가 올바르게 설정되어 있는지 확인합니다.
3. Route 53 호스팅 영역 `<hosted-zone-id>`의 네임 서버 구성을 조회하여 네임 서버가 도메인에 대해 올바르게 구성되어 있는지 확인합니다.
4. Route 53 호스팅 영역 `<hosted-zone-id>`의 TTL 설정을 조회하여 TTL 값이 적절한지 확인합니다.
5. Route 53 호스팅 영역 `<hosted-zone-id>`의 라우팅 정책 구성을 조회하여 라우팅 정책(Simple, Weighted, Latency, Failover)이 올바르게 구성되어 있는지 확인합니다.
6. 호스팅 영역 `<hosted-zone-id>`와 연관된 Route 53 상태 확인을 조회하고 구성된 경우 상태 확인 상태를 확인합니다.
7. Route 53 호스팅 영역 `<hosted-zone-id>`의 별칭 레코드 구성을 조회하여 별칭 레코드가 올바른 리소스를 가리키는지 확인합니다.
8. Route 53 쿼리 로그 또는 CloudFront 로그가 포함된 CloudWatch Logs 로그 그룹에서 호스팅 영역 `<hosted-zone-id>` 관련 DNS 해석 실패나 문제를 필터링합니다.

## 진단

1. 플레이북 1단계의 AWS 서비스 상태를 분석하여 Route 53 서비스 가용성을 확인합니다. Route 53은 글로벌 서비스이므로 전 세계 서비스 상태 문제를 확인합니다.

2. 플레이북 2단계의 호스팅 영역 구성에서 호스팅 영역이 존재하지 않거나 DNS 레코드가 누락/잘못되어 있으면 권한 수준에서 해석이 실패합니다. 쿼리된 도메인에 대한 A, AAAA 또는 CNAME 레코드가 존재하는지 확인합니다.

3. 플레이북 3단계의 네임 서버 구성에서 도메인의 등록된 네임 서버가 Route 53 호스팅 영역 네임 서버와 일치하지 않으면 DNS 쿼리가 잘못된 권한 서버로 전송됩니다. 이것이 새 호스팅 영역에서 해석 실패의 가장 흔한 원인입니다.

4. 플레이북 4단계의 TTL 설정에서 매우 긴 TTL 값이 표시되면 DNS 변경이 TTL 기간 동안 전파되지 않을 수 있습니다.

5. 플레이북 5단계의 라우팅 정책에서 가중치, 지연, 장애 조치 또는 지리적 위치 라우팅에 정상 엔드포인트가 없거나 가중치가 잘못 구성되어 있으면(모두 0) 응답이 반환되지 않습니다.

6. 플레이북 6단계의 상태 확인에서 장애 조치 또는 가중치 레코드의 모든 상태 확인이 비정상이면 Route 53이 레코드를 반환하지 않을 수 있습니다.

7. 플레이북 7단계의 별칭 레코드 구성이 존재하지 않거나 비정상인 대상(ELB, CloudFront, S3 웹사이트)을 가리키면 별칭에 대한 해석이 실패합니다.

8. 플레이북 8단계의 Route 53 쿼리 로그 또는 CloudFront 로그에서 NXDOMAIN 또는 SERVFAIL 응답이 표시되면 구체적인 쿼리 패턴과 응답 코드를 파악하여 실패 유형을 진단합니다.

상관관계를 찾을 수 없는 경우: DNS 전파 지연을 고려하여 분석 기간을 48시간으로 확장하고, 도메인 등록이 활성이고 만료되지 않았는지 확인하고, DNSSEC가 활성화된 경우 DNSSEC 검증 실패를 점검하고, 여러 지리적 위치에서 해석을 테스트합니다.