---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/ImagePullBackOff-registry.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- imagepullbackoff
- infrastructure
- k8s-deployment
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-secret
- k8s-service
- kubernetes
- pods
- registry
- sts
---

---
title: ImagePullBackOff - Registry
weight: 202
categories:
  - kubernetes
  - registry
---

# ImagePullBackOff-registry — 이미지 풀링 실패

## 의미

Kubelet이 레지스트리에서 Container 이미지를 반복적으로 풀링하지 못하고 있습니다(ImagePullBackOff 또는 ErrImagePull Pod 상태 발생). 이미지 참조가 잘못되었거나, 인증 정보가 틀리거나,
 imagePullSecrets가 누락되었거나 만료되었거나, 레지스트리 또는 레지스트리로의 네트워크 경로가 불가용합니다. Pod가 ImagePullBackOff 상태로 유지되어 Container 시작이 불가합니다.

## 영향

Pod 시작 불가; Deployment가 0 Replica로 유지; 롤링 업데이트 실패; 애플리케이션 배포 실패; 서비스 불가용; 새 워크로드 생성 불가; Pod가 ImagePullBackOff 상태로 고착; 이미지 풀링 오류 발생; Container 레지스트리 연결 문제; 이미지 풀링 실패로 KubePodPending 알림 발생 가능.

## 플레이북

### AI Agent용 (NLP)

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 describe하여 이미지 풀링 실패의 정확한 오류 메시지를 확인합니다. Events 섹션에서 "Failed to pull image"와 구체적인 사유(인증 오류, 미발견, 타임아웃)를 확인합니다.

2. Namespace `<namespace>`에서 Pod `<pod-name>`의 이벤트를 Failed 사유로 필터링하고 타임스탬프 순으로 조회하여 이미지 풀링 실패 시퀀스를 확인합니다.

3. 이미지 존재 여부와 접근 가능성을 확인합니다: Namespace `<namespace>`에서 Pod `<pod-name>`의 이미지 이름을 조회하고 노드에서 수동으로 이미지 풀링을 테스트합니다.

4. imagePullSecrets 구성을 확인합니다: Namespace `<namespace>`에서 Pod `<pod-name>`의 imagePullSecrets를 조회하고, Secret이 존재하는지 확인하며, 인증 정보를 디코딩하여 확인합니다.

5. Namespace `<namespace>`에서 Deployment `<deployment-name>`을 describe하여 이미지 참조(레지스트리, 리포지토리, 태그)가 올바른지 확인하고, Pod 템플릿에 imagePullSecrets가 적절히 구성되어 있는지 확인합니다.

6. 동일 Namespace의 Pod에서 레지스트리 URL로 요청을 실행하여 레지스트리 연결을 테스트합니다.

7. Pod가 스케줄된 노드의 디스크 공간을 SSH로 확인합니다. 디스크 부족은 이미지 풀링을 방해합니다.

### DevOps/SRE용 (CLI)

1. 이미지 풀링 오류에 대한 Pod 이벤트 확인:
   ```bash
   kubectl describe pod <pod-name> -n <namespace> | grep -A 10 "Events:"
   ```

2. 이미지 풀링 실패로 필터링된 이벤트 조회:
   ```bash
   kubectl get events -n <namespace> --field-selector involvedObject.name=<pod-name>,reason=Failed --sort-by='.lastTimestamp'
   ```

3. 이미지 참조 확인 및 풀링 테스트:
   ```bash
   kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.containers[*].image}'
   # 노드에서: docker pull <image-name> 또는 crictl pull <image-name>
   ```

4. imagePullSecrets 확인 및 인증 정보 디코딩:
   ```bash
   kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.imagePullSecrets[*].name}'
   kubectl get secret <secret-name> -n <namespace> -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d
   ```

5. Deployment 이미지 구성 확인:
   ```bash
   kubectl describe deployment <deployment-name> -n <namespace>
   kubectl get deployment <deployment-name> -n <namespace> -o jsonpath='{.spec.template.spec.containers[*].image}'
   ```

6. 디버그 Pod에서 레지스트리 연결 테스트:
   ```bash
   kubectl run test-registry --rm -it --image=curlimages/curl -- curl -I https://<registry-url>/v2/
   ```

7. 노드 디스크 공간 확인:
   ```bash
   kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.nodeName}'
   kubectl debug node/<node-name> -it --image=busybox -- df -h
   ```

## 진단

1. 플레이북의 Pod 이벤트를 분석하여 구체적인 이미지 풀링 오류를 파악합니다. "unauthorized" 또는 "authentication required"를 포함하는 이벤트는 인증 정보 문제를 나타냅니다. "not found" 또는 "manifest unknown"은 이미지 또는 태그가 존재하지 않음을 나타냅니다. "timeout" 또는 "connection refused"는 네트워크 또는 레지스트리 가용성 문제를 나타냅니다.

2. 이벤트에서 인증 실패가 확인되면, 플레이북 출력에서 imagePullSecrets 구성을 확인합니다. Secret이 존재하는지, 유효한 인증 정보를 포함하는지, kubernetes.io/dockerconfigjson 타입인지 확인합니다. Secret의 레지스트리 URL이 이미지 레지스트리와 일치하는지 디코딩하여 확인합니다.

3. 이벤트에서 이미지 미발견이 확인되면, 레지스트리에 이미지 이름과 태그가 존재하는지 확인합니다. 이미지가 최근 삭제되었는지, 태그가 덮어쓰여졌는지, 리포지토리 이름이 잘못되었는지 확인합니다. 레지스트리 호스트명을 포함한 전체 이미지 경로를 확인합니다.

4. 이벤트에서 네트워크 또는 연결 문제가 확인되면, 플레이북의 레지스트리 연결 테스트 결과를 사용합니다. 노드가 레지스트리에 도달할 수 있는지, DNS 해석이 작동하는지, NetworkPolicy가 레지스트리로의 이그레스를 차단하는지 확인합니다.

5. 이벤트에서 속도 제한(예: "too many requests")이 확인되면, 레지스트리에 풀링 할당량이 있는지 확인합니다. Docker Hub의 경우 익명 풀링이 제한됩니다. 인증된 풀링을 위해 imagePullSecrets가 구성되어 있는지 확인합니다.

6. 이벤트에서 디스크 공간 문제 또는 "no space left on device"가 확인되면, 플레이북의 노드 디스크 공간 확인 결과를 확인합니다. kubelet은 이미지를 풀링하고 추출하기 위해 이미지 저장 디렉토리에 충분한 디스크 공간이 필요합니다.

**이벤트에서 명확한 원인을 파악하지 못한 경우**: 이미지가 더 이상 존재하지 않는 다이제스트를 사용하는지 확인, 프라이빗 레지스트리가 VPN 또는 특정 네트워크 접근을 필요로 하는지 확인, 레지스트리 인증서가 만료되었거나 노드에서 신뢰하지 않는지 점검, 최근 클러스터 또는 노드 업그레이드가 Container 런타임 동작을 변경했는지 검토합니다.
