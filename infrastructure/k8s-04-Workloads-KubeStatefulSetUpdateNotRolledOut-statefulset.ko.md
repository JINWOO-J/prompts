---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/KubeStatefulSetUpdateNotRolledOut-statefulset.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- k8s-statefulset
- kubestatefulsetupdatenotrolledout
- performance
- statefulset
- workloads
---

---
title: Kube StatefulSet Update Not RolledOut
weight: 20
---

# StatefulSet 업데이트 미롤아웃 (KubeStatefulSetUpdateNotRolledOut)

## 의미

StatefulSet 업데이트가 롤아웃되지 않은 상태입니다(StatefulSet 업데이트 관련 알림 발생). StatefulSet 업데이트 프로세스가 중단되었거나, 일시 중지되었거나, Pod 스케줄링 실패, 리소스 제약 또는 업데이트 전략 문제로 진행할 수 없기 때문입니다.
StatefulSet의 업데이트 상태가 중단되고, Pod가 Pending 또는 Terminating 상태로 남으며, StatefulSet 이벤트에 FailedCreate, FailedScheduling 또는 FailedAttachVolume 오류가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며 StatefulSet 업데이트가 완료되지 않아 Pod가 오래된 설정으로 실행됨을 나타냅니다. 주로 지속적인 리소스 제약, 볼륨 Zone 불일치 또는 클러스터 용량 제한이 원인이며, PersistentVolumeClaim 바인딩 실패가 업데이트 롤아웃을 차단할 수 있습니다.

## 영향

StatefulSet 업데이트 알림이 발생하며, 서비스 저하 또는 사용 불가가 발생합니다. StatefulSet 업데이트가 중단되고, 이전 Pod가 오래된 설정으로 계속 실행됩니다. 새 Pod를 생성하거나 스케줄링할 수 없으며, StatefulSet 원하는 상태가 불일치합니다. 업데이트 전략이 진행할 수 없고, 시스템 구성 요소가 일관되지 않은 버전으로 실행될 수 있습니다.

## 플레이북

1. namespace <namespace>에서 StatefulSet <statefulset-name>을 describe하여 다음을 확인합니다:
   - 업데이트 상태, 현재 리비전 및 업데이트 리비전
   - 업데이트 전략 설정
   - 업데이트가 롤아웃되지 않는 이유를 보여주는 Condition
   - FailedCreate, FailedScheduling 또는 FailedAttachVolume 오류를 보여주는 Event

2. namespace <namespace>에서 StatefulSet <statefulset-name>의 이벤트를 타임스탬프 순으로 조회하여 업데이트 롤아웃 문제 순서를 확인합니다.

3. namespace <namespace>에서 StatefulSet <statefulset-name>의 롤아웃 상태를 확인하여 업데이트가 진행 중인지 중단되었는지 확인합니다.

4. namespace <namespace>에서 label app=<statefulset-label>로 StatefulSet에 속한 Pod를 조회하고 Pod를 describe하여 Pending 또는 Terminating 상태의 Pod를 식별합니다.

5. namespace <namespace>에서 StatefulSet <statefulset-name> 설정을 조회하고 리소스 요청, Node Selector, Toleration 및 Affinity 규칙을 확인합니다.

6. namespace <namespace>에서 label app=<statefulset-label>로 PersistentVolumeClaim 리소스를 조회하고 PVC를 describe하여 볼륨 가용성을 확인합니다.

## 진단

1. 플레이북의 StatefulSet 이벤트를 분석하여 롤아웃 차단 요인을 파악합니다. "FailedCreate" 이벤트는 PVC 프로비저닝 또는 Pod 생성 문제를 나타냅니다. "FailedScheduling" 이벤트는 Node 리소스 또는 Affinity 제약을 나타냅니다. "FailedAttachVolume" 이벤트는 스토리지 백엔드 문제를 나타냅니다.

2. 이벤트가 PVC 문제를 나타내면(볼륨 관련 메시지가 포함된 FailedCreate), 대기 중인 Pod Ordinal의 PVC 상태를 확인합니다. StatefulSet은 PVC를 순차적으로 생성하고 각 PVC가 바인딩될 때까지 기다린 후 해당 Pod를 생성합니다. StorageClass가 필요한 Zone에서 볼륨을 프로비저닝할 수 있는지 확인합니다.

3. 이벤트가 스케줄링 실패를 나타내면(FailedScheduling, InsufficientCPU, InsufficientMemory), 플레이북의 Node 용량과 연관시킵니다. Pod 리소스 요청이 사용 가능한 Node 용량을 초과하는지 또는 Node Selector/Affinity 규칙이 사용 가능한 모든 Node를 제외하는지 확인합니다.

4. 이벤트가 Pod Readiness 문제를 나타내면(Pod가 생성되었지만 Ready 상태가 되지 않음), 롤아웃을 차단하는 Pod를 분석합니다. StatefulSet은 기본적으로 OrderedReady 업데이트 전략을 사용하므로 단일 비정상 Pod가 전체 롤아웃을 차단합니다. Pod 로그와 Readiness Probe 설정을 확인합니다.

5. 이벤트가 Pod 종료 문제를 나타내면(Pod가 Terminating 상태에 머물러 있음), 삭제를 방해하는 Finalizer 또는 이전 Pod 리비전의 종료를 차단하는 PodDisruptionBudget 제약을 확인합니다.

6. 이벤트가 볼륨 연결 실패를 나타내면(FailedAttachVolume, VolumeNotFound), PersistentVolume이 존재하고 Pod가 스케줄링된 Node에서 접근 가능한지 확인합니다. 스토리지 백엔드 연결과 볼륨 Zone이 Node Zone과 일치하는지 확인합니다.

7. 명확한 이벤트 패턴이 없으면, 플레이북의 StatefulSet 현재 리비전과 업데이트 리비전을 비교합니다. 리비전이 다르면 컨트롤러가 업데이트를 시도하지만 Pod가 전환되지 않는 것입니다. 롤아웃을 의도적으로 보류하는 업데이트 전략의 partition 설정을 확인합니다.
