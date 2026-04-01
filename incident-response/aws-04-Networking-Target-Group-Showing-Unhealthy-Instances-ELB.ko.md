---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/AWS%20Playbooks/04-Networking/Target-Group-Showing-Unhealthy-Instances-ELB.md)'
role: SRE / AWS Incident Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- alb
- capacity
- cloudwatch
- elb
- group
- incident-response
- instances
- k8s-service
- networking
- performance
- scaling
- security
- showing
- sts
- target
- unhealthy
---

# Target Group in ELB Showing Unhealthy Instances - ELB 대상 그룹 비정상 인스턴스 표시

## 의미

대상 그룹 인스턴스가 비정상 상태를 표시하는 현상(UnhealthyTargetCount와 같은 경보 트리거)은 대상 인스턴스가 상태 확인에 실패하거나, 보안 그룹 또는 Network ACL이 상태 확인 트래픽을 차단하거나, 리스너 구성이 잘못되었거나, 인스턴스가 올바르게 등록되지 않았거나, 상태 확인 경로 또는 프로토콜이 잘못 구성되었을 때 발생합니다.
 대상 인스턴스가 비정상으로 표시되고, 로드 밸런서가 비정상 대상으로의 트래픽 라우팅을 중지하며, 상태 확인 실패가 증가합니다. 이는 로드 밸런싱 계층에 영향을 미치며 서비스 용량을 감소시킵니다.

## 영향

대상 인스턴스가 비정상으로 표시됩니다. 로드 밸런서가 비정상 대상으로의 트래픽 라우팅을 중지합니다. 서비스 용량이 감소합니다. UnhealthyTargetCount 경보가 발생합니다. 애플리케이션 가용성이 감소합니다. 상태 확인 실패가 증가합니다. 사용자 요청이 타임아웃될 수 있습니다. 서비스 저하가 발생합니다.

## 플레이북

1. 대상 그룹 `<target-group-name>`이 존재하고 로드 밸런서 `<load-balancer-name>`이 활성이며, 리전 `<region>`의 ELB AWS 서비스 상태가 정상인지 확인합니다.
2. 대상 그룹 `<target-group-name>`을 조회하여 대상 인스턴스의 상태를 확인하고 상태 확인 경로, 프로토콜, 포트, 타임아웃, 간격, 정상/비정상 임계값을 포함한 상태 확인 구성을 점검합니다.
3. 대상 그룹 `<target-group-name>`의 대상 유형 구성을 조회하여 대상 유형(인스턴스 vs IP)을 확인합니다.
4. 대상 인스턴스와 연관된 보안 그룹 `<security-group-id>`를 조회하여 로드 밸런서로의/로부터의 상태 확인 트래픽을 허용하는 보안 그룹을 확인합니다.
5. 로드 밸런서 `<load-balancer-name>`의 리스너 구성 및 유형(ALB, NLB, CLB)을 조회하여 상태 확인을 위한 리스너가 올바르게 구성되어 있는지 확인합니다.
7. 대상 그룹 `<target-group-name>`의 대상을 조회하여 인스턴스 등록 상태를 확인하고, 대상 포트가 상태 확인 포트와 일치하는지 검증합니다.
8. 대상 그룹 `<target-group-name>`의 CloudWatch 지표(정상 호스트 수, 비정상 호스트 수, 대상 응답 시간)를 조회하여 상태 확인 패턴을 파악합니다.
9. 대상 그룹 `<target-group-name>`의 상태 확인 경로를 조회하여 상태 확인 경로가 존재하고 200 상태 코드를 반환하는지 확인합니다.
10. 애플리케이션 로그가 포함된 CloudWatch Logs에서 상태 확인 엔드포인트 오류나 상태 확인에 영향을 미치는 애플리케이션 오류를 필터링합니다.

## 진단

1. 플레이북 1단계의 AWS 서비스 상태를 분석하여 리전의 ELB 서비스 가용성을 확인합니다.

2. 플레이북 2단계의 대상 상태에서 구체적인 실패 사유(예: "Health checks failed", "Connection timeout", "HTTP 5xx")가 표시되면 해당 사유를 사용하여 조사를 안내합니다.

3. 플레이북 3단계의 대상 유형이 "instance"이지만 대상이 IP로 등록되었거나 그 반대인 경우, 등록 유형 불일치가 상태 확인 실패를 유발합니다.

4. 플레이북 4단계의 보안 그룹이 상태 확인 포트에서 로드 밸런서 보안 그룹으로부터의 인바운드 트래픽을 허용하지 않으면 상태 확인이 대상에 도달할 수 없습니다.

5. 플레이북 5단계의 리스너 구성에서 상태 확인 설정(경로, 포트, 프로토콜)이 애플리케이션 기대와 다르면 상태 확인이 실패합니다.

6. 플레이북 8단계의 CloudWatch 지표에서 HealthyHostCount가 갑자기 감소했다면 타임스탬프를 배포 이벤트, 인스턴스 상태 변경 또는 보안 그룹 변경과 상관 분석합니다.

7. 플레이북 9단계의 상태 확인 경로가 대상 애플리케이션에 존재하지 않거나 200이 아닌 응답을 반환하면 애플리케이션이 상태 프로브에 올바르게 응답하지 않는 것입니다.

상관관계를 찾을 수 없는 경우: 애플리케이션 로그 쿼리 기간을 30분으로 확장하고, 인스턴스 수준 리소스 사용률(CPU, 메모리, 디스크)을 확인하고, 애플리케이션 종속성 실패를 점검합니다.