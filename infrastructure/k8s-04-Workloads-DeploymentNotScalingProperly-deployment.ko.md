---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/DeploymentNotScalingProperly-deployment.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- autoscal
- capacity
- deployment
- deploymentnotscalingproperly
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- scaling
- workloads
---

---
title: Deployment Not Scaling Properly - Deployment
weight: 235
categories:
  - kubernetes
  - deployment
---

# Deployment가 제대로 스케일링되지 않음 (DeploymentNotScalingProperly-deployment)

## 의미

Deployment가 설정, HPA 신호 또는 부하에 따라 예상대로 Replica 수를 변경하지 않는 상태입니다(KubeDeploymentReplicasMismatch 알림 발생 가능). 스케일업 또는 스케일다운이 필요한 조건임에도 불구하고 스케일링이 이루어지지 않습니다. 리소스 제약, HPA 설정 오류, Metrics Server 문제 또는 Pod Readiness 문제로 인해 Replica 수 조정이 실패하는 스케일링 장애를 나타냅니다.

## 영향

Deployment가 원하는 Replica 수로 스케일링할 수 없으며, 애플리케이션의 용량이 부족합니다. 서비스가 과부하될 수 있고, HPA 스케일링이 실패합니다. 애플리케이션이 트래픽 급증을 처리할 수 없으며, KubeDeploymentReplicasMismatch 알림이 발생합니다. Replica 수가 원하는 상태와 불일치하고, Pod 생성이 실패하며, 스케일링 작업이 중단되거나 실패합니다.

## 플레이북

1. namespace <namespace>에서 deployment <deployment-name>을 describe하여 다음을 확인합니다:
   - Replica 상태 (desired/current/ready/available)
   - 스케일링 실패 이유를 보여주는 Condition
   - FailedCreate, FailedScheduling 또는 스케일링 오류를 보여주는 Event

2. namespace <namespace>에서 involved object name <deployment-name>으로 필터링하고 마지막 타임스탬프 순으로 정렬하여 이벤트를 조회하고 스케일링 실패 순서를 확인합니다.

3. HPA를 사용하는 경우 namespace <namespace>에서 horizontal pod autoscaler <hpa-name>을 describe하여 HPA 설정을 확인합니다.

4. 모든 Node를 조회하고 리소스 사용량 메트릭을 확인하여 리소스 제약이 있는지 확인합니다.

5. kube-system namespace에서 label k8s-app=metrics-server로 Pod를 조회하여 Metrics Server 상태를 확인합니다.

6. namespace <namespace>에서 label app=<app-label>로 Pod를 조회하여 Pod 상태와 Readiness를 확인합니다.

7. namespace <namespace>에서 ResourceQuota 객체를 describe하여 Quota가 스케일링을 차단하는지 확인합니다.

## 진단

1. 플레이북 1-2단계의 Deployment 이벤트를 분석하여 주요 스케일링 실패 원인을 파악합니다. "FailedScheduling" 이벤트는 스케줄링 제약을 나타냅니다. "FailedCreate" 이벤트는 Pod 생성 실패를 나타냅니다. "exceeded quota" 이벤트는 리소스 Quota 제한을 나타냅니다. "ScalingReplicaSet" 후 실패 이벤트는 스케일링 작업 문제를 나타냅니다.

2. 이벤트가 스케줄링 실패를 나타내면("Insufficient cpu" 또는 "Insufficient memory"가 포함된 FailedScheduling), 플레이북 4단계의 Node 리소스 메트릭과 연관시켜 클러스터 용량 소진을 확인합니다. 사용 가능한 용량이 있는 Node를 확인하고 Node Selector 또는 Affinity 규칙이 스케줄링 옵션을 제한하는지 검증합니다.

3. 이벤트가 리소스 Quota 문제를 나타내면("exceeded quota" 또는 "forbidden" 메시지 포함), 플레이북 7단계의 Quota 상태를 확인하고 Deployment 리소스 요청과 비교하여 Quota 증가가 필요한지 또는 리소스 요청을 줄여야 하는지 판단합니다.

4. HPA가 설정된 경우, 플레이북 3단계의 HPA 상태를 분석하여 스케일링 결정 문제를 파악합니다. "unable to get metrics" 또는 "failed to compute desired" 메시지가 있으면 Metrics Server 문제를 나타냅니다. 현재 메트릭 값과 목표 임계값을 확인합니다.

5. HPA에서 메트릭 수집 실패가 표시되면, 플레이북 5단계의 Metrics Server Pod 상태를 확인합니다. Metrics Server Pod가 실행되지 않거나 비정상이면 HPA가 스케일링 결정을 내릴 수 없습니다.

6. 이벤트가 Pod Readiness 실패를 나타내면(Pod가 생성되었지만 Ready 상태가 되지 않음), 플레이북 6단계의 Pod 상태를 분석하여 Pod가 Readiness Probe를 통과하지 못하는 이유를 파악합니다. 이는 스케일업 완료를 방해하는 애플리케이션 수준 문제를 나타낼 수 있습니다.

7. 이벤트가 새 Pod의 이미지 Pull 실패를 나타내면, 이미지 가용성과 레지스트리 연결을 확인합니다. 새 Pod 이미지를 Pull할 수 없으면 스케일링을 완료할 수 없습니다.

8. 이벤트가 결정적이지 않지만 스케일링이 발생하지 않으면, Deployment Replica 설정이 예상 값과 일치하는지 확인하고 Deployment가 일시 중지되었거나 HPA/수동 스케일링 설정이 충돌하는지 확인합니다.

**이벤트에서 명확한 실패 원인을 찾을 수 없는 경우**: HPA 이벤트 이력에서 스케일링 결정 패턴을 검토하고, Node Autoscaler가 활성화되어 작동하는지 확인하고, cluster-autoscaler 로그에서 대기 중인 스케일업 결정을 검사하고, PodDisruptionBudget이 스케일다운 작업을 제한하는지 확인하고, API Server의 Rate Limiting이 컨트롤러 작업에 영향을 미치는지 확인합니다.
