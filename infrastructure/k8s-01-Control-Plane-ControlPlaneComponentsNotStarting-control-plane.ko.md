---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/ControlPlaneComponentsNotStarting-control-plane.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- control
- controlplanecomponentsnotstarting
- infrastructure
- k8s-namespace
- k8s-node
- k8s-pod
- k8s-service
- kubernetes
- plane
- sts
---

---
title: Control Plane Components Not Starting - Control Plane 컴포넌트 시작 실패
weight: 292
categories:
  - kubernetes
  - control-plane
---

# ControlPlaneComponentsNotStarting-control-plane

## 의미

kube-apiserver, etcd, controller-manager 또는 scheduler와 같은 핵심 Control Plane 컴포넌트가 시작에 실패하거나 크래시루프 상태이며(KubeAPIDown, KubeSchedulerDown, KubeControllerManagerDown 알림 트리거 가능), 이는 구성 오류, 리소스 고갈, 인증서 문제 또는 Control Plane 노드의 OS/런타임 문제로 인해 발생합니다. Control Plane 컴포넌트 실패로 클러스터 운영이 차단됩니다.

## 영향

클러스터가 비기능 상태가 됩니다. API Server를 사용할 수 없고, etcd 데이터 저장소에 접근할 수 없으며, 모든 클러스터 운영이 실패합니다. 기존 워크로드는 계속 실행될 수 있지만 관리할 수 없습니다. 클러스터가 사실상 다운됩니다. KubeAPIDown, KubeSchedulerDown 또는 KubeControllerManagerDown 알림이 발생하고, Control Plane Pod가 CrashLoopBackOff 또는 Pending 상태이며, 클러스터 관리가 불가능합니다.

## 플레이북

1. kube-system 네임스페이스에서 tier=control-plane 레이블을 가진 Control Plane 컴포넌트 Pod를 describe하여 API Server, Controller Manager, Scheduler 및 etcd를 포함한 모든 Control Plane 컴포넌트 Pod의 상세 정보를 확인합니다.

2. kube-system 네임스페이스에서 타임스탬프 순으로 이벤트를 조회하여 컴포넌트 시작 실패, CrashLoopBackOff 또는 구성 오류를 필터링합니다.

3. 모든 노드를 나열하고 Control Plane 노드를 식별하여 Ready 상태와 리소스 또는 네트워크 문제를 나타내는 조건을 확인합니다.

4. 실패하는 Control Plane 컴포넌트 Pod(예: kube-apiserver 또는 etcd)의 로그를 kube-system에서 조회하거나, Control Plane 노드의 systemd 서비스에서 구성, 인증서 또는 리소스 오류를 확인합니다.

5. Control Plane 노드에서 Static Pod 매니페스트 파일(예: /etc/kubernetes/manifests/kube-apiserver.yaml 및 /etc/kubernetes/manifests/etcd.yaml)을 검사하여 구성, 파일 경로, 인증서 및 인수를 검증합니다.

6. 모든 노드의 리소스 사용량 메트릭을 조회하고 Control Plane 노드에 충분한 CPU 및 메모리 여유가 있는지 확인합니다.

7. Control Plane 노드의 디스크 공간과 inode 가용성을 확인합니다. 특히 etcd 데이터와 Kubernetes 매니페스트를 호스팅하는 볼륨을 확인합니다.

8. API Server Pod 또는 Control Plane 노드에서 etcd 엔드포인트에 대한 네트워크 연결성을 검증하여 API Server가 데이터 저장소에 접근할 수 있는지 확인합니다.

## 진단

1. 플레이북의 Control Plane 컴포넌트 이벤트를 분석하여 어떤 컴포넌트가 실패하고 있고 실패의 성격이 무엇인지 식별합니다. 이벤트에서 CrashLoopBackOff, Failed 또는 ImagePullBackOff가 나타나면, 이벤트 타임스탬프와 오류 메시지를 사용하여 구체적인 실패 원인을 식별합니다.

2. 이벤트에서 구성 오류 또는 잘못된 인수가 나타나면, 플레이북 5단계의 Static Pod 매니페스트를 검토합니다. 컴포넌트 시작 타임스탬프에서 이벤트가 검증 실패 또는 인수 파싱 오류를 보이면, 구성 문제가 근본 원인입니다.

3. 이벤트에서 인증서 오류 또는 TLS 실패가 나타나면, 플레이북의 인증서 만료 상태를 검증합니다. 컴포넌트가 시작을 중단한 타임스탬프에서 인증서 관련 이벤트가 나타나면, 만료되거나 유효하지 않은 인증서가 실패를 유발하고 있습니다.

4. 이벤트에서 리소스 압박(OOMKilled, Evicted)이 나타나면, 플레이북 6단계의 노드 리소스 메트릭을 확인합니다. 이벤트 타임스탬프에서 리소스 사용량이 제한에 근접했다면, 리소스 고갈이 컴포넌트 시작을 방해하고 있습니다.

5. 이벤트에서 디스크 공간 또는 스토리지 문제가 나타나면, 플레이북 7단계의 디스크 가용성을 검증합니다. 이벤트 타임스탬프에서 디스크 공간이 부족하거나 고갈되었다면, 스토리지 제약이 컴포넌트 시작을 차단하고 있습니다.

6. 이벤트에서 kubelet 실패 또는 노드 문제가 나타나면, 플레이북 4단계의 kubelet 상태를 분석합니다. 컴포넌트 실패 이전에 kubelet 이벤트가 재시작 또는 실패를 보이면, kubelet 문제가 Static Pod 관리를 방해하고 있습니다.

7. 이벤트에서 etcd 연결 실패가 나타나면, 플레이북 8단계의 etcd 상태와 네트워크 연결성을 검증합니다. 다른 컴포넌트가 시작에 실패한 타임스탬프에서 etcd 이벤트가 비가용성을 보이면, etcd 문제가 근본 원인입니다.

8. 이벤트에서 최근 업그레이드 또는 유지보수 활동이 나타나면, 활동 타임스탬프와 컴포넌트 실패 시작을 연관시킵니다. 업그레이드 작업 중 또는 직후에 실패가 시작되었다면, 업그레이드 프로세스가 문제를 도입했을 수 있습니다.

**연관 관계를 찾을 수 없는 경우**: 컴포넌트 로그에서 이전 경고 메시지 또는 점진적 실패를 검토하고, 시간이 지남에 따라 발전한 리소스 고갈을 확인하며, 인증서 만료를 검토하고, 디스크 공간과 inode 가용성 추세를 검증하며, 표준 배포 프로세스 외부에서 구성 파일이 수정되었는지 확인합니다. 컴포넌트 시작 실패는 즉각적인 변경보다 누적된 문제로 인해 발생할 수 있습니다.
