---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/04-Networking/Not-Serving-Updated-Content-CloudFront.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- cloudfront
- cloudwatch
- content
- incident-response
- k8s-service
- networking
- performance
- s3
- serving
- sts
- updated
---

# CloudFront Not Serving Updated Content - CloudFront 업데이트된 콘텐츠 미제공

## 의미

CloudFront가 업데이트된 콘텐츠를 제공하지 않는 현상(캐시 문제 또는 CloudFrontStaleContent 경보 트리거)은 캐시 TTL 설정이 너무 길거나, 캐시 무효화가 수행되지 않았거나, 오리진 캐시 헤더가 업데이트를 방해하거나, CloudFront 배포 캐시 동작이 잘못 구성되었거나, 오리진 서버가 오래된 콘텐츠를 반환하거나, CloudFront 캐시 무효화가 불완전할 때 발생합니다.
 CloudFront가 오래된 캐시 콘텐츠를 제공하고, 콘텐츠 업데이트가 반영되지 않으며, 캐시 무효화가 효과가 없습니다. 이는 콘텐츠 전달 및 CDN 계층에 영향을 미치며 콘텐츠 신선도를 감소시킵니다.

## 영향

CloudFront가 오래된 캐시 콘텐츠를 제공합니다. 콘텐츠 업데이트가 반영되지 않습니다. 캐시 무효화가 효과가 없습니다. 사용자 대면 콘텐츠가 오래됩니다. CDN 캐시 동작이 잘못됩니다. 콘텐츠 새로고침이 실패합니다.

## 플레이북

1. CloudFront 배포 `<distribution-id>`가 존재하고 리전 `<region>`의 CloudFront AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 CloudFront 배포 `<distribution-id>`를 조회하여 캐시 동작 설정, 기본 TTL 구성, 오리진 캐시 정책 설정을 점검합니다.
3. CloudFront 접근 로그가 포함된 CloudWatch Logs에서 배포 `<distribution-id>` 관련 캐시 히트 패턴이나 콘텐츠 수명 지표를 필터링합니다.
4. 배포 `<distribution-id>`의 CloudFront 무효화 이력을 조회하여 무효화 상태, 완료 시간, 무효화 패턴을 확인합니다.
5. CloudFront 배포 `<distribution-id>`의 CloudWatch 지표(CacheHitRate, BytesDownloaded)를 최근 24시간 동안 조회하여 캐시 동작 패턴을 파악합니다.
6. 배포 `<distribution-id>`의 CloudFront 캐시 동작을 나열하고 TTL 설정, 캐시 정책 구성, 오리진 응답 헤더를 확인합니다.
7. CloudFront 배포 `<distribution-id>`의 오리진 구성을 조회하여 오리진 캐시 헤더를 확인합니다.
8. CloudTrail 이벤트가 포함된 CloudWatch Logs에서 최근 24시간 이내 `<distribution-id>` 관련 CloudFront 배포 캐시 정책 또는 무효화 이벤트를 필터링합니다.
9. 배포 `<distribution-id>`의 CloudFront 무효화 상태를 조회하여 최근 무효화가 성공적으로 완료되었는지 확인합니다.

## 진단

1. CloudFront 배포의 CloudWatch 지표(플레이북 5단계)를 분석하여 최근 24시간 동안의 CacheHitRate를 포함한 캐싱 패턴을 파악합니다. 캐시 히트율이 매우 높으면(100%에 가까움) 콘텐츠가 오리진에서 가져오지 않고 캐시에서 제공되고 있는 것입니다.

2. 캐시 무효화 이력(플레이북 4단계 및 9단계)을 검토하여 무효화가 요청되고 성공적으로 완료되었는지 확인합니다. 무효화가 보류 중이거나 실패했으면 캐시 콘텐츠가 업데이트되지 않습니다.

3. CloudFront 캐시 동작 구성(플레이북 6단계)을 확인하여 영향을 받는 콘텐츠 경로의 TTL 설정을 검증합니다. 최소 TTL, 기본 TTL 또는 최대 TTL이 높은 값으로 설정되어 있으면 오리진 업데이트에 관계없이 콘텐츠가 장기간 캐시됩니다.

4. 오리진 캐시 헤더(플레이북 7단계)를 확인하여 오리진 서버가 CloudFront의 TTL 설정을 재정의하는 Cache-Control 또는 Expires 헤더를 보내고 있지 않은지 검증합니다.

5. 오래된 콘텐츠를 즉시 해결하려면 영향을 받는 경로에 대한 캐시 무효화를 생성합니다. 자주 업데이트되는 콘텐츠의 경우 TTL 값을 줄이거나 버전이 지정된 URL을 구현하는 것을 고려합니다.

상관관계를 찾을 수 없는 경우: 기간을 30일로 확장하고, 오리진 서버 캐시 헤더 및 CloudFront 엣지 로케이션 캐시 상태를 포함한 대안적 증거 소스를 검토합니다.