---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/04-Cost-Optimization/Spot-Instance-Management-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- capacity
- cost
- infrastructure
- instance
- k8s-namespace
- k8s-node
- k8s-pod
- kubernetes
- management
- optimization
- spot
- sts
---

# Spot Instance Management (Spot 인스턴스 관리)

## 의미

Spot 인스턴스 관리 알림은 Spot 노드 중단이 빈번하거나, Spot 노드 용량이 미가용하거나, Spot 노드 사용이 최적화되지 않은 상황(SpotNodeInterrupted 또는 SpotNodeCapacityUnavailable 같은 알림 발생)을 나타냅니다. Spot 노드 중단율이 임계값 초과, Spot 노드 용량 요청 실패, Spot 노드 종료 알림 빈번, Spot 노드 가격 변동으로 인한 중단, 또는 Spot 노드 할당 전략 비최적 등이 원인입니다.
 Spot 노드 중단 메트릭이 높은 비율을 보이고, Spot 노드 용량 요청이 실패를 보이며, Spot 노드 종료 알림이 빈번하고, Spot 노드 가격 메트릭이 변동성을 나타냅니다. 이는 비용 관리 계층과 Spot 노드 수명주기 관리에 영향을 미치며, 주로 Spot 노드 용량 제약, Spot 노드 가격 변동성, Spot 노드 중단 처리 실패, 또는 Spot 노드 할당 전략 설정 오류가 원인입니다. Spot 노드가 컨테이너 워크로드를 호스팅하는 경우, 컨테이너 워크로드가 중단되고 애플리케이션이 가용성 문제를 겪을 수 있습니다.

## 영향

SpotNodeInterrupted 알림 발생, SpotNodeCapacityUnavailable 알림 발생, Spot 노드 중단으로 워크로드 중단 발생, Spot 노드 용량 미가용, Spot 노드 종료 알림 빈번, Spot 노드를 통한 비용 최적화 미달성. Spot 노드 중단 메트릭이 높은 비율을 보입니다. Spot 노드가 컨테이너 워크로드를 호스팅하는 경우, 컨테이너 워크로드가 중단되고, Pod 축출이 빈번하게 발생하며, 컨테이너 애플리케이션이 가용성 문제를 겪을 수 있습니다. 애플리케이션이 워크로드 중단이나 Spot 노드 중단 실패를 경험할 수 있습니다.

## 플레이북

1. label node.kubernetes.io/instance-type=spot인 노드를 wide 출력으로 조회하여 클러스터의 모든 Spot 노드와 상태, 용량, 조건을 확인합니다.
2. 모든 namespace에서 최근 이벤트를 타임스탬프 순으로 조회하고 spot, preempt, interrupt 패턴으로 필터링하여 Spot 노드 중단, 선점 경고, 종료 알림을 확인합니다.
3. 노드 <spot-node-name>을 describe하여 조건, 할당 가능 리소스, 종료 알림을 포함한 Spot 노드 세부 정보를 점검합니다.
4. Spot 노드의 Prometheus 메트릭(spot_node_interruption_rate, spot_node_termination_count)을 최근 7일 동안 조회하여 중단 패턴을 식별합니다.
5. 노드 모니터링 Pod의 로그를 조회하고 최근 7일 내 중단 패턴이나 종료 알림을 필터링합니다.
6. 가용 영역 <az>의 노드 유형 <node-type>에 대한 Spot 노드 가격 이력을 최근 7일 동안 조회하여 가격 변동성 패턴을 식별합니다.
7. 클러스터의 Spot 노드 요청을 조회하고 이행 상태와 용량 가용성을 포함한 요청 상태를 확인하여 용량 제약을 식별합니다.
8. 노드 그룹 <node-group-name>의 Spot 노드 설정을 조회하고 Spot 노드 할당 전략과 중단 처리 설정을 점검하여 Spot 노드 관리 설정을 확인합니다.
9. Spot 노드 중단 타임스탬프와 Spot 노드 가격 변경 타임스탬프를 5분 이내로 비교하여 중단이 가격 인상과 상관관계가 있는지 확인하고, Spot 노드 가격 이력을 보조 증거로 활용합니다.

## 진단

1. 4단계의 Spot 노드 중단 메트릭을 검토합니다. 중단율이 높으면 3단계의 노드 세부 정보를 기반으로 중단이 특정 노드 유형이나 가용 영역과 상관관계가 있는지 확인합니다.

2. 6단계의 Spot 가격 이력을 분석합니다. 가격이 높은 변동성을 보이거나 온디맨드 가격을 빈번히 초과하면 가격 기반 중단이 발생하고 있습니다. 노드 유형이나 가용 영역 다양화를 고려합니다.

3. 5단계의 노드 모니터링 로그에서 성공적인 워크로드 마이그레이션 없이 종료 알림이 있으면 중단 처리 자동화가 실패하고 있습니다. 워크로드가 성공적으로 마이그레이션되면 영향은 가용성 문제가 아닌 운영 노이즈입니다.

4. 7단계의 Spot 노드 용량 요청을 검토합니다. 용량 미가용으로 요청이 실패하면 대체 노드 유형이나 온디맨드 폴백이 필요할 수 있습니다. 용량이 가용하지만 사용되지 않으면 할당 전략을 검토해야 합니다.

5. 8단계의 노드 그룹 설정에서 비최적 할당 전략(예: 단일 노드 유형, 단일 AZ)이 있으면 다양화가 중단 빈도를 줄일 수 있습니다.

분석이 결론에 이르지 못하면: 2단계의 이벤트에서 Spot 중단 패턴과 워크로드 영향을 확인합니다. 중단이 특정 워크로드에 불균형적으로 영향을 미치는지(워크로드 배치 문제 시사) 또는 모든 워크로드에 동일하게 영향을 미치는지(클러스터 전체 Spot 설정 문제 시사) 판단합니다. 중단 처리 자동화가 워크로드를 정상적으로 마이그레이션하도록 올바르게 설정되었는지 확인합니다.
