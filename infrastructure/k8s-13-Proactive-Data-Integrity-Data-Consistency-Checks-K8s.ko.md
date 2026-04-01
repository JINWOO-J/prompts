---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/06-Data-Integrity/Data-Consistency-Checks-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- checks
- consistency
- data
- infrastructure
- integrity
- k8s-namespace
- k8s-pod
- k8s-pvc
- k8s-statefulset
- monitoring
- storage
---

# Data Consistency Checks — 데이터 일관성 점검

## 의미

데이터 일관성 점검은 데이터 일관성을 검증할 수 없거나 데이터 무결성 문제가 감지되었음을 나타냅니다(DataConsistencyFailed 또는 DataIntegrityViolation 같은 알림 발생). 데이터 일관성 검증 실패, 데이터 무결성 점검에서 손상 감지, 데이터 복제 불일치 확인, 데이터 체크섬 검증 실패, 또는 데이터 일관성 모니터링에서 위반 감지 등이 원인입니다. 데이터 일관성 점검에서 실패가 나타나고, 데이터 무결성 위반이 감지되며, 데이터 복제 불일치가 확인되고, 데이터 일관성 모니터링에서 문제가 표시됩니다. 이는 데이터 무결성 계층과 Persistent Volume 신뢰성에 영향을 미치며, 일반적으로 데이터 손상, 복제 지연 문제, 체크섬 검증 실패, 또는 데이터 일관성 모니터링 문제로 인해 발생합니다. 데이터 일관성이 컨테이너 워크로드에 영향을 미치면 컨테이너 Persistent Volume 데이터가 불일치하고 애플리케이션에서 데이터 무결성 문제가 발생할 수 있습니다.

## 영향

DataConsistencyFailed 알림 발생, DataIntegrityViolation 알림 발생, 데이터 일관성 검증 불가, 데이터 무결성 문제 감지, 데이터 손상 가능성, Persistent Volume 신뢰성 저하. 데이터 일관성 점검에서 실패가 나타나며, 데이터 일관성이 컨테이너 워크로드에 영향을 미치면 컨테이너 Persistent Volume 데이터가 불일치하고, Pod 데이터가 손상되며, 컨테이너 애플리케이션에서 데이터 무결성 문제가 발생할 수 있습니다. 애플리케이션에서 데이터 손상 또는 데이터 일관성 실패가 발생할 수 있습니다.

## 플레이북

1. 네임스페이스 <namespace>의 Persistent Volume Claim을 조회하여 모든 PVC와 현재 상태를 확인합니다.

2. 네임스페이스 <namespace>의 최근 이벤트를 타임스탬프 순으로 조회하여 최근 데이터 일관성 문제나 스토리지 오류를 확인합니다.

3. 네임스페이스 <namespace>의 PVC <pvc-name>을 상세 조회하여 Persistent Volume 일관성 점검 상태와 마지막 일관성 점검 타임스탬프를 확인합니다.

4. 네임스페이스 <namespace>의 StatefulSet <statefulset-name>을 상세 조회하여 StatefulSet 데이터 일관성 및 복제 상태를 확인합니다.

5. kube-system 네임스페이스에서 app=csi-controller 레이블의 Persistent Volume 컨트롤러 Pod 로그를 조회하고 데이터 일관성 오류를 필터링합니다.

6. 지난 24시간 동안의 Persistent Volume에 대한 Prometheus 메트릭(replication_lag, data_consistency_status 포함)을 조회하여 데이터 일관성 문제를 확인합니다.

7. 볼륨 `<volume-name>`의 Persistent Volume 무결성 점검 결과를 조회하고 볼륨 데이터 무결성 상태를 확인하여 Persistent Volume 데이터 일관성을 점검합니다.

8. 네임스페이스 <namespace>의 모든 PVC를 wide 출력으로 조회하고 볼륨 데이터 무결성 상태를 확인하여 PVC 데이터 일관성을 점검합니다.

## 진단

1. 1단계와 3단계의 PVC 상태를 검토합니다. 일관성 점검 상태에서 실패가 나타나면 영향받는 볼륨을 식별하고 일관성 점검 타임스탬프를 확인하여 불일치가 언제 발생했는지 파악합니다.

2. 4단계의 StatefulSet 데이터 일관성을 분석합니다. 복제 상태에서 오류가 나타나면 레플리카 간 데이터가 불일치할 수 있습니다. 복제가 정상이면 단일 레플리카 데이터 손상이 원인일 수 있습니다.

3. 5단계의 CSI 컨트롤러 로그에서 데이터 일관성 오류가 나타나면, 오류가 스토리지 수준(스토리지 인프라 문제 시사)인지 애플리케이션 수준(애플리케이션 데이터 손상 시사)인지 확인합니다.

4. 6단계의 복제 메트릭을 검토합니다. replication_lag가 높으면 일관성 위반이 손상이 아닌 지연으로 인한 것일 수 있습니다. 지연이 낮으면 실제 데이터 손상이 존재합니다.

5. 7단계의 볼륨 무결성 점검 결과에서 실패가 나타나면 Persistent Volume 데이터가 손상된 것이며 백업에서 복구가 필요할 수 있습니다.

분석이 결론에 도달하지 못하는 경우: 2단계의 이벤트에서 스토리지 오류나 데이터 관련 문제를 확인합니다. 8단계의 PVC 데이터 일관성을 검토하여 볼륨 수준 무결성을 확인합니다. 일관성 문제가 모든 레플리카에 영향을 미치는지(애플리케이션 수준 손상 시사) 또는 특정 레플리카에만 영향을 미치는지(해당 레플리카의 스토리지 수준 문제 시사) 판단합니다.
