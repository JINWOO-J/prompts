---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/KubeContainerWaiting-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-configmap
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-secret
- k8s-service
- kubecontainerwaiting
- pods
---

---
title: Kube Container Waiting
weight: 20
---

# KubeContainerWaiting — Container 대기 상태

## 의미

Pod의 Container가 너무 오랫동안 Waiting 상태에 있습니다(KubeContainerWaiting 알림 발생). 누락된 의존성, 리소스 제약, 이미지 풀링 문제 또는 구성 문제로 Container를 시작할 수 없습니다. kubectl에서 Container가 Waiting 상태를 보이고,
 Pod 이벤트에 ImagePullBackOff, ErrImagePull, CreateContainerConfigError 또는 CreateContainerError가 표시되며, Container 상태에 대기 사유가 표시됩니다. 이는 워크로드 플레인에 영향을 미치며, Container 시작이 차단되어 Pod가 Ready 상태가 되지 못함을 나타냅니다. 일반적으로 이미지 풀링 실패, 누락된 ConfigMap 또는 Secret, 리소스 불가용, 노드 Taint/Toleration 불일치가 원인입니다. 누락된 ConfigMap, Secret 또는 PersistentVolumeClaim 의존성이 Container 초기화를 차단할 수 있습니다.

## 영향

KubeContainerWaiting 알림 발생; 서비스 저하 또는 불가용; Container 시작 불가; Pod가 Waiting 상태로 유지; 애플리케이션 실행 불가; Container 시작이 차단됨; Pod Readiness 확보 불가; 워크로드가 원하는 상태에 도달하지 못함. Container가 무기한 Waiting 상태로 유지; Pod 이벤트에 ImagePullBackOff, ErrImagePull 또는 CreateContainerConfigError 오류 표시; 애플리케이션이 시작되지 않고 오류 발생 가능; 누락된 ConfigMap, Secret 또는 PersistentVolumeClaim 의존성이 초기화 실패를 유발할 수 있음.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 describe하여 Container 대기 상태와 사유를 확인하고 Container가 시작되지 못하는 이유를 파악합니다.

2. Namespace `<namespace>`에서 Pod `<pod-name>`의 이벤트를 타임스탬프 순으로 조회하고 ImagePullBackOff, ErrImagePull, CreateContainerConfigError, CreateContainerError 등 대기 관련 오류 패턴을 필터링하여 시작 차단 요인을 파악합니다.

3. Namespace `<namespace>`에서 Pod `<pod-name>`이 참조하는 ConfigMap, Secret, PersistentVolumeClaim 리소스를 조회하고 Container 초기화를 방해하는 누락된 의존성을 확인합니다.

4. Namespace `<namespace>`에서 Pod `<pod-name>`을 조회하고 Container 이미지 가용성과 imagePullSecrets를 포함한 이미지 풀링 구성을 확인하여 이미지 풀링 문제를 파악합니다.

5. Namespace `<namespace>`에서 Pod `<pod-name>`을 조회하고 GPU 등 특수 리소스에 대한 Pod 리소스 request를 확인하며, 노드 `<node-name>`에서 해당 리소스의 가용성을 확인하여 리소스 제약을 파악합니다.

6. 노드 `<node-name>`을 조회하고 노드 Taint와 Toleration을 확인하여 Pod 요구사항과의 호환성을 확인하고 스케줄링 문제를 파악합니다.

## 진단

1. 플레이북 1-2단계의 Pod 이벤트를 분석하여 Container 대기 사유를 파악합니다. 이벤트에 Container가 시작되지 못하는 이유가 명확히 표시됩니다. 가장 일반적인 원인 순으로 진단합니다:

2. 이벤트에 "ImagePullBackOff" 또는 "ErrImagePull"이 표시되면(플레이북 2단계):
   - 이미지 이름과 태그가 올바른지 확인
   - 레지스트리에 이미지가 존재하는지 확인
   - 프라이빗 레지스트리에 대한 imagePullSecrets 구성 확인
   - Container 레지스트리로의 네트워크 연결 확인
   - 레지스트리 인증 정보가 유효한지 확인

3. 이벤트에 "CreateContainerConfigError"가 표시되면(플레이북 2단계), 누락된 의존성을 확인합니다(플레이북 3단계):
   - envFrom 또는 volumeMounts에서 참조하는 ConfigMap이 존재하지 않음
   - envFrom, volumeMounts 또는 imagePullSecrets에서 참조하는 Secret이 존재하지 않음
   - PersistentVolumeClaim이 바인딩되지 않았거나 존재하지 않음

4. 이벤트에 "CreateContainerError"가 표시되면, Container 런타임 로그에서 구체적인 오류를 확인합니다. 일반적인 원인:
   - 잘못된 Container 구성(잘못된 형식의 command/args)
   - 런타임과 호환되지 않는 Container 이미지
   - Container 생성을 방해하는 보안 컨텍스트

5. 리소스 제약으로 인한 Container 대기인 경우(플레이북 5-6단계), 스케줄러가 Pod를 배치했지만 리소스가 불가용합니다:
   - 노드에서 GPU 또는 기타 확장 리소스가 불가용
   - 볼륨을 노드에 연결할 수 없음

6. 노드에 Pod가 허용하지 않는 Taint가 있는 경우(플레이북 6단계), Pod가 스케줄되었지만 노드가 적합하지 않습니다. 이는 일반적으로 스케줄링 경쟁 조건을 나타냅니다.

**Container 대기 해결을 위해**: 이벤트에서 파악된 구체적인 문제를 해결합니다. ImagePullBackOff의 경우 이미지 참조 또는 레지스트리 접근을 수정합니다. CreateContainerConfigError의 경우 누락된 ConfigMap, Secret 또는 PVC를 생성합니다. 리소스 문제의 경우 리소스 request 또는 노드 구성을 조정합니다.
