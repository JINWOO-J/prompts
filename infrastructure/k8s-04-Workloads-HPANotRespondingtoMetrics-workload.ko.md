---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/HPANotRespondingtoMetrics-workload.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- autoscal
- compute
- hpanotrespondingtometrics
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- kubernetes
- performance
- scaling
- sts
- workload
- workloads
---

---
title: HPA Not Responding to Metrics - Workload
weight: 250
categories:
  - kubernetes
  - workload
---

# HPA가 Metrics에 응답하지 않음 (HPANotRespondingtoMetrics-workload)

## 의미

HPA(Horizontal Pod Autoscaler)가 리소스 Metrics에 응답하지 않는 상태입니다(KubeHPAReplicasMismatch 또는 KubeDeploymentReplicasMismatch 알림 발생).
kube-system namespace의 metrics-server Pod가 사용 불가능하거나, metrics.k8s.io/v1beta1 API에서 리소스 Metrics를 조회할 수 없거나, Deployment Pod 템플릿에 CPU 또는 메모리 리소스 요청이 정의되지 않았거나, 네트워크 또는 인증 문제로 Metrics API에 접근할 수 없기 때문입니다. HPA에 Metrics 사용 불가 Condition이 표시되고, kube-system namespace의 metrics-server Pod에 장애가 표시되며, HPA 상태에 FailedGetObjectMetric 또는 FailedComputeMetricsReplicas 오류가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며 자동 스케일링을 방해합니다. 주로 metrics-server 장애 또는 리소스 요청 누락이 원인이며, 애플리케이션이 부하 변화에 적응할 수 없어 오류가 발생할 수 있습니다.

## 영향

HPA가 CPU 또는 메모리 Metrics를 기반으로 Pod를 스케일링할 수 없으며, 리소스 사용률에 관계없이 Deployment가 고정된 Replica 수를 유지합니다. 자동 스케일링이 비활성화되고, 애플리케이션이 부하 변화에 적응할 수 없습니다. CPU 또는 메모리 사용량이 임계값을 초과해도 Pod가 현재 Replica 수를 유지합니다. HPA 상태에 Metrics 사용 불가 Condition이 표시되고, KubeHPAReplicasMismatch 및 KubeDeploymentReplicasMismatch 알림이 발생합니다. 스케일링을 위해 수동 개입이 필요하며, 리소스 기반 자동 스케일링이 실패합니다.

## 플레이북

1. namespace <namespace>에서 HPA <hpa-name>을 describe하여 다음을 확인합니다:
   - 현재 Metrics 대비 목표 Metrics
   - 원하는 Replica 수 대비 현재 Replica 수
   - Metrics가 사용 불가능한 이유를 보여주는 Condition
   - FailedGetObjectMetric, FailedComputeMetricsReplicas 또는 Metrics 오류를 보여주는 Event

2. namespace <namespace>에서 HPA <hpa-name>의 이벤트를 타임스탬프 순으로 조회하여 Metrics 실패 순서를 확인합니다.

3. kube-system namespace에서 label k8s-app=metrics-server로 Pod를 조회하고 metrics-server 로그를 확인하여 실행 중이고 정상 작동하는지 검증합니다.

4. namespace <namespace>에서 deployment <deployment-name>을 describe하여 리소스 요청이 정의되어 있는지 확인합니다. HPA가 Metrics를 계산하려면 리소스 요청이 필요합니다.

5. namespace <namespace>에서 Pod 리소스 사용량 Metrics를 조회하여 Metrics가 수집되고 있는지 테스트하고 Metrics API 접근성을 확인합니다.

6. kube-system namespace에서 metrics-server Service 및 Endpoint를 확인하여 Metrics 조회를 위한 네트워크 연결 및 API 접근성을 검증합니다.

## 진단

1. 플레이북의 HPA 이벤트를 분석하여 Metrics 관련 오류를 파악합니다. 이벤트에 FailedGetObjectMetric, FailedComputeMetricsReplicas 또는 "unable to get metrics" 오류가 표시되면, 이벤트 타임스탬프를 사용하여 Metrics가 사용 불가능해진 시점을 확인합니다.

2. 이벤트가 metrics-server 문제를 나타내면, 플레이북 3단계의 metrics-server Pod 상태를 확인합니다. HPA가 응답을 중단한 시점에 metrics-server 이벤트에 CrashLoopBackOff, 재시작 또는 장애가 표시되면 metrics-server가 근본 원인입니다.

3. 이벤트가 리소스 요청 누락을 나타내면, 플레이북 4단계의 Deployment 설정을 검사합니다. Deployment에 CPU 또는 메모리 리소스 요청이 없으면 HPA가 사용률을 계산할 수 없어 Metrics가 사용 불가능하게 표시됩니다.

4. 이벤트가 Metrics API 접근성 문제를 나타내면, 플레이북 5단계의 Metrics API 가용성을 확인합니다. Metrics API 요청이 실패하거나 오류를 반환하면 metrics-server Service 및 Endpoint 연결을 조사합니다.

5. 이벤트가 Service 또는 Endpoint 변경을 나타내면, 플레이북 6단계의 metrics-server Service를 확인합니다. Metrics가 사용 불가능해진 시점에 Service 이벤트에 수정이 표시되면 Service 설정 변경이 Metrics 가용성에 영향을 미친 것입니다.

6. 이벤트가 NetworkPolicy 변경을 나타내면, 정책이 metrics-server 통신에 영향을 미치는지 확인합니다. Metrics 실패 전에 NetworkPolicy 이벤트가 발생했다면 정책 변경이 Metrics 수집을 차단했을 수 있습니다.

7. 이벤트가 metrics-server 리소스 압박을 나타내면, metrics-server Pod 리소스 사용량을 확인합니다. 실패 시점에 리소스 관련 이벤트에 스로틀링 또는 OOMKilled가 표시되면 metrics-server 리소스 제약이 Metrics 수집을 방해한 것입니다.

**상관관계를 찾을 수 없는 경우**: 검색 범위를 확장하고(5분→10분, 30분→1시간, 1시간→2시간), metrics-server 로그에서 점진적 성능 저하를 검토하고, 간헐적 네트워크 연결 문제를 확인하고, Metrics API 인증 또는 권한 문제가 시간이 지남에 따라 발생했는지 검사하고, metrics-server 리소스 제약이 점진적으로 누적되었는지 확인하고, metrics-server 접근성에 영향을 미치는 DNS 또는 서비스 디스커버리 문제를 확인합니다. Metrics 사용 불가는 즉각적인 변경이 아닌 점진적 인프라 저하로 인해 발생할 수 있습니다.
