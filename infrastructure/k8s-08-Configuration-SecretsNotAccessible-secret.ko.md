---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/08-Configuration/SecretsNotAccessible-secret.md)'
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
- secret
- secretsnotaccessible
- sts
---

---
title: Secrets Not Accessible - Secret 접근 불가
weight: 210
categories:
  - kubernetes
  - secret
---

# SecretsNotAccessible-secret

## 의미

Secret이 Pod에 접근 불가합니다(Pod 관련 알림 트리거). Secret이 올바르게 마운트되지 않았거나, RBAC 권한이 접근을 차단하거나, Secret 참조가 잘못되었거나, Pod의 서비스 계정에 권한이 부족한 것이 원인입니다.

## 영향

Pod가 Secret에 접근 불가, 애플리케이션이 민감 데이터 읽기 실패, Secret 마운트 실패, 환경 변수 미설정, Pod가 CrashLoopBackOff 또는 Pending 상태 진입, KubePodPending 알림 발생 가능, 인증 자격 증명 누락, 필수 Secret 없이 서비스 시작 불가, 이미지 풀 Secret 실패. Pod가 CrashLoopBackOff 또는 Pending 상태로 무기한 유지되며, Secret 의존성 누락으로 컨테이너 초기화가 차단될 수 있습니다.

## 플레이북

1. namespace <namespace>에서 Pod <pod-name>을 describe하여 Pod 볼륨 구성, 컨테이너 볼륨 마운트, 환경 변수 소스, 이미지 풀 Secret을 확인하고 어떤 Secret이 참조되고 어떻게 접근해야 하는지 식별합니다 - Events 섹션에서 특정 Secret 이름과 함께 "FailedMount"를 확인합니다.

2. namespace <namespace>에서 Pod <pod-name>의 이벤트를 타임스탬프 순으로 조회하여 Secret 관련 이벤트 순서를 확인합니다. FailedMount 등의 reason이나 Secret 접근 또는 권한 실패를 나타내는 메시지에 집중합니다.

3. namespace <namespace>에서 Secret <secret-name>을 조회하고 존재하며 예상 데이터를 포함하는지 확인합니다.

4. namespace <namespace>에서 Pod <pod-name> 상태를 확인하고 컨테이너 대기 상태 reason과 message 필드를 확인하여 Secret 접근 오류를 식별합니다.

5. Pod의 서비스 계정 <service-account-name>이 namespace <namespace>에서 Secret에 접근할 권한이 있는지 확인하여 RBAC 권한을 검증합니다.

6. namespace <namespace>에서 Deployment <deployment-name>을 조회하고 Pod 템플릿의 Secret 참조와 마운트 구성을 검토합니다.

## 진단

1. 플레이북의 Pod 이벤트를 분석하여 특정 Secret 접근 오류를 식별합니다. "secret not found"와 함께 "FailedMount"를 보여주는 이벤트는 Secret이 존재하지 않음을 나타냅니다. "forbidden" 또는 "unauthorized"를 보여주는 이벤트는 RBAC 권한 문제를 나타냅니다. "MountVolume.SetUp failed"를 보여주는 이벤트는 마운트 구성 문제를 나타냅니다.

2. 이벤트가 Secret 미발견을 나타내면, 플레이북 Secret 조회 결과를 사용하여 Secret이 Pod와 동일한 namespace에 존재하는지 확인합니다. Pod spec의 Secret 이름이 대소문자 구분을 포함하여 정확히 일치하는지 확인합니다.

3. 이벤트가 RBAC 권한 문제를 나타내면, 플레이북 RBAC 검증 결과를 활용하여 서비스 계정에 Secret에 대한 "get" 및 "list" 권한이 있는지 확인합니다. Role 또는 RoleBinding이 최근에 수정되거나 삭제되었는지 확인합니다.

4. 이벤트가 마운트 구성 문제를 나타내면, 플레이북 describe 출력의 Pod 볼륨과 volumeMount 구성을 검토합니다. Secret 키 이름이 실제 Secret 데이터의 키와 일치하는지 확인합니다.

5. 이벤트가 서비스 계정 문제를 나타내면, Pod의 서비스 계정이 존재하고 올바르게 참조되는지 확인합니다. 서비스 계정이 최근에 수정되었거나 imagePullSecrets 구성이 변경되었는지 확인합니다.

6. 이벤트가 불확실하면, 이벤트 타임스탬프를 최근 Deployment 롤아웃 또는 Pod 템플릿 업데이트와 비교합니다. Secret 참조 또는 마운트 경로가 Deployment 구성에서 변경되었는지 확인합니다.

**이벤트에서 명확한 원인이 식별되지 않는 경우**: Secret 데이터가 비어있거나 잘못된 형식이 아닌지 검토하고, Secret 유형이 예상 용도와 일치하는지 확인하고(Opaque, kubernetes.io/dockerconfigjson 등), admission webhook이 Secret 접근을 차단하는지 확인하고, 노드 수준 문제가 볼륨 마운트를 방해하는지 조사합니다.
