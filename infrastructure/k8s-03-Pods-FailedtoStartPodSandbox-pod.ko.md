---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/03-Pods/FailedtoStartPodSandbox-pod.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- docker
- failedtostartpodsandbox
- infrastructure
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- pods
---

---
title: Failed to Start Pod Sandbox - Pod
weight: 243
categories:
  - kubernetes
  - pod
---

# FailedtoStartPodSandbox-pod — Pod Sandbox 시작 실패

## 의미

Pod Sandbox 생성이 실패하고 있습니다(KubePodPending 알림 발생). Container 런타임이 Pod Sandbox를 생성할 수 없거나, CNI 플러그인이 작동하지 않거나, 네트워크 구성이 잘못되었거나,
 리소스 제약으로 Sandbox 생성이 불가합니다. Pod가 ContainerCreating 상태를 보이고, Pod 이벤트에 FailedCreatePodSandbox 오류가 표시되며, Container 런타임 또는 CNI 플러그인 Pod에 실패가 나타날 수 있습니다. 이는 워크로드 플레인에 영향을 미치며, Container 런타임 문제, CNI 플러그인 실패 또는 리소스 제약으로 인해 Pod가 Running 상태로 전환되지 못합니다. 애플리케이션을 시작할 수 없습니다.

## 영향

Pod 시작 불가; Pod Sandbox 생성 실패; Pod가 ContainerCreating 상태로 유지; KubePodPending 알림 발생; Container 런타임 오류 발생; 네트워크 설정 실패; Pod 생성 불가; 애플리케이션 배포 불가; 서비스가 새 Pod를 확보할 수 없음. Pod가 무기한 ContainerCreating 상태로 유지; Pod 이벤트에 FailedCreatePodSandbox 오류 표시; Container 런타임 또는 CNI 플러그인 Pod에 실패가 나타날 수 있음; 애플리케이션이 시작되지 않고 오류가 발생할 수 있음.

## 플레이북

1. Namespace `<namespace>`에서 Pod `<pod-name>`을 describe하여 Container 대기 상태의 reason과 message 필드를 확인하고 Sandbox 생성 실패를 파악합니다.

2. Namespace `<namespace>`에서 Pod `<pod-name>`의 이벤트를 타임스탬프 순으로 조회하여 Pod 관련 이벤트를 파악합니다. FailedCreatePodSandbox 사유나 Sandbox 생성 실패를 나타내는 메시지에 집중합니다.

3. Pod가 스케줄된 노드에서 Container 런타임 상태(Docker, containerd)를 Pod Exec 도구 또는 SSH(노드 접근 가능 시)를 사용하여 확인하고 런타임이 정상 작동하는지 확인합니다.

4. kube-system Namespace의 Pod를 나열하고 CNI 플러그인 Pod 상태(예: Calico, Flannel, Cilium)를 확인하여 네트워크 플러그인이 실행 중인지 확인합니다.

5. 노드에서 kubelet 로그를 조회하고 Sandbox 생성 오류, Container 런타임 실패 또는 CNI 플러그인 오류를 필터링합니다.

6. 노드 리소스 가용성을 확인하고 리소스 제약이 Sandbox 생성을 방해하는지 확인합니다.

## 진단

1. 플레이북 1-2단계의 Pod 이벤트를 분석하여 Sandbox 생성 실패 원인을 파악합니다. "FailedCreatePodSandbox"를 포함하는 이벤트에는 구체적인 원인을 나타내는 상세 오류 메시지가 포함됩니다.

2. 이벤트에서 CNI 관련 오류(예: "network plugin is not ready", "failed to set up pod network")가 표시되면, CNI 플러그인 상태를 확인합니다(플레이북 4단계):
   - kube-system Namespace에서 CNI 플러그인 Pod(Calico, Flannel, Cilium 등)가 실행 중인지 확인
   - CNI 플러그인 Pod 로그에서 오류 확인
   - 노드의 /etc/cni/net.d/에 CNI 구성 파일이 존재하는지 확인
   - /opt/cni/bin/에 CNI 바이너리가 존재하는지 확인

3. 이벤트에서 Container 런타임 오류가 표시되면(플레이북 3단계), 런타임이 Pod Sandbox를 생성할 수 없습니다:
   - containerd 또는 Docker 서비스가 실행 중인지 확인
   - 런타임 로그에서 구체적인 오류 확인
   - 런타임 소켓이 접근 가능한지 확인 (/run/containerd/containerd.sock)

4. kubelet 로그에서 Sandbox 오류가 표시되면(플레이북 5단계), 일반적인 원인:
   - 런타임이 Sandbox 생성 요청에 응답하지 않음
   - 네트워크 Namespace 생성 실패
   - IP 주소 할당 실패 (IPAM 고갈)
   - Cgroup 생성 실패

5. 노드에서 리소스 압박이 표시되면(플레이북 6단계), 다음으로 인해 Sandbox 생성이 실패할 수 있습니다:
   - Container 레이어를 위한 디스크 공간 부족
   - 열린 파일이 너무 많음 (PID 또는 파일 디스크립터 제한)
   - 새 Cgroup 생성을 방해하는 메모리 압박

6. 문제가 특정 노드의 모든 Pod에 영향을 미치면, 노드 특정 문제(런타임, CNI 또는 리소스)입니다. 여러 노드의 Pod에 영향을 미치면, 클러스터 전체 문제(CNI 구성, IPAM 고갈)일 가능성이 높습니다.

**Sandbox 실패 해결을 위해**: 비정상적인 CNI 플러그인 Pod 재시작, 응답하지 않는 Container 런타임 재시작, 네트워크 구성이 올바른지 확인, 노드에 충분한 리소스가 있는지 확인합니다. 지속적인 문제의 경우 kubelet과 런타임 로그에서 상세 오류 정보를 확인합니다.
