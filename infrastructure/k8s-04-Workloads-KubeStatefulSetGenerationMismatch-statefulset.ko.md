---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/KubeStatefulSetGenerationMismatch-statefulset.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- k8s-statefulset
- kubestatefulsetgenerationmismatch
- performance
- statefulset
- sts
- workloads
---

---
title: Kube StatefulSet Generation Mismatch
weight: 20
---

# StatefulSet Generation 불일치 (KubeStatefulSetGenerationMismatch)

## 의미

롤백 또는 실패한 업데이트로 인한 StatefulSet Generation 불일치 상태입니다(StatefulSet Generation 관련 알림 발생). 관찰된 Generation이 원하는 Generation과 일치하지 않아 StatefulSet 업데이트 또는 롤백 작업이 성공적으로 완료되지 않았음을 나타냅니다.
kubectl에서 StatefulSet의 Generation이 불일치하며, StatefulSet 이벤트에 Failed, ProgressDeadlineExceeded 또는 PodCreateError 오류가 표시되고, Pod가 실패 또는 오류 상태를 보일 수 있습니다. 이는 워크로드 플레인에 영향을 미치며 StatefulSet 조정 실패 또는 업데이트 문제를 나타냅니다. 주로 지속적인 리소스 제약, 볼륨 Zone 문제 또는 클러스터 용량 제한이 원인이며, PersistentVolumeClaim 바인딩 실패가 Generation 업데이트를 방해할 수 있습니다.

## 영향

KubeStatefulSetGenerationMismatch 알림이 발생하며, 서비스 저하 또는 사용 불가가 발생합니다. StatefulSet이 원하는 상태를 달성할 수 없고, Generation 불일치가 적절한 조정을 방해합니다. StatefulSet 업데이트 또는 롤백이 중단되며, StatefulSet 상태에 Generation 불일치가 표시됩니다. 컨트롤러가 StatefulSet 상태를 조정할 수 없고, StatefulSet 조정 작업이 실패합니다.

## 플레이북

1. namespace <namespace>에서 StatefulSet <statefulset-name>을 describe하여 다음을 확인합니다:
   - 관찰된 Generation 대비 원하는 Generation
   - Replica 상태 (desired/current/ready)
   - 업데이트 전략 설정
   - Generation 불일치가 존재하는 이유를 보여주는 Condition
   - Failed, ProgressDeadlineExceeded 또는 PodCreateError 오류를 보여주는 Event

2. namespace <namespace>에서 StatefulSet <statefulset-name>의 이벤트를 타임스탬프 순으로 조회하여 Generation 불일치 문제 순서를 확인합니다.

3. namespace <namespace>에서 StatefulSet <statefulset-name>의 롤아웃 이력을 조회하여 불일치를 유발했을 수 있는 최근 업데이트 또는 롤백을 확인합니다.

4. namespace <namespace>에서 label app=<statefulset-label>로 StatefulSet에 속한 Pod를 조회하고 Pod를 describe하여 실패 또는 오류 상태의 Pod를 식별합니다.

5. namespace <namespace>에서 label app=<statefulset-label>로 PersistentVolumeClaim 리소스를 조회하고 PVC를 describe하여 볼륨 바인딩 및 가용성을 확인합니다.

6. namespace <namespace>에서 StatefulSet <statefulset-name> 설정을 조회하고 업데이트 전략을 확인하여 업데이트 차단 요인을 파악합니다.

## 진단

1. 플레이북의 StatefulSet 이벤트를 분석하여 컨트롤러가 원하는 Generation으로 조정할 수 없는 이유를 파악합니다. "FailedCreate" 또는 "FailedScheduling" 이벤트는 컨트롤러가 Pod를 업데이트하려 하지만 차단 요인을 만나고 있음을 나타냅니다. "ProgressDeadlineExceeded" 이벤트는 업데이트가 허용 시간을 초과하여 중단되었음을 나타냅니다.

2. 이벤트가 Pod 생성 실패를 나타내면(FailedCreate, PodCreateError), 컨트롤러가 업데이트된 Generation을 위한 새 Pod를 생성할 수 없는 것입니다. PVC 바인딩 상태와 namespace의 리소스 Quota 가용성을 확인합니다. StatefulSet은 Pod 생성 전에 성공적인 PVC 바인딩이 필요합니다.

3. 이벤트가 스케줄링 실패를 나타내면, 새 Pod를 Node에 배치할 수 없는 것입니다. 업데이트된 Pod 템플릿의 리소스 요청과 사용 가능한 Node 용량을 비교합니다. 새 스펙의 Node Selector와 Toleration이 사용 가능한 Node와 일치하는지 확인합니다.

4. 플레이북의 롤아웃 이력에서 최근 업데이트 또는 롤백이 표시되면, 업데이트 전략이 롤아웃 진행을 허용하는지 확인합니다. updateStrategy의 partition 필드를 확인합니다 — 0이 아닌 partition은 의도적으로 일부 Pod의 업데이트를 방해하며, 이는 Generation 불일치로 나타날 수 있습니다.

5. Pod가 존재하지만 새 리비전으로 전환되지 않으면, Pod가 종료에 머물러 있거나 업데이트 전략이 Pod가 Ready 상태가 되기를 기다리고 있는지 확인합니다. OrderedReady 전략의 StatefulSet은 한 번에 하나의 Pod를 업데이트하며 각각이 Ready 상태가 되기를 기다립니다.

6. 이벤트가 리소스 Quota 초과를 나타내면(Forbidden, exceeded quota), namespace Quota가 새 Pod 생성을 방해하는 것입니다. ResourceQuota 상태와 현재 사용량 대비 제한을 확인합니다.

7. 명확한 이벤트 패턴이 없으면, StatefulSet 스펙의 관찰된 Generation과 metadata Generation을 비교합니다. 지속적인 불일치는 StatefulSet 컨트롤러가 스펙 변경을 처리할 수 없음을 나타냅니다. kube-controller-manager 로그에서 StatefulSet 컨트롤러 오류를 확인합니다.
