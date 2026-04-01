---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/KubeDeploymentReplicasMismatch-deployment.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- deployment
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-service
- kubedeploymentreplicasmismatch
- performance
- workloads
---

---
title: Kube Deployment Replicas Mismatch
weight: 20
---

# Deployment Replica 불일치 (KubeDeploymentReplicasMismatch)

## 의미

Deployment가 예상 Replica 수와 일치하지 않는 상태입니다(KubeDeploymentReplicasMismatch 알림 발생). 현재 Ready Replica 수가 원하는 Replica 수와 일치하지 않아 Pod를 생성, 스케줄링 또는 Ready 상태로 만들 수 없음을 나타냅니다.
kubectl에서 Deployment의 Replica 수가 불일치하며, Pod가 Pending 또는 NotReady 상태로 남고, Deployment 이벤트에 FailedCreate 또는 FailedScheduling 오류가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며 Deployment가 원하는 상태를 달성하지 못하게 하는 스케줄링 제약, 리소스 제한 또는 Pod 상태 문제를 나타냅니다. 주로 클러스터 용량 제한, 리소스 Quota 제약 또는 지속적인 스케줄링 문제가 원인이며, 애플리케이션이 부족한 용량으로 실행되어 오류가 발생할 수 있습니다.

## 영향

KubeDeploymentReplicasMismatch 알림이 발생하며, 서비스 저하 또는 사용 불가가 발생합니다. Deployment가 원하는 Replica 수를 달성할 수 없고, 현재 Replica가 원하는 Replica와 불일치합니다. 애플리케이션이 부족한 용량으로 실행되며, 롤링 업데이트가 차단될 수 있고, Replica 수가 원하는 상태와 일치하지 않습니다.

## 플레이북

1. namespace <namespace>에서 deployment <deployment-name>을 describe하여 다음을 확인합니다:
   - Replica 상태 (desired/current/ready/available)
   - Replica 불일치 이유를 보여주는 Condition
   - FailedCreate, FailedScheduling 또는 ReplicaSetCreateError 오류를 보여주는 Event

2. namespace <namespace>에서 involved object name <deployment-name>으로 필터링하고 마지막 타임스탬프 순으로 정렬하여 이벤트를 조회하고 Replica 불일치 문제 순서를 확인합니다.

3. namespace <namespace>에서 label app=<app-label>로 ReplicaSet 리소스를 조회하고 ReplicaSet 상태 및 Replica 수를 확인하여 Replica 분포를 검증합니다.

4. namespace <namespace>에서 label app=<app-label>로 Pod를 조회하고 pod <pod-name>을 describe하여 Pending, CrashLoopBackOff 또는 NotReady 상태의 Pod를 식별합니다.

5. namespace <namespace>에서 deployment <deployment-name>을 YAML 형식으로 조회하여 Pod 템플릿의 리소스 요청, Node Selector, Toleration 및 Affinity 규칙을 확인합니다.

6. Node를 describe하여 할당된 리소스를 확인하고 추가 Pod 스케줄링을 위한 클러스터 전체 용량 가용성을 검증합니다.

## 진단

1. 플레이북 1-2단계의 Deployment 이벤트를 분석하여 주요 실패 원인을 파악합니다. "FailedScheduling" 이벤트는 리소스 또는 스케줄링 제약을 나타냅니다. "FailedCreate" 이벤트는 ReplicaSet 생성 문제를 나타냅니다. "BackOff" 또는 "CrashLoopBackOff" 이벤트는 Pod 크래시 루프를 나타냅니다. "Unhealthy" 또는 "FailedReadiness" 이벤트는 Readiness Probe 실패를 나타냅니다.

2. 이벤트가 스케줄링 실패를 나타내면("Insufficient cpu" 또는 "Insufficient memory" 메시지가 포함된 FailedScheduling), 플레이북 4단계의 Pod Pending 타임스탬프와 플레이북 6단계의 Node 용량 데이터를 연관시켜 리소스 소진이 근본 원인임을 확인합니다. 어떤 리소스(CPU, 메모리 또는 둘 다)가 어떤 Node에서 제약되는지 확인합니다.

3. 이벤트가 리소스 Quota 문제를 나타내면("exceeded quota" 또는 "forbidden: exceeded quota" 메시지 포함), namespace 리소스 Quota에서 Quota 상태를 확인하고 플레이북 5단계의 Deployment 리소스 요청과 비교하여 Quota가 차단 요인임을 확인합니다.

4. 이벤트가 Pod 크래시를 나타내면(CrashLoopBackOff, Error 또는 OOMKilled), 플레이북 4단계의 Pod describe 출력을 분석하여 컨테이너 종료 코드와 종료 사유를 파악합니다. 종료 코드 137은 OOMKilled를 나타내고, 종료 코드 1은 애플리케이션 오류를 나타냅니다.

5. 이벤트가 이미지 Pull 실패를 나타내면(ErrImagePull, ImagePullBackOff), 플레이북 5단계의 Deployment 스펙에서 이미지 이름과 태그를 확인하고 레지스트리 연결 또는 인증 문제를 확인합니다.

6. 이벤트가 Readiness Probe 실패를 나타내면, 플레이북 4단계의 Pod Condition과 Probe 설정을 분석하여 Replica가 Ready 상태가 되지 못하게 하는 애플리케이션 수준 문제를 파악합니다.

7. 이벤트가 Node Affinity 또는 Taint 문제를 나타내면("didn't match node selector" 또는 "node(s) had taints" 메시지 포함), 플레이북 5단계의 Deployment Toleration 및 Affinity 규칙과 플레이북 6단계의 사용 가능한 Node Label 및 Taint를 비교합니다.

8. 이벤트가 결정적이지 않거나 일반적인 오류만 표시하면, 플레이북 3단계의 ReplicaSet 상태를 비교하여 Generation 간 Replica 분포를 확인하고 불일치가 중단된 롤아웃 때문인지 스케일링 실패 때문인지 식별합니다.

**이벤트에서 명확한 실패 원인을 찾을 수 없는 경우**: Deployment 수정 이력을 검토하여 최근 변경을 식별하고, 자동 스케일링이 설정된 경우 HPA 충돌을 확인하고, PodDisruptionBudget이 스케일링을 차단하지 않는지 확인하고, 과거 Deployment 패턴을 검사합니다. Replica 불일치는 누적 리소스 압박 또는 간헐적 스케줄링 제약으로 인해 발생할 수 있습니다.
