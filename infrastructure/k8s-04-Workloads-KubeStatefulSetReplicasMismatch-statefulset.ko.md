---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/KubeStatefulSetReplicasMismatch-statefulset.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- k8s-statefulset
- kubestatefulsetreplicasmismatch
- performance
- scaling
- statefulset
- sts
- workloads
---

---
title: Kube StatefulSet Replicas Mismatch
weight: 20
---

# StatefulSet Replica 불일치 (KubeStatefulSetReplicasMismatch)

## 의미

StatefulSet이 예상 Replica 수와 일치하지 않는 상태입니다(KubeStatefulSetReplicasMismatch 알림 발생). 현재 Ready Replica 수가 원하는 Replica 수와 일치하지 않아 Pod를 생성, 스케줄링 또는 Ready 상태로 만들 수 없음을 나타냅니다.
kubectl에서 StatefulSet의 Replica 수가 불일치하며, Pod가 Pending, CrashLoopBackOff 또는 NotReady 상태로 남고, StatefulSet 이벤트에 FailedCreate, FailedScheduling 또는 FailedAttachVolume 오류가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며 StatefulSet이 원하는 상태를 달성하지 못하게 하는 스케줄링 제약, 리소스 제한, Pod 상태 문제 또는 Persistent Volume 문제를 나타냅니다. 주로 클러스터 용량 제한, 볼륨 Zone 제약 또는 지속적인 스케줄링 문제가 원인이며, PersistentVolumeClaim 바인딩 실패가 Pod 생성을 차단할 수 있습니다.

## 영향

KubeStatefulSetReplicasMismatch 알림이 발생하며, 서비스 저하 또는 사용 불가가 발생합니다. StatefulSet이 원하는 Replica 수를 달성할 수 없고, 현재 Replica가 원하는 Replica와 불일치합니다. 애플리케이션이 부족한 용량으로 실행되며, Stateful 워크로드가 Quorum을 잃을 수 있습니다. 데이터 일관성이 영향받을 수 있고, Persistent Volume 문제가 StatefulSet 스케일링을 차단합니다.

## 플레이북

1. namespace <namespace>에서 StatefulSet <statefulset-name>을 describe하여 다음을 확인합니다:
   - Replica 상태 (desired/current/ready)
   - 리소스 요청을 포함한 Pod 템플릿 설정
   - Replica 불일치 이유를 보여주는 Condition
   - FailedCreate, FailedScheduling 또는 FailedAttachVolume 오류를 보여주는 Event

2. namespace <namespace>에서 StatefulSet <statefulset-name>의 이벤트를 타임스탬프 순으로 조회하여 Replica 불일치 문제 순서를 확인합니다.

3. namespace <namespace>에서 label app=<statefulset-label>로 StatefulSet에 속한 Pod를 조회하고 Pod를 describe하여 Pending, CrashLoopBackOff 또는 NotReady 상태의 Pod를 식별합니다.

4. namespace <namespace>에서 label app=<statefulset-label>로 PersistentVolumeClaim 리소스를 조회하고 PVC를 describe하여 볼륨 바인딩 및 가용성을 확인합니다.

5. namespace <namespace>에서 StatefulSet <statefulset-name> 설정을 조회하고 리소스 요청, Node Selector, Toleration 및 Affinity 규칙을 확인합니다.

6. Node를 describe하고 할당된 리소스를 확인하여 추가 Pod 스케줄링을 위한 클러스터 전체 가용성을 검증합니다.

## 진단

1. 플레이북의 StatefulSet 이벤트를 분석하여 Replica 생성 차단 요인을 파악합니다. "FailedCreate" 이벤트는 PVC 또는 Pod 생성 문제를 나타냅니다. "FailedScheduling" 이벤트는 리소스 또는 배치 제약을 나타냅니다. "FailedAttachVolume" 이벤트는 Pod 시작을 방해하는 스토리지 문제를 나타냅니다.

2. 이벤트가 PVC 바인딩 문제를 나타내면(Pending PVC, ProvisioningFailed), 각 Pod Ordinal의 PVC 상태를 확인합니다. StatefulSet은 Pod를 순차적으로 생성하므로 단일 PVC 바인딩 실패가 해당 Pod와 모든 후속 Pod의 생성을 차단합니다. StorageClass Provisioner 가용성과 Zone 제약을 확인합니다.

3. 이벤트가 스케줄링 실패를 나타내면(InsufficientCPU, InsufficientMemory, NodeAffinity), 플레이북의 Pod 리소스 요청과 사용 가능한 Node 용량을 비교합니다. Node Selector 또는 Anti-Affinity 규칙이 현재 클러스터 상태에 비해 너무 제한적인지 확인합니다.

4. Pod가 존재하지만 Ready 상태가 아니면(CrashLoopBackOff, Error 또는 Readiness Probe 실패), Replica 수에 현재 Pod가 표시되지만 Ready 수가 더 낮습니다. Pod 로그와 컨테이너 종료 코드를 분석하여 Readiness를 방해하는 애플리케이션 수준 실패를 파악합니다.

5. 이벤트가 볼륨 연결 실패를 나타내면, StatefulSet의 volumeClaimTemplates가 스케줄링 가능한 Node가 있는 Zone에서 볼륨을 프로비저닝할 수 있는 StorageClass를 지정하는지 확인합니다. PV와 Node 간의 Zone 불일치는 영구적인 스케줄링 실패를 유발합니다.

6. 일부 Replica가 실행 중이지만 원하는 것보다 적으면, 누락되거나 실패하는 Pod Ordinal을 식별합니다. StatefulSet은 순서대로(0, 1, 2...) Pod를 생성하므로 가장 낮은 누락 Ordinal이 실패가 발생한 위치를 나타냅니다. 해당 특정 Pod의 이벤트와 상태를 확인합니다.

7. 명확한 이벤트 패턴이 없으면, StatefulSet의 podManagementPolicy를 확인합니다. OrderedReady 정책(기본값)에서는 비정상 Pod가 더 높은 Ordinal Pod의 생성을 차단합니다. Parallel 정책에서는 모든 Pod가 동시에 생성되지만 각각 PVC가 먼저 바인딩되어야 합니다.
