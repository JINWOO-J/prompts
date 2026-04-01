---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/04-Networking/Not-Distributing-Traffic-Properly-Global-Accelerator.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- accelerator
- distributing
- global
- incident-response
- k8s-service
- networking
- performance
- properly
- sts
- traffic
---

# AWS Global Accelerator Not Distributing Traffic Properly - AWS Global Accelerator 트래픽 분배 이상

## 의미

AWS Global Accelerator가 트래픽을 올바르게 분배하지 않는 현상(트래픽 분배 실패 또는 GlobalAcceleratorTrafficDistributionFailed 경보 트리거)은 액셀러레이터 엔드포인트 그룹 구성이 잘못되었거나, 상태 확인 실패로 트래픽 라우팅이 방해되거나, 엔드포인트 가중치가 잘못 구성되었거나, 트래픽 다이얼 설정이 분배를 제한하거나, 엔드포인트 상태가 라우팅을 방해하거나, Global Accelerator 리스너 구성이 잘못되었을 때 발생합니다.
 Global Accelerator 트래픽 분배가 실패하고, 트래픽이 정상 엔드포인트로 라우팅되지 않으며, 트래픽 분배가 불균등합니다. 이는 네트워킹 및 글로벌 라우팅 계층에 영향을 미치며 트래픽 최적화를 감소시킵니다.

## 영향

Global Accelerator 트래픽 분배가 실패합니다. 트래픽이 정상 엔드포인트로 라우팅되지 않습니다. 트래픽 분배가 불균등합니다. 엔드포인트 그룹 라우팅이 효과가 없습니다. 사용자 요청이 최적으로 분배되지 않습니다. 트래픽 다이얼 설정이 흐름을 제한합니다. 액셀러레이터 라우팅 성능이 저하됩니다.

## 플레이북

1. Global Accelerator `<accelerator-arn>`이 존재하고 리전 `<region>`의 Global Accelerator AWS 서비스 상태가 정상인지 확인합니다.
2. 리전 `<region>`의 Global Accelerator `<accelerator-arn>`을 조회하여 엔드포인트 그룹 구성, 엔드포인트 구성, 상태 확인 설정, 트래픽 다이얼 구성을 점검합니다.
3. 액셀러레이터 `<accelerator-arn>`의 Global Accelerator 엔드포인트 상태를 조회하여 엔드포인트 상태, 상태 확인 결과, 엔드포인트 가용성을 확인합니다.
4. Global Accelerator 이벤트가 포함된 CloudWatch Logs에서 트래픽 분배 패턴이나 라우팅 결정 로그를 필터링합니다.
5. Global Accelerator `<accelerator-arn>`의 CloudWatch 지표(FlowLogs, HealthCheckStatus)를 최근 1시간 동안 조회하여 트래픽 분배 패턴을 파악합니다.
6. 액셀러레이터 `<accelerator-arn>`의 Global Accelerator 리스너를 나열하고 리스너 구성, 엔드포인트 그룹 연결, 라우팅 구성을 확인합니다.
7. Global Accelerator `<accelerator-arn>`의 엔드포인트 가중치를 조회하여 가중치 구성을 확인합니다.
8. Global Accelerator `<accelerator-arn>`의 트래픽 다이얼 설정을 조회하여 트래픽 다이얼 구성을 확인합니다.
9. CloudTrail 이벤트가 포함된 CloudWatch Logs에서 최근 24시간 이내 액셀러레이터 `<accelerator-arn>` 관련 Global Accelerator 엔드포인트 그룹 또는 리스너 변경 이벤트를 필터링합니다.

## 진단

1. Global Accelerator의 CloudWatch 지표(플레이북 5단계)를 분석하여 트래픽 분배 패턴을 파악합니다. 지표에서 일부 엔드포인트로만 트래픽이 흐르면 상태 확인 실패 또는 가중치 구성이 문제입니다.

2. 엔드포인트 상태(플레이북 3단계)를 검토하여 모든 엔드포인트가 정상인지 확인합니다. 엔드포인트가 비정상 상태이면 트래픽을 라우팅할 수 없습니다.

3. 엔드포인트 그룹 구성(플레이북 2단계)을 확인하여 엔드포인트 가중치, 트래픽 다이얼 설정, 상태 확인 구성을 검증합니다. 엔드포인트 가중치가 0이거나 트래픽 다이얼이 0%이면 해당 엔드포인트로 트래픽이 라우팅되지 않습니다.

4. 트래픽 다이얼 설정(플레이북 8단계)을 검토하여 트래픽이 제한되고 있지 않은지 확인합니다. 트래픽 다이얼이 100% 미만이면 해당 엔드포인트 그룹으로 트래픽의 일부만 라우팅됩니다.

5. 리스너 구성(플레이북 6단계)을 확인하여 포트 매핑과 엔드포인트 그룹 연결이 올바른지 검증합니다.

6. CloudTrail 이벤트(플레이북 9단계)와 트래픽 분배 실패 타임스탬프를 5분 이내로 상관 분석합니다.

상관관계를 찾을 수 없는 경우: 기간을 24시간으로 확장하고, 엔드포인트 가중치 구성 및 리스너 라우팅 설정을 포함한 대안적 증거 소스를 검토합니다.