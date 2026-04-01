---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/KubePodContainerWaiting-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- infrastructure
- k8s-configmap
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-secret
- k8s-service
- kubepodcontainerwaiting
- kubernetes
- pods
- scaling
- sts
---

---
title: Kube Pod Container Waiting
weight: 29
categories: [kubernetes, pod]
---

# KubePodContainerWaiting — Pod Container 대기 상태

## 의미

Pod Container가 Waiting 상태에 고착되어 있습니다(KubePodContainerWaiting 알림 발생). 이미지 풀링 문제, 리소스 프로비저닝 지연 또는 구성 문제로 Container를 시작할 수 없습니다.
 Container 상태에 특정 사유(ImagePullBackOff, CreateContainerConfigError, PodInitializing)와 함께 Waiting이 표시되며, Container가 실행되지 않습니다. 이는 워크로드 플레인에 영향을 미치며, Container 시작을 방해하는 차단 문제를 나타냅니다. Pod가 트래픽을 처리할 수 없고, Deployment가 불완전하며, 서비스 용량이 감소합니다.

## 영향

KubePodContainerWaiting 알림 발생; Container 시작 불가; Pod가 Ready 상태가 아님; Deployment에 불완전한 Replica 표시; 서비스 엔드포인트 누락; 스케일링 작업 차단; HPA 효과 감소; Job 실행 불가; 이 Pod를 기다리는 의존 서비스 실패 가능; Deployment 진행 기한 초과 가능.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 조회하고 어떤 Container가 Waiting 상태인지와 구체적인 대기 사유를 파악합니다.

2. Pod의 이벤트를 조회하고 구체적인 대기 사유로 필터링하여 상세 오류 정보를 확인합니다.

3. 사유가 ImagePullBackOff 또는 ErrImagePull인 경우: 이미지 이름, 태그, 레지스트리 인증 정보가 올바른지 확인합니다.

4. 사유가 CreateContainerConfigError인 경우: Pod 사양의 ConfigMap 및 Secret 참조가 존재하고 올바른 형식인지 확인합니다.

5. 사유가 PodInitializing인 경우: Init Container 상태와 로그를 확인하여 초기화가 완료되지 않는 이유를 파악합니다.

6. 모든 볼륨 마운트가 바인딩되고 사용 가능한 기존 PersistentVolumeClaim을 참조하는지 확인합니다.

7. 리소스 request가 가용 노드 용량으로 충족될 수 있는지 확인합니다.

## 진단

대기 사유를 분석하고 특정 하위 시스템과 상관 분석합니다: ImagePull*은 레지스트리 문제, CreateContainer*는 구성 문제, PodInitializing은 Init Container 문제를 나타냅니다. Pod 상태와 이벤트를 근거로 판단합니다.

Container 구성을 기존 클러스터 리소스와 비교하고, 참조된 모든 ConfigMap, Secret, PVC가 Namespace에 존재하는지 확인합니다. 리소스 인벤토리와 Pod 사양을 근거로 판단합니다.

Container가 사이드카 주입 패턴(Istio, Vault)을 사용하는지 확인하고, 주입 Webhook이 올바르게 작동하는지 확인합니다. Webhook 로그와 주입 상태를 근거로 판단합니다.

대기 시작 시간을 최근 변경 사항과 상관 분석하고, Deployment, ConfigMap 또는 Secret 변경이 대기 상태를 트리거했는지 확인합니다. 리소스 수정 타임스탬프를 근거로 판단합니다.

Init Container가 있는 경우 성공적으로 완료되는지 확인합니다. 메인 Container는 모든 Init Container가 완료될 때까지 대기합니다. Init Container 로그와 상태를 근거로 판단합니다.

지정된 시간 범위 내에서 상관관계를 찾지 못한 경우: Container 런타임 로그(containerd/docker) 확인, 노드에 Container 레이어를 위한 충분한 디스크 공간이 있는지 확인, Container 생성 타임아웃 문제 확인, Container 시작 실패에 대한 보안 컨텍스트와 Capabilities를 점검합니다.
