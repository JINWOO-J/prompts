---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/06-Data-Integrity/Data-Corruption-Detection-K8s.md)'
role: SRE / K8s Proactive Operations
origin: scoutflo
tags:
- corruption
- data
- detection
- infrastructure
- integrity
- k8s-namespace
- k8s-pod
- k8s-pvc
- monitoring
- storage
- sts
---

# Data Corruption Detection — 데이터 손상 감지

## 의미

데이터 손상 감지는 데이터 손상이 감지되거나 데이터 무결성 위반이 확인되었음을 나타냅니다(DataCorruptionDetected 또는 DataIntegrityViolation 같은 알림 발생). 데이터 손상 점검에서 손상 감지, 데이터 무결성 위반 확인, 데이터 체크섬 검증 실패, 데이터 손상 모니터링에서 문제 감지, 또는 데이터 복원 테스트에서 손상 발견 등이 원인입니다. 데이터 손상 점검에서 실패가 나타나고, 데이터 무결성 위반이 감지되며, 데이터 체크섬 검증이 실패하고, 데이터 손상 모니터링에서 문제가 표시됩니다. 이는 데이터 무결성 계층과 데이터 신뢰성에 영향을 미치며, 일반적으로 스토리지 손상, 데이터 전송 오류, 체크섬 검증 실패, 또는 데이터 손상 모니터링 문제로 인해 발생합니다. 데이터 손상이 컨테이너 워크로드에 영향을 미치면 컨테이너 Persistent Volume 데이터가 손상되고 애플리케이션에서 데이터 무결성 실패가 발생할 수 있습니다.

## 영향

DataCorruptionDetected 알림 발생, DataIntegrityViolation 알림 발생, 데이터 손상 감지, 데이터 무결성 위반 확인, 데이터 신뢰성 저하, 애플리케이션에서 데이터 오류 발생 가능. 데이터 손상 감지에서 실패가 나타나며, 데이터 손상이 컨테이너 워크로드에 영향을 미치면 컨테이너 Persistent Volume 데이터가 손상되고, Pod 데이터가 유효하지 않으며, 컨테이너 애플리케이션에서 데이터 무결성 실패가 발생할 수 있습니다. 애플리케이션에서 데이터 오류 또는 데이터 손상 실패가 발생할 수 있습니다.

## 플레이북

1. 네임스페이스 <namespace>의 Persistent Volume Claim을 조회하여 손상 분석을 위한 모든 PVC와 현재 상태를 확인합니다.

2. 네임스페이스 <namespace>의 최근 이벤트를 타임스탬프 순으로 조회하여 최근 데이터 손상 오류나 스토리지 실패를 확인합니다.

3. 네임스페이스 <namespace>의 PVC <pvc-name>을 상세 조회하여 Persistent Volume 손상 점검 상태와 마지막 손상 점검 타임스탬프를 확인합니다.

4. kube-system 네임스페이스에서 app=csi-controller 레이블의 Persistent Volume 컨트롤러 Pod 로그를 조회하고 데이터 손상 오류 또는 무결성 위반 패턴을 필터링합니다.

5. 지난 24시간 동안의 Persistent Volume에 대한 Prometheus 메트릭(data_errors, data_corruption_errors 포함)을 조회하여 데이터 손상 패턴을 확인합니다.

6. 네임스페이스 <namespace>의 볼륨 스냅샷을 조회하고 스냅샷 체크섬 및 손상 감지 결과를 확인합니다.

7. 네임스페이스 <namespace>의 StatefulSet <statefulset-name>을 상세 조회하고 데이터 일관성 및 손상 감지 상태를 확인합니다.

8. Persistent Volume Claim 무결성 점검 결과를 조회하고 Persistent Volume 데이터 손상 상태를 확인하여 PVC 데이터 무결성을 점검합니다.

## 진단

1. 3단계의 PVC 손상 상태를 검토합니다. 손상 점검 상태에서 실패가 나타나면 손상 범위를 평가하고 백업에서 데이터 복구가 필요한지 판단합니다.

2. 4단계의 CSI 컨트롤러 로그를 분석합니다. 로그에서 손상 오류 또는 무결성 위반 패턴이 나타나면, 손상이 스토리지 수준(디스크 또는 스토리지 시스템 문제 시사)인지 애플리케이션 수준(애플리케이션 버그 시사)인지 확인합니다.

3. 5단계의 Persistent Volume 메트릭에서 data_corruption_errors가 나타나면 영향받는 볼륨과 타임스탬프를 확인합니다. 오류가 증가하고 있으면 손상이 진행 중이며, 안정적이면 과거 이벤트로 인한 손상일 수 있습니다.

4. 6단계의 볼륨 스냅샷 체크섬을 검토합니다. 스냅샷에서 손상이 나타나면 스냅샷 시점에 이미 손상이 존재했으며 이전 스냅샷에서 복구해야 합니다. 스냅샷이 정상이면 복구에 사용할 수 있습니다.

5. 8단계의 PVC 무결성 점검 결과에서 실패가 나타나면 데이터 중요도에 따라 영향받는 볼륨의 복구 우선순위를 정합니다.

분석이 결론에 도달하지 못하는 경우: 2단계의 이벤트에서 스토리지 실패나 데이터 관련 오류를 확인합니다. 7단계의 StatefulSet 데이터 상태를 검토하여 복제 상태를 확인합니다. 손상이 특정 볼륨에만 영향을 미치는지(국소적 스토리지 문제 시사) 또는 여러 볼륨에 영향을 미치는지(시스템적 스토리지 인프라 문제 시사) 판단합니다.
