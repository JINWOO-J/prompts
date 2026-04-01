---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/04-Workloads/KubeDeploymentGenerationMismatch-deployment.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- deployment
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-service
- kubedeploymentgenerationmismatch
- performance
- workloads
---

---
title: Kube Deployment Generation Mismatch
weight: 20
---

# Deployment Generation 불일치 (KubeDeploymentGenerationMismatch)

## 의미

롤백 또는 실패한 업데이트로 인한 Deployment Generation 불일치 상태입니다(Deployment Generation 관련 알림 발생). 관찰된 Generation이 원하는 Generation과 일치하지 않아 Deployment 업데이트 또는 롤백 작업이 성공적으로 완료되지 않았음을 나타냅니다.
kubectl에서 Deployment의 Generation이 불일치하며, Deployment 이벤트에 Failed, ProgressDeadlineExceeded 또는 ReplicaSetCreateError 오류가 표시되고, ReplicaSet 리소스에 생성 실패가 표시될 수 있습니다. 이는 워크로드 플레인에 영향을 미치며 Deployment 조정 실패 또는 업데이트 문제를 나타냅니다. 주로 지속적인 리소스 제약, Deployment 컨트롤러 문제 또는 클러스터 용량 제한이 원인이며, 애플리케이션이 오래된 설정으로 실행되어 오류가 발생할 수 있습니다.

## 영향

KubeDeploymentGenerationMismatch 알림이 발생하며, 서비스 저하 또는 사용 불가가 발생합니다. Deployment가 원하는 상태를 달성할 수 없고, Generation 불일치가 적절한 조정을 방해합니다. Deployment 업데이트 또는 롤백이 중단되며, Deployment 상태에 Generation 불일치가 표시됩니다. 컨트롤러가 Deployment 상태를 조정할 수 없고, Deployment 조정 작업이 실패합니다.

## 플레이북

1. namespace <namespace>에서 deployment <deployment-name>을 describe하여 다음을 확인합니다:
   - 관찰된 Generation 대비 원하는 Generation
   - Replica 상태 (desired/updated/ready/available)
   - 롤아웃이 중단된 이유를 보여주는 Condition
   - Failed, ProgressDeadlineExceeded 또는 ReplicaSetCreateError 오류를 보여주는 Event

2. namespace <namespace>에서 involved object name <deployment-name>으로 필터링하고 마지막 타임스탬프 순으로 정렬하여 이벤트를 조회하고 Generation 불일치 문제 순서를 확인합니다.

3. namespace <namespace>에서 deployment <deployment-name>의 롤아웃 이력을 조회하여 불일치를 유발했을 수 있는 최근 업데이트 또는 롤백을 확인합니다.

4. namespace <namespace>에서 label app=<app-label>로 ReplicaSet 리소스를 조회하고 ReplicaSet 상태 및 Replica 수를 확인하여 Replica 분포를 검증합니다.

5. namespace <namespace>에서 label app=<app-label>로 Pod를 조회하고 pod <pod-name>을 describe하여 실패 또는 오류 상태의 Pod를 식별합니다.

6. namespace <namespace>에서 deployment <deployment-name>을 조회하고 업데이트 전략 설정과 롤아웃이 일시 중지되었는지 확인하여 업데이트 차단 요인을 파악합니다.

## 진단

1. 플레이북 1-2단계의 Deployment 이벤트를 분석하여 주요 실패 원인을 파악합니다. "ProgressDeadlineExceeded" 이벤트는 롤아웃 타임아웃을 나타냅니다. "ReplicaSetCreateError" 이벤트는 ReplicaSet 생성 실패를 나타냅니다. "FailedCreate" 이벤트는 Pod 생성 문제를 나타냅니다. "Paused" 이벤트는 의도적으로 일시 중지된 롤아웃을 나타냅니다.

2. 이벤트가 ProgressDeadlineExceeded를 나타내면, 플레이북 1단계의 Deployment Condition을 확인하여 롤아웃이 완료되지 않은 구체적인 이유를 파악합니다. 플레이북 3단계의 롤아웃 이력과 연관시켜 새 업데이트인지 중단된 이전 업데이트인지 판단합니다.

3. 이벤트가 ReplicaSet 생성 실패를 나타내면, 플레이북 4단계의 ReplicaSet 상태를 분석하여 어떤 Generation의 ReplicaSet이 실패했는지 확인합니다. 이벤트 메시지에서 리소스 Quota 제약 또는 Admission Webhook 거부를 확인합니다.

4. 이벤트가 스케줄링 실패를 나타내면(FailedScheduling), 플레이북 5단계의 Pod Pending 상태와 새 ReplicaSet을 연관시켜 새 Pod를 스케줄링할 수 없음을 확인합니다. Node 용량 데이터에서 리소스 제약을 확인합니다.

5. 이벤트가 이미지 Pull 실패를 나타내면(ErrImagePull, ImagePullBackOff), Deployment 스펙의 새 이미지 참조를 확인하고 새 이미지가 존재하고 접근 가능한지 확인합니다.

6. 이벤트가 새 Pod의 크래시를 나타내면(CrashLoopBackOff, Error), 플레이북 5단계의 Pod describe 출력을 분석하여 새 버전 Pod가 실패하는 이유를 파악합니다. 이는 새 Deployment 버전의 애플리케이션 수준 문제를 나타냅니다.

7. 플레이북 6단계에서 Deployment가 "Paused: true"를 표시하면, 일시 중지된 롤아웃 중 Generation 불일치는 예상되는 동작입니다. 일시 중지가 의도적인지 또는 재개를 위한 수동 개입이 필요한지 확인합니다.

8. 이벤트가 결정적이지 않으면, 플레이북 1단계의 관찰된 Generation 대비 원하는 Generation을 비교하고 플레이북 3단계의 롤아웃 이력과 연관시켜 불일치가 최근 업데이트, 롤백 시도 또는 중단된 조정으로 인한 것인지 판단합니다.

**이벤트에서 명확한 실패 원인을 찾을 수 없는 경우**: Deployment 컨트롤러 로그에서 조정 오류를 검토하고, 클러스터 전체의 지속적인 리소스 제약을 확인하고, kube-system namespace에서 Deployment 컨트롤러 Pod 상태를 확인하고, Deployment가 빠른 연속으로 여러 번 수정되어 컨트롤러 백로그를 유발했는지 검사합니다.
