---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/04-Cost-Optimization/Right-sizing-Analysis-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- analysis
- cost
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- kubernetes
- monitoring
- optimization
- performance
- right
- sizing
- storage
- sts
---

# Right-sizing Analysis (적정 규모 분석)

## 의미

적정 규모 분석 알림은 Kubernetes 리소스가 실제 사용률 대비 과다 프로비저닝되거나 과소 프로비저닝되어 비용 비효율이나 성능 문제를 유발하는 상황(OverProvisionedResource 또는 UnderProvisionedResource 같은 알림 발생)을 나타냅니다. Pod의 CPU/메모리 할당이 사용률 초과, Deployment의 리소스 요청이 워크로드 요구와 불일치, PVC의 스토리지 할당이 실제 사용량 초과, 또는 리소스 메트릭의 지속적인 과다/과소 사용 패턴 등이 원인입니다.
 리소스가 할당 대비 현저히 낮거나 높은 사용률 메트릭을 보이고, 비용 메트릭이 과다 프로비저닝을 나타내며, 성능 메트릭이 과소 프로비저닝을 나타내고, 리소스 할당이 워크로드 요구와 일치하지 않습니다. 이는 비용 관리 계층과 리소스 최적화에 영향을 미치며, 주로 초기 과다 프로비저닝, 워크로드 변경, 또는 사용률 모니터링 부재가 원인입니다. 리소스가 컨테이너 워크로드인 경우, 컨테이너 리소스 요청이 불일치하고 애플리케이션이 비용 비효율이나 성능 제약을 겪을 수 있습니다.

## 영향

OverProvisionedResource 알림 발생, UnderProvisionedResource 알림 발생, 과다 프로비저닝으로 불필요한 비용 누적, 과소 프로비저닝으로 성능 문제 발생, 리소스 할당이 워크로드 요구와 불일치, 비용 최적화 기회 미활용. 사용률 메트릭이 상당한 할당 불일치를 보입니다. 리소스가 컨테이너 워크로드인 경우, 컨테이너 리소스 요청이 불일치하고, Pod 리소스 제한이 부적절하며, 컨테이너 애플리케이션이 비용 비효율이나 성능 제약을 겪을 수 있습니다. 애플리케이션이 비용 낭비나 성능 저하를 경험할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 Pod <pod-name>을 describe하여 적정 규모 분석을 위한 Pod 리소스 요청, 제한, 현재 리소스 소비를 점검합니다.
2. namespace <namespace>에서 최근 이벤트를 타임스탬프 순으로 조회하여 리소스 제약, OOMKilled, CPU 스로틀링 관련 이벤트를 확인합니다.
3. namespace <namespace>에서 Pod를 조회하고 적정 규모 분석을 위한 리소스 사양을 확인합니다.
4. CPU 사용률과 메모리 사용률의 Prometheus 메트릭을 최근 30일 동안 조회하여 Pod 리소스 요청 및 제한과 비교합니다.
5. namespace <namespace>에서 PVC <pvc-name>을 describe하여 스토리지 적정 규모를 위한 스토리지 할당과 실제 사용량을 비교합니다.
6. 리소스 요청 사양과 실제 사용률 메트릭을 최근 30일 동안 비교하여 요청이 사용률을 크게 초과하거나 미달하는지 확인하고, Prometheus 메트릭을 보조 증거로 활용합니다.
7. namespace <namespace>의 리소스 쿼터 사용량을 조회하고 리소스 사용률 메트릭과 비교하여 비용-사용률 불일치를 식별합니다.
8. namespace <namespace>에서 HPA <hpa-name>을 describe하여 HPA 리소스 목표 사용률 설정이 실제 사용 패턴과 일치하는지 확인합니다.

## 진단

1. 1단계, 3단계, 4단계의 Pod 리소스 소비를 검토합니다. Pod가 지속적으로 요청된 CPU/메모리의 30% 미만을 사용하면 과다 프로비저닝되어 적정 규모 조정 대상입니다. Pod가 빈번하게 스로틀링되거나 OOMKilled되면 과소 프로비저닝입니다.

2. 4단계의 30일 사용률 메트릭을 분석합니다. 사용률이 지속적으로 낮으면 리소스 요청을 줄입니다. 사용률이 간헐적 급증을 보이면 현재 요청을 유지하되 오토스케일링을 고려합니다.

3. 5단계의 PVC 점검에서 스토리지 할당이 사용량을 크게 초과하면 스토리지 적정 규모 기회가 존재합니다. 더 작은 스토리지 클래스나 데이터 정리를 고려합니다.

4. 7단계의 리소스 쿼터 비교를 검토합니다. 쿼터 사용이 높지만 개별 Pod 사용률이 낮으면 많은 과다 프로비저닝된 Pod가 불필요하게 쿼터를 소비하고 있습니다.

5. 8단계의 HPA 설정에서 목표 사용률이 실제 패턴과 맞지 않으면 워크로드 특성에 더 잘 맞도록 오토스케일러 설정을 조정해야 할 수 있습니다.

분석이 결론에 이르지 못하면: 2단계의 이벤트에서 과소 프로비저닝을 나타내는 OOMKilled나 CPU 스로틀링 이벤트를 확인합니다. 6단계의 사용률 비교를 검토하여 할당-사용률 격차가 가장 큰 Pod를 식별합니다. 비용 영향 기준으로 적정 규모 조정 우선순위를 정합니다(낮은 사용률의 대규모 리소스 우선).
