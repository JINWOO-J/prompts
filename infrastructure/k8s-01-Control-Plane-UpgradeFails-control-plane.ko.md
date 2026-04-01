---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/UpgradeFails-control-plane.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- control
- infrastructure
- k8s-namespace
- k8s-pod
- kubernetes
- plane
- upgradefails
---

---
title: Upgrade Fails - 업그레이드 실패 - Control Plane
weight: 294
categories:
  - kubernetes
  - control-plane
---

# UpgradeFails-control-plane

## 의미

Control Plane 업그레이드 시도가 중간에 실패하며(KubeAPIDown, KubeSchedulerDown 또는 KubeControllerManagerDown 알림 트리거 가능), 이는 버전 스큐, 호환되지 않는 컴포넌트 버전, 잘못된 구성 또는 컴포넌트가 대상 버전으로 이동하는 것을 방해하는 기반 인프라 문제로 인해 발생합니다. Control Plane 컴포넌트에서 버전 불일치가 나타나고, kubeadm 업그레이드 로그에 오류 메시지가 나타나며, Control Plane Pod가 시작에 실패하거나 버전 호환성 오류를 보일 수 있습니다. 이는 업그레이드 프로세스 실패, 컴포넌트 호환성 문제 또는 성공적인 클러스터 업그레이드를 방해하는 인프라 제약을 나타냅니다. 애플리케이션에서 API 버전 호환성 오류가 발생할 수 있습니다.

## 영향

클러스터 업그레이드가 실패합니다. 클러스터가 일관되지 않은 상태로 남을 수 있으며, 컴포넌트가 서로 다른 버전에 있을 수 있습니다. 클러스터 안정성이 손상되고, 롤백이 필요할 수 있습니다. 클러스터 운영이 중단될 수 있으며, KubeAPIDown 알림이 발생할 수 있습니다. KubeSchedulerDown 알림이 발생할 수 있고, KubeControllerManagerDown 알림이 발생할 수 있습니다. Control Plane 컴포넌트가 시작에 실패하고, 버전 스큐 오류가 발생합니다.

## 플레이북

1. kube-system 네임스페이스에서 tier=control-plane 레이블을 가진 Pod를 describe하여 버전, 상태 및 업그레이드 관련 오류를 포함한 상세 Control Plane 컴포넌트 정보를 확인합니다.

2. kube-system 네임스페이스에서 마지막 타임스탬프 순으로 이벤트를 나열하여 최근 Control Plane 이벤트를 조회하고, 업그레이드 실패, 버전 불일치 오류 또는 컴포넌트 시작 실패를 필터링합니다.

3. Kubernetes 클라이언트 및 서버 버전 정보를 조회하여 현재 클러스터 버전 상태를 확인합니다.

4. Control Plane Pod에서 Pod Exec 도구를 사용하거나 SSH를 통해 Control Plane 노드에 직접 접근하여 `kubeadm version`을 실행합니다.

5. Control Plane Pod에서 Pod Exec 도구를 사용하거나 SSH를 통해 Control Plane 노드에 직접 접근하여 `kubeadm upgrade plan`을 실행하여 업그레이드 호환성을 검증합니다.

6. Pod Exec 도구 또는 SSH를 통해 Control Plane 노드의 kubelet 서비스 로그에서 최근 200개 항목을 확인하고 오류 메시지를 필터링하거나, 가능한 경우 `/var/log/kubeadm-upgrade.log`의 kubeadm 업그레이드 로그 파일을 확인합니다.

7. 모든 노드의 상세 정보를 조회하여 모든 클러스터 컴포넌트가 대상 Kubernetes 버전과 호환되는지 검증합니다.

8. kube-system 네임스페이스에서 etcd Pod를 조회하여 etcd 버전 호환성을 검증합니다.

## 진단

1. 플레이북의 Control Plane 컴포넌트 이벤트를 분석하여 업그레이드 중 어떤 컴포넌트가 실패했는지 식별합니다. 이벤트에서 CrashLoopBackOff, Failed 또는 시작 오류가 나타나면, 이벤트 타임스탬프와 오류 메시지를 사용하여 업그레이드 프로세스의 구체적인 실패 지점을 식별합니다.

2. 이벤트에서 버전 호환성 오류가 나타나면, 플레이북 3-4단계의 컴포넌트 버전을 검증합니다. 이벤트에서 API 버전 불일치 또는 호환성 실패가 나타나면, 컴포넌트 간 버전 스큐가 성공적인 업그레이드를 방해하고 있습니다.

3. 이벤트에서 인증서 문제가 나타나면, 인증서 만료 상태를 검증합니다. 업그레이드 실패 타임스탬프에서 인증서 관련 이벤트 또는 오류가 나타나면, 만료되거나 호환되지 않는 인증서가 업그레이드를 차단하고 있습니다.

4. 이벤트에서 etcd 문제가 나타나면, 플레이북 8단계의 etcd 버전 호환성과 상태를 검증합니다. etcd 이벤트에서 버전 비호환성 또는 데이터 형식 문제가 나타나면, 진행하기 전에 etcd 업그레이드에 주의가 필요합니다.

5. 이벤트에서 컴포넌트 시작 실패가 나타나면, 플레이북 6단계의 컴포넌트 로그를 검토합니다. 실패 타임스탬프에서 로그가 구성 검증 오류, 잘못된 인수 또는 누락된 의존성을 보이면, 구성 문제가 시작을 차단하고 있습니다.

6. 이벤트에서 리소스 제약이 나타나면, Control Plane 노드 리소스를 검증합니다. 업그레이드 중 리소스 압박 이벤트가 나타났다면, 불충분한 리소스가 컴포넌트 시작을 방해한 것입니다.

7. 이벤트에서 부분적 업그레이드 완료가 나타나면, 어떤 컴포넌트가 성공적으로 업그레이드되었고 어떤 것이 실패했는지 식별합니다. 이벤트에서 일부 컴포넌트가 새 버전이고 다른 것이 이전 버전이면, 실패한 컴포넌트부터 업그레이드를 재개합니다.

**연관 관계를 찾을 수 없는 경우**: 검색 범위를 48시간으로 확장하고, 상세한 오류 메시지에 대해 업그레이드 로그를 검토하며, 컴포넌트 간 버전 호환성 문제를 확인하고, etcd 데이터 무결성을 검토하며, 인프라 리소스가 업그레이드에 충분한지 검증하고, 업그레이드 중 네트워크 연결 문제를 확인하며, 이전 업그레이드 이력에서 패턴을 검토합니다. 업그레이드 실패는 컴포넌트 상태에서 즉시 보이지 않는 누적된 구성 문제 또는 인프라 제약으로 인해 발생할 수 있습니다.
