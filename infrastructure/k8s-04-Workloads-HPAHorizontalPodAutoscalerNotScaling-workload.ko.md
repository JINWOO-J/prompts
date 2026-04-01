---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/HPAHorizontalPodAutoscalerNotScaling-workload.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- autoscal
- hpahorizontalpodautoscalernotscaling
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
title: HPA Horizontal Pod Autoscaler Not Scaling - Workload
weight: 215
categories:
  - kubernetes
  - workload
---

# HPA가 스케일링하지 않음 (HPAHorizontalPodAutoscalerNotScaling-workload)

## 의미

HPA(Horizontal Pod Autoscaler)가 예상대로 Pod를 스케일링하지 않는 상태입니다(KubeHPAReplicasMismatch 또는 KubeDeploymentReplicasMismatch 알림 발생).
metrics-server에서 CPU 또는 메모리 Metrics를 사용할 수 없거나, Deployment Pod 템플릿에 리소스 요청이 정의되지 않았거나, kube-system namespace의 metrics-server Pod가 작동하지 않거나, HPA의 min 또는 max Replica 설정이 잘못되었거나, HPA 목표 사용률 임계값이 잘못 설정되었기 때문입니다. HPA에 Metrics 사용 불가 Condition이 표시되고, kube-system namespace의 metrics-server Pod에 장애가 표시될 수 있으며, HPA 상태에 스케일링 문제가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며 자동 스케일링을 방해합니다. 주로 metrics-server 장애 또는 리소스 요청 누락이 원인이며, 애플리케이션이 트래픽 급증을 처리할 수 없어 오류가 발생할 수 있습니다.

## 영향

높은 부하 시 CPU 또는 메모리가 목표 사용률을 초과해도 Pod가 스케일업되지 않으며, 낮은 부하 시 리소스가 과소 사용되어도 Pod가 스케일다운되지 않습니다. 애플리케이션이 트래픽 급증을 처리할 수 없고, 낮은 사용률 시 리소스가 낭비됩니다. Deployment가 고정된 Replica 수를 유지하며, HPA 상태에 스케일링 문제와 Metrics 사용 불가 또는 스케일링 비활성화 Condition이 표시됩니다. KubeHPAReplicasMismatch 및 KubeDeploymentReplicasMismatch 알림이 발생하고, 부하 시 애플리케이션 성능이 저하되며, 수동 스케일링이 필요합니다.

## 플레이북

1. namespace <namespace>에서 HPA <hpa-name>을 describe하여 다음을 확인합니다:
   - 현재 Metrics 대비 목표 Metrics
   - 원하는 Replica 수 대비 현재 Replica 수
   - Min/Max Replica 설정
   - 스케일링이 작동하지 않는 이유를 보여주는 Condition
   - FailedGetObjectMetric, FailedComputeMetricsReplicas 또는 기타 오류를 보여주는 Event

2. namespace <namespace>에서 HPA <hpa-name>의 이벤트를 타임스탬프 순으로 조회하여 스케일링 실패 순서를 확인합니다.

3. namespace <namespace>에서 deployment <deployment-name>을 describe하여 리소스 요청이 정의되어 있는지 확인합니다. HPA가 작동하려면 리소스 Metrics가 필요합니다.

4. kube-system namespace에서 label k8s-app=metrics-server로 Pod를 조회하고 metrics-server 로그를 확인하여 실행 중이고 정상인지 검증합니다.

5. namespace <namespace>에서 deployment <deployment-name> 설정을 조회하고 리소스 요청 및 제한을 검토하여 HPA 스케일링에 적절히 설정되었는지 확인합니다.

6. namespace <namespace>에서 HPA <hpa-name> 상태 및 설정을 조회하여 Metrics가 수집되고 있는지, 스케일링 결정이 이루어지고 있는지 확인합니다.

## 진단

1. 플레이북의 HPA 이벤트를 분석하여 스케일링 실패 원인을 파악합니다. 이벤트에 FailedGetObjectMetric, FailedComputeMetricsReplicas, "ScalingDisabled" 또는 Metrics 사용 불가 Condition이 표시되면, 이벤트 타임스탬프와 오류 메시지를 사용하여 구체적인 문제를 식별합니다.

2. 이벤트가 Metrics 사용 불가를 나타내면, 플레이북 4단계의 metrics-server 상태를 확인합니다. 스케일링이 중단된 시점에 metrics-server 이벤트에 장애, 재시작 또는 사용 불가가 표시되면 metrics-server가 근본 원인입니다.

3. 이벤트가 리소스 요청 누락을 나타내면, 플레이북 3단계의 Deployment 설정을 검사합니다. Deployment에 CPU 또는 메모리 리소스 요청이 없으면 HPA Metrics 계산을 활성화하기 위해 리소스 요청을 추가합니다.

4. 이벤트가 HPA 설정 문제를 나타내면, 플레이북 6단계의 HPA 설정을 확인합니다. min/max Replica가 동일하거나 목표 Metrics가 잘못 설정되었으면 스케일링을 활성화하도록 HPA 설정을 조정합니다.

5. 이벤트가 스케일업을 방해하는 리소스 제약을 나타내면, 클러스터 용량과 Quota를 확인합니다. 스케일링 이벤트에 스케줄링 실패 또는 Quota 소진이 표시되면 HPA 설정 오류가 아닌 용량 제약이 스케일링을 차단하는 것입니다.

6. 이벤트가 최근 Deployment 변경을 나타내면, Deployment 롤아웃 타임스탬프와 스케일링 실패를 연관시킵니다. 스케일링이 중단되기 전에 Deployment 이벤트가 발생했다면 새 Deployment 설정이 HPA 동작에 영향을 미쳤을 수 있습니다.

7. 이벤트가 스케일다운 차단을 나타내면, PodDisruptionBudget과 Deployment 전략을 확인합니다. PDB 또는 최소 가용성 제약이 Pod 종료를 방해하면 스케일다운을 진행할 수 없습니다.

**상관관계를 찾을 수 없는 경우**: 검색 범위를 확장하고(5분→10분, 30분→1시간, 1시간→2시간), metrics-server 로그에서 점진적 성능 저하를 검토하고, 간헐적 Metrics 수집 실패를 확인하고, HPA가 항상 잘못 설정되었지만 최근에야 적용되었는지 검사하고, 리소스 Quota 제약이 시간이 지남에 따라 발생했는지 확인하고, 스케일링을 방해한 누적 리소스 압박을 확인합니다. HPA 스케일링 실패는 즉각적인 설정 변경이 아닌 점진적 Metrics 또는 인프라 문제로 인해 발생할 수 있습니다.
