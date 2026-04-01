---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/KubePodImagePullBackOff-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- docker
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-secret
- k8s-service
- kubepodimagepullbackoff
- kubernetes
- pods
- scaling
- sts
---

---
title: Kube Pod Image Pull BackOff
weight: 26
categories: [kubernetes, pod]
---

# KubePodImagePullBackOff — Pod 이미지 풀링 BackOff

## 의미

Pod가 ImagePullBackOff 상태에 고착되어 있습니다(KubePodImagePullBackOff 알림 발생). 인증 실패, 네트워크 문제, 존재하지 않는 이미지 또는 레지스트리 불가용으로 인해
 Kubernetes가 레지스트리에서 Container 이미지를 풀링할 수 없습니다. Pod 상태에 지수 백오프 지연과 함께 ImagePullBackOff가 표시되고, Container 생성이 차단되며, Pod를 시작할 수 없습니다. 이는 워크로드 플레인에 영향을 미치며, 이미지 또는 레지스트리 접근 문제를 나타냅니다. 새 배포 실패, 스케일링 작업으로 Replica 추가 불가, 롤아웃 차단, 서비스 용량 증가 불가.

## 영향

KubePodImagePullBackOff 알림 발생; Pod 시작 불가; Deployment 또는 스케일링 작업 실패; 새 Replica 생성 불가; 롤아웃 차단; 서비스 용량 감소; Deployment에 불가용 Replica 표시; HPA 스케일 업 불가; 예약된 Job 시작 불가; Init Container 풀링 불가; 애플리케이션 업데이트 진행 불가; 기존 Pod가 실패하면 서비스 가용성에 영향.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 조회하고 상태가 ImagePullBackOff인지 확인하며, 실패한 특정 Container 이미지를 기록합니다.

2. Namespace `<namespace>`에서 Pod `<pod-name>`의 이벤트를 조회하고 'Failed to pull image', 'ImagePullBackOff', 'ErrImagePull'을 필터링하여 구체적인 오류 메시지를 파악합니다.

3. 이미지 이름과 태그가 올바르고 레지스트리에 이미지가 존재하는지 확인합니다. 레지스트리를 직접 확인하거나 로컬에서 docker pull을 사용합니다.

4. Pod 사양에 imagePullSecrets가 올바르게 구성되어 있는지 확인하고, 참조된 Secret이 Namespace에 존재하는지 확인합니다.

5. imagePullSecret을 조회하고 대상 레지스트리에 대한 유효한 인증 정보가 포함되어 있는지 확인합니다. 사용자 이름과 레지스트리 서버 값을 확인합니다.

6. 노드에서 레지스트리 연결을 테스트하여 노드가 레지스트리 엔드포인트에 도달할 수 있는지 확인합니다(NetworkPolicy, 방화벽 규칙, 프록시 설정).

7. Pod가 사용하는 ServiceAccount에 imagePullSecrets가 연결되어 있는지 확인합니다(ServiceAccount 기반 이미지 풀링 인증 정보 사용 시).

## 진단

Pod 사양의 이미지 이름을 레지스트리의 가용 이미지와 비교하고, 이미지 태그가 존재하는지 확인합니다(일반적인 문제: 존재하지 않는 'latest' 사용 또는 잘못된 태그). 레지스트리 API 또는 UI를 근거로 판단합니다.

이미지 풀링 실패를 레지스트리 가용성과 상관 분석하고, 레지스트리에 장애 또는 속도 제한이 발생하고 있는지 확인합니다. 레지스트리 상태 페이지와 오류 메시지를 근거로 판단합니다.

이미지 풀링 Secret을 분석하고 인증 정보가 유효하며 만료되지 않았는지 확인합니다. 특히 TTL이 있는 토큰(ECR, GCR 임시 토큰)에 주의합니다. Secret 생성 시간과 레지스트리 인증 로그를 근거로 판단합니다.

이미지가 프라이빗 레지스트리에 있는지 확인하고, 해당 레지스트리 호스트명에 대해 imagePullSecrets가 올바르게 구성되어 있는지 확인합니다. Pod 사양과 Secret 데이터를 근거로 판단합니다.

노드가 레지스트리에 네트워크 연결이 가능한지 확인하고, 이미지 풀링을 차단할 수 있는 NetworkPolicy, 방화벽 규칙 또는 프록시 요구사항을 점검합니다. 노드 네트워크 구성과 이그레스 규칙을 근거로 판단합니다.

지정된 시간 범위 내에서 상관관계를 찾지 못한 경우: 노드에서 수동으로 이미지 풀링 시도, Container 런타임 로그(containerd/docker)에서 상세 오류 확인, 레지스트리 TLS 인증서 유효성 확인, 이미지가 크기 제한을 초과하는지 확인, 이미지 레이어 저장을 위한 노드 디스크 공간을 확인합니다.
