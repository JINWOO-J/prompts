---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/DeploymentNotUpdating-deployment.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- deployment
- deploymentnotupdating
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-pod
- k8s-service
- kubernetes
- performance
- workloads
---

---
title: Deployment Not Updating - Deployment
weight: 226
categories:
  - kubernetes
  - deployment
---

# Deployment가 업데이트되지 않음 (DeploymentNotUpdating-deployment)

## 의미

Deployment가 업데이트되지 않거나 새 Replica를 롤아웃하지 않는 상태입니다(KubeDeploymentReplicasMismatch 알림 발생). Deployment 컨트롤러가 조정하지 않거나, 리소스 제약으로 Pod를 생성할 수 없거나, 이미지 Pull 실패로 새 Pod가 시작되지 않거나, Deployment 업데이트 전략이 업데이트를 차단하기 때문입니다.
kubectl에서 Deployment의 Generation이 불일치하며, Deployment 이벤트에 FailedCreate 또는 FailedUpdate 오류가 표시되고, ReplicaSet 리소스에 생성 실패가 표시될 수 있습니다. 이는 워크로드 플레인에 영향을 미치며 애플리케이션 업데이트가 적용되지 않게 합니다. 주로 리소스 제약, 이미지 Pull 실패 또는 Deployment 컨트롤러 문제가 원인이며, 애플리케이션을 업그레이드할 수 없어 오류가 발생할 수 있습니다.

## 영향

Deployment 업데이트가 적용되지 않으며, 새 애플리케이션 버전을 배포할 수 없습니다. 롤링 업데이트가 실패하고, Pod가 이전 이미지 버전에 머물러 있습니다. 원하는 Replica 수를 달성할 수 없으며, KubeDeploymentReplicasMismatch 알림이 발생합니다. Deployment 상태에 업데이트 실패가 표시되고, 애플리케이션을 업그레이드할 수 없으며, 실패한 업데이트 중 서비스 중단이 발생할 수 있습니다.

## 플레이북

1. namespace <namespace>에서 deployment <deployment-name>을 describe하여 다음을 확인합니다:
   - Replica 상태 (desired/updated/ready/available)
   - 롤아웃이 중단된 이유를 보여주는 Condition
   - FailedCreate, FailedScheduling 또는 기타 오류를 보여주는 Event

2. namespace <namespace>에서 involved object name <deployment-name>으로 필터링하고 마지막 타임스탬프 순으로 정렬하여 이벤트를 조회하고 업데이트 실패 순서를 확인합니다.

3. namespace <namespace>에서 deployment <deployment-name>의 롤아웃 상태를 확인하여 롤아웃이 진행 중인지 중단되었는지 확인합니다.

4. namespace <namespace>에서 label app=<app-label>로 ReplicaSet을 조회하여 이전 대비 새 ReplicaSet을 확인하고 어떤 ReplicaSet에 새 Pod가 있는지 확인합니다.

5. namespace <namespace>에서 label app=<app-label>로 Pod를 조회하고 pod <new-pod-name>을 describe하여 새 Pod가 실패하는 이유를 확인합니다.

6. 리소스 제약을 확인합니다:
   - namespace <namespace>에서 ResourceQuota 객체를 describe합니다
   - Node를 describe하여 할당된 리소스와 용량을 확인합니다

7. namespace <namespace>에서 deployment <deployment-name>을 조회하고 업데이트 전략을 확인하여 maxUnavailable/maxSurge 설정이 롤아웃을 차단하는지 확인합니다.

8. kube-system namespace에서 kube-controller-manager Pod의 로그를 조회하고 deployment <deployment-name> 관련 컨트롤러 오류를 필터링합니다.

## 진단

1. 플레이북 1-2단계의 Deployment 이벤트를 분석하여 주요 업데이트 실패 원인을 파악합니다. "FailedCreate" 이벤트는 Pod 생성 문제를 나타냅니다. "ProgressDeadlineExceeded" 이벤트는 롤아웃 타임아웃을 나타냅니다. "FailedScheduling" 이벤트는 스케줄링 제약을 나타냅니다. "ImagePullBackOff" 또는 "ErrImagePull" 이벤트는 이미지 Pull 실패를 나타냅니다.

2. 이벤트가 이미지 Pull 실패를 나타내면(ErrImagePull, ImagePullBackOff), 이것이 업데이트 실패의 가장 흔한 원인입니다. Deployment 스펙의 새 이미지 참조를 확인하고, 레지스트리에 이미지가 존재하는지 확인하고, 프라이빗 레지스트리 사용 시 레지스트리 자격 증명을 확인하고, 이미지 레지스트리에 대한 네트워크 연결을 확인합니다.

3. 이벤트가 스케줄링 실패를 나타내면(FailedScheduling), 플레이북 6단계의 Node 용량 데이터와 연관시켜 리소스 소진을 확인합니다. 새 Pod 스펙의 리소스 요청이 이전 버전보다 증가하여 충족할 수 없는지 확인합니다.

4. 이벤트가 리소스 Quota 문제를 나타내면("exceeded quota" 메시지 포함), 플레이북 6단계의 Quota 상태를 확인하고 새 Pod 리소스 요청과 비교합니다. Quota를 늘려야 하는지 또는 새 Deployment 리소스 요청이 과도한지 판단합니다.

5. 이벤트가 새 Pod의 크래시를 나타내면(CrashLoopBackOff, Error, OOMKilled), 플레이북 5단계의 새 Pod describe 출력을 분석하여 새 버전의 애플리케이션 수준 문제를 파악합니다. 새 버전의 시작 오류 또는 설정 문제에 대한 컨테이너 로그를 확인합니다.

6. 플레이북 3단계의 롤아웃 상태에서 롤아웃이 중단되었지만 실패 이벤트가 없으면, 플레이북 7단계의 Deployment 업데이트 전략을 확인합니다. maxUnavailable 및 maxSurge 설정이 롤아웃을 차단하지 않는지 확인합니다(예: Pod가 Ready 상태가 될 수 없는 상황에서 maxUnavailable=0).

7. 플레이북 4단계의 ReplicaSet 분석에서 새 ReplicaSet의 Ready Pod가 0이고 이전 ReplicaSet에 모든 Pod가 있으면, 업데이트가 첫 번째 새 Pod 생성에서 중단된 것입니다. 첫 번째 새 Pod가 시작할 수 없는 이유에 진단을 집중합니다.

8. 플레이북 8단계의 Deployment 컨트롤러 로그에서 조정 오류가 표시되거나 컨트롤러가 Deployment를 처리하지 않으면, 워크로드 문제가 아닌 Control Plane 문제를 나타냅니다.

**이벤트에서 명확한 실패 원인을 찾을 수 없는 경우**: Deployment가 일시 중지되었는지 확인하고(Deployment 스펙에서 paused: true 확인), Webhook 설정이 Pod 생성을 거부하지 않는지 확인하고, Pod Security Policy 또는 Admission Controller 차단을 확인하고, 새 컨테이너에 호환되지 않는 Security Context 요구사항이 있는지 검사하고, 새 버전이 다른 RBAC 접근을 필요로 하는 경우 Service Account 권한을 확인합니다.
