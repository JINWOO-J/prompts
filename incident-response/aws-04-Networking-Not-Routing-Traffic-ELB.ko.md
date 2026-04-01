---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/04-Networking/Not-Routing-Traffic-ELB.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- alb
- capacity
- cloudwatch
- elb
- incident-response
- k8s-service
- networking
- performance
- routing
- security
- sts
- traffic
---

# Elastic Load Balancer (ELB) Not Routing Traffic - ELB 트래픽 라우팅 불가

## 의미

Elastic Load Balancer가 대상 인스턴스로 트래픽을 라우팅하지 못하는 현상(UnhealthyTargetCount 또는 TargetResponseTime과 같은 경보 트리거)은 대상 인스턴스가 비정상이거나, 보안 그룹 또는 Network ACL이 트래픽을 차단하거나, 리스너 구성이 잘못되었거나, 인스턴스가 대상 그룹에 올바르게 등록되지 않았거나, 로드 밸런서 스킴이 잘못 구성되었거나, 리스너 규칙이 라우팅을 방해할 때 발생합니다.
 로드 밸런서가 요청을 라우팅할 수 없고, 애플리케이션이 트래픽을 받지 못하며, 상태 확인이 실패합니다. 이는 로드 밸런싱 계층에 영향을 미치며 서비스 접근을 차단합니다.

## 영향

로드 밸런서가 요청을 라우팅할 수 없습니다. 애플리케이션이 트래픽을 받지 못합니다. 서비스를 사용할 수 없게 됩니다. 상태 확인이 실패합니다. UnhealthyTargetCount 경보가 발생합니다. 대상 응답 시간이 증가합니다. 사용자 요청이 타임아웃됩니다. 서비스 엔드포인트에 접근할 수 없게 됩니다. 고가용성이 손상됩니다.

## 플레이북

1. 로드 밸런서 `<load-balancer-name>`과 대상 그룹 `<target-group-name>`이 존재하고, 리전 `<region>`의 ELB AWS 서비스 상태가 정상인지 확인합니다.
2. 로드 밸런서 `<load-balancer-name>`과 연관된 대상 그룹 `<target-group-name>`을 조회하여 대상 인스턴스의 상태를 확인합니다.
3. 로드 밸런서 `<load-balancer-name>`의 유형(ALB, NLB, CLB)을 조회하여 유형별 라우팅 동작을 확인합니다.
4. 로드 밸런서 `<load-balancer-name>`의 스킴(인터넷 대면 vs 내부)을 조회하여 스킴이 요구사항과 일치하는지 확인합니다.
5. 로드 밸런서 `<load-balancer-name>`과 연관된 보안 그룹 `<security-group-id>`를 조회하여 로드 밸런서로의/로부터의 트래픽을 허용하는 보안 그룹을 확인합니다.
6. 로드 밸런서 `<load-balancer-name>`의 리스너 구성 및 리스너 규칙을 조회하여 리스너가 올바르게 구성되어 있는지(예: 올바른 포트의 HTTP/HTTPS) 확인합니다.
8. 대상 그룹 `<target-group-name>`의 대상을 조회하여 인스턴스 등록 상태를 확인하고, 대상 포트를 검증합니다.
9. 로드 밸런서 `<load-balancer-name>`의 CloudWatch 지표(요청 수, 대상 응답 시간, 정상 호스트 수)를 조회하여 트래픽 패턴을 파악합니다.
10. 애플리케이션 로그가 포함된 CloudWatch Logs에서 로드 밸런서 접근 로그 오류나 라우팅 문제를 필터링합니다.

## 진단

1. 플레이북 2단계의 대상 상태에서 모든 대상이 "unhealthy"이면 로드 밸런서에 트래픽을 라우팅할 정상 백엔드가 없습니다.

2. 플레이북 3단계의 로드 밸런서 유형이 애플리케이션 요구사항과 다르면(HTTP/HTTPS용 ALB, TCP/UDP용 NLB) 로드 밸런서 유형이 필요한 라우팅 동작을 지원하지 않을 수 있습니다.

3. 플레이북 4단계의 로드 밸런서 스킴이 "internal"이지만 클라이언트가 인터넷에서 연결을 시도하면 로드 밸런서에 인터넷으로 접근할 수 없습니다.

4. 플레이북 5단계의 보안 그룹이 리스너 포트의 인바운드 트래픽이나 대상 포트의 아웃바운드 트래픽을 허용하지 않으면 네트워크 접근이 차단됩니다.

5. 플레이북 6단계의 리스너 구성에서 잘못된 포트, 프로토콜 또는 라우팅 규칙이 표시되면 트래픽이 대상으로 올바르게 전달되지 않습니다.

6. 플레이북 8단계의 대상 등록에서 인스턴스가 등록되지 않았거나 "draining" 상태이면 대상을 트래픽에 사용할 수 없습니다.

상관관계를 찾을 수 없는 경우: 접근 로그 쿼리 기간을 30분으로 확장하고, 로드 밸런서 엔드포인트의 DNS 해석을 확인하고, 트래픽을 차단하는 AWS WAF 규칙을 점검합니다.