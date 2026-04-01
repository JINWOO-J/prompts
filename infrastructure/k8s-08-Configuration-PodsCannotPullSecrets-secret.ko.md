---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/08-Configuration/PodsCannotPullSecrets-secret.md)'
role: Kubernetes SRE
origin: scoutflo
extract_date: 2026-03-05
tags:
- configuration
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-rbac
- k8s-secret
- k8s-service
- kubernetes
- podscannotpullsecrets
- secret
- sts
---

---
title: Pods Cannot Pull Secrets - Pod의 Secret 가져오기 실패
weight: 240
categories:
  - kubernetes
  - secret
---

# PodsCannotPullSecrets-secret

## 의미

Pod가 Secret을 가져오거나 접근할 수 없습니다(Pod 관련 알림 트리거). Secret이 존재하지 않거나, Secret 참조가 잘못되었거나, RBAC 권한이 접근을 차단하거나, Secret이 올바르게 마운트되지 않은 것이 원인입니다.

## 영향

Pod 시작 불가, 애플리케이션이 Secret 읽기 실패, Secret 접근 실패 발생, Pod가 CrashLoopBackOff 또는 Pending 상태 진입, KubePodPending 알림 발생, 인증 자격 증명 누락, 이미지 풀 Secret 실패, 필수 Secret 없이 서비스 시작 불가, 환경 변수 미설정. Pod가 CrashLoopBackOff 또는 Pending 상태로 무기한 유지되며, Secret 의존성 누락으로 컨테이너 초기화가 차단될 수 있습니다.

## 플레이북

1. namespace <namespace>에서 Pod <pod-name>을 describe하여 이미지 풀 Secret, Pod 볼륨 구성, 컨테이너 볼륨 마운트, 환경 변수 소스를 확인하고 어떤 Secret이 참조되는지 식별합니다 - Events 섹션에서 특정 Secret 이름과 함께 "Failed" 또는 "FailedMount"를 확인합니다.

2. namespace <namespace>에서 Pod <pod-name>의 이벤트를 타임스탬프 순으로 조회하여 Secret 관련 이벤트 순서를 확인합니다. Failed, FailedMount 등의 reason이나 Secret 접근 실패를 나타내는 메시지에 집중합니다.

3. namespace <namespace>에서 Secret <secret-name>을 조회하고 동일 namespace에 존재하는지 확인합니다.

4. namespace <namespace>에서 Pod <pod-name> 상태를 확인하고 컨테이너 대기 상태 reason과 message 필드를 확인하여 Secret 접근 오류를 식별합니다.

5. Pod의 서비스 계정 <service-account-name>이 namespace <namespace>에서 Secret에 접근할 권한이 있는지 확인하여 RBAC 권한을 검증합니다.

6. namespace <namespace>에서 Deployment <deployment-name>을 조회하고 Pod 템플릿의 Secret 참조를 검토하여 구성이 올바른지 확인합니다.

## 진단

1. 플레이북의 Pod 이벤트를 분석하여 특정 Secret 가져오기 오류를 식별합니다. "secret not found"를 보여주는 이벤트는 Secret이 존재하지 않거나 다른 namespace에 있음을 나타냅니다. "FailedMount"를 보여주는 이벤트는 볼륨 마운트 문제를 나타냅니다. "forbidden"을 보여주는 이벤트는 RBAC 권한 문제를 나타냅니다.

2. 이벤트가 Secret 미발견을 나타내면, 플레이북 Secret 조회 결과를 사용하여 Secret이 존재하지 않음을 확인합니다. Secret이 최근에 삭제되었는지, 생성되지 않았는지, Pod와 다른 namespace에 존재하는지 확인합니다.

3. 이벤트가 RBAC 권한 문제를 나타내면, 플레이북 RBAC 검증 결과를 활용하여 Pod의 서비스 계정에 Secret 접근 권한이 있는지 확인합니다. Role과 RoleBinding 객체가 존재하고 서비스 계정에 대해 올바르게 구성되어 있는지 확인합니다.

4. 이벤트가 imagePullSecrets 문제(이미지 풀 실패)를 나타내면, Pod spec의 imagePullSecrets 참조가 kubernetes.io/dockerconfigjson 유형의 기존 Secret을 가리키는지 확인합니다. Secret에 유효한 레지스트리 자격 증명이 포함되어 있는지 확인합니다.

5. 이벤트가 볼륨 마운트 실패를 나타내면, 플레이북 describe 출력의 Pod 볼륨 구성을 검토합니다. Secret 키 참조가 Secret의 실제 키와 일치하는지 확인하고, 중요하지 않은 Secret에 대해 optional 플래그가 적절히 설정되어 있는지 확인합니다.

6. 이벤트가 불확실하면, 이벤트 타임스탬프를 최근 배포 변경과 비교합니다. Secret 참조가 수정되었는지, 새 Pod 템플릿이 롤아웃되었는지, namespace 구성이 변경되었는지 확인합니다.

**이벤트에서 명확한 원인이 식별되지 않는 경우**: Secret 데이터가 손상되거나 비어있지 않은지 확인하고, Secret이 올바른 유형으로 생성되었는지 확인하고, admission controller 또는 정책이 Secret 접근을 차단하는지 조사하고, API 서버 로그에서 Secret 조회 오류를 검토합니다.
