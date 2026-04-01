---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/03-Backup-DR/Multi-cluster-Failover-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- backup
- cluster
- dns
- failover
- infrastructure
- k8s-ingress
- k8s-namespace
- k8s-pod
- k8s-service
- multi
- networking
- rds
---

# Multi-cluster Failover (멀티 클러스터 페일오버)

## 의미

멀티 클러스터 페일오버 알림은 크로스 클러스터 페일오버 절차를 실행할 수 없거나 재해 복구 시나리오에서 페일오버 작업이 실패하는 상황(FailoverFailed 또는 MultiClusterFailoverFailed 같은 알림 발생)을 나타냅니다. 페일오버 작업 타임아웃, DNS 페일오버 미발생, 크로스 클러스터 복제 비동기화, 페일오버 헬스 체크 실패, 또는 페일오버 자동화 트리거 미활성화 등이 원인입니다.
 페일오버 작업이 실패 상태를 보이고, DNS 레코드가 보조 클러스터로 업데이트되지 않으며, 크로스 클러스터 복제가 지연이나 오류를 보이고, 페일오버 헬스 체크가 보조 클러스터에서 비정상 상태를 나타냅니다. 이는 네트워킹 계층과 재해 복구 인프라에 영향을 미치며, 주로 DNS 전파 문제, 복제 지연 문제, 헬스 체크 실패, 또는 페일오버 자동화 설정 오류가 원인입니다. 페일오버가 컨테이너 워크로드를 보호하는 경우, 컨테이너 서비스가 사용 불가 상태로 유지되고 애플리케이션이 장시간 다운타임을 겪을 수 있습니다.

## 영향

MultiClusterFailoverFailed 알림 발생, FailoverFailed 알림 발생, 재해 복구 절차 실행 불가, RTO 목표 미충족, 주 클러스터에서 서비스 사용 불가 유지, DNS 페일오버 미발생, 크로스 클러스터 복제 비동기화, 페일오버 헬스 체크 실패. 페일오버 작업이 대기 또는 실패 상태로 유지되고, DNS 레코드가 보조 클러스터 엔드포인트로 업데이트되지 않습니다. 페일오버가 컨테이너 워크로드를 보호하는 경우, 컨테이너 서비스가 사용 불가 상태로 유지되고, 보조 클러스터에서 Pod 스케줄링이 실패하며, 컨테이너 애플리케이션이 장시간 다운타임을 겪을 수 있습니다. 애플리케이션이 장시간 서비스 중단 또는 데이터 손실을 경험할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 Ingress, Service, Endpoint를 wide 출력으로 조회하고 namespace <namespace>에서 Ingress <ingress-name>을 describe하여 페일오버 설정과 현재 클러스터 라우팅 상태를 파악합니다.

2. namespace <namespace>에서 최근 이벤트를 타임스탬프 순으로 조회하고 kube-system namespace에서 Ingress 관련 이벤트를 필터링하여 최근 페일오버 트리거나 DNS 업데이트 문제를 확인합니다.

3. namespace <namespace>에서 Ingress <ingress-name>의 헬스 체크 설정을 조회하고 상태, 엔드포인트 설정, 실패 임계값 설정을 점검하여 헬스 체크 접근성을 확인합니다.

4. namespace <namespace>에서 Service를 조회하고 Service 엔드포인트 설정을 확인하여 페일오버 엔드포인트 설정과 현재 활성 클러스터 엔드포인트를 검증합니다.

5. Ingress 헬스 체크의 Prometheus 메트릭(ingress_health_status, ingress_health_failure_reason)을 최근 1시간 동안 조회하여 헬스 체크 실패 패턴을 확인합니다.

6. namespace <namespace>에서 Ingress 컨트롤러 Pod의 로그를 조회하고 최근 1시간 내 페일오버 레코드 변경 패턴이나 DNS 업데이트 실패를 필터링합니다.

7. 리소스 <resource-name>의 크로스 클러스터 복제 상태를 조회하고 복제 지연 메트릭을 확인하여 주 클러스터와 보조 클러스터 간 복제 동기화를 점검합니다.

8. 주 클러스터 <primary-cluster>와 보조 클러스터 <secondary-cluster>에서 'firing' 상태의 활성 Prometheus 알림을 조회하여 클러스터 서비스 상태 차이를 확인합니다.

9. 보조 클러스터 <secondary-cluster>에서 Deployment <deployment-name> 설정을 조회하고 레플리카 수와 Pod 상태를 확인하여 보조 클러스터 준비 상태를 점검합니다.

10. DNS 레코드 업데이트 타임스탬프와 페일오버 트리거 타임스탬프를 5분 이내로 비교하여 DNS 페일오버가 예상 시간 내에 발생하는지 확인하고, Ingress 컨트롤러 로그를 보조 증거로 활용합니다.

## 진단

1. 3단계의 Ingress 헬스 체크 설정을 검토합니다. 헬스 체크가 실패를 보이거나 잘못된 임계값 설정이 있으면 이것이 페일오버 문제의 가장 유력한 원인입니다. 헬스 체크 엔드포인트가 접근 가능하고 실패 임계값이 적절한지 확인합니다.

2. 7단계의 크로스 클러스터 복제 상태를 분석합니다. 복제 지연이 허용 임계값을 초과하면 페일오버 시 데이터 일관성 위험이 존재합니다. 복제가 동기화되어 있으면 보조 클러스터 준비 상태 분석으로 진행합니다.

3. 5단계의 헬스 체크 메트릭에서 실패가 있으면 실패가 주 클러스터(페일오버를 트리거해야 함)인지 보조 클러스터(페일오버 완료를 방해)인지 확인합니다. 주 클러스터가 실패하는데 페일오버가 트리거되지 않으면 자동화 설정을 검토해야 합니다.

4. 9단계의 보조 클러스터 Deployment 상태를 검토합니다. 레플리카 수가 0이거나 Pod가 비정상이면 보조 클러스터가 페일오버 시 트래픽을 수용할 수 없습니다. 보조 클러스터가 준비되었는데도 페일오버가 실패하면 DNS 또는 라우팅 설정이 문제입니다.

5. 6단계의 Ingress 컨트롤러 로그에서 DNS 업데이트 실패가 있으면 DNS 전파 또는 권한이 페일오버 완료를 방해하고 있습니다. 로그에 페일오버 시도가 없으면 페일오버 트리거가 활성화되지 않고 있습니다.

분석이 결론에 이르지 못하면: 8단계의 클러스터 상태 알림을 비교하여 주 클러스터와 보조 클러스터 상태 차이를 확인합니다. 페일오버 트리거 설정을 검토하고 헬스 체크 실패 임계값이 오탐이나 누락을 방지하도록 올바르게 보정되었는지 확인합니다.
