---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/02-Nodes/KubeletDown-node.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- infrastructure
- k8s-node
- k8s-pod
- k8s-service
- kubeletdown
- node
- nodes
- sts
---

---
title: Kubelet Down — Kubelet 중단
weight: 20
---

# KubeletDown

## 의미

하나 이상의 Node에서 Kubelet 서비스에 접근할 수 없거나 응답하지 않습니다(KubeletDown 알림 발생). Kubelet 프로세스가 실패했거나, 네트워크 연결이 끊겼거나, Control Plane과 통신할 수 없기 때문입니다. kubectl에서 Node가 NotReady 또는 Unknown 상태로 표시되고, Kubelet 로그에 연결 타임아웃 오류나 프로세스 실패가 기록되며, kubectl 명령이 연결 거부 또는 타임아웃 오류로 실패합니다.
 이는 데이터 플레인에 영향을 미치며, Node가 Pod를 관리하거나 상태를 보고하거나 API 서버 요청에 응답하는 것을 방해합니다. 일반적으로 Kubelet 프로세스 크래시, 인증서 만료, 네트워크 연결 문제 또는 리소스 제약이 원인이며, 영향받는 Node에서 실행 중인 애플리케이션에 오류가 발생하거나 접근이 불가능해질 수 있습니다.

## 영향

KubeletDown 알림이 발생하고, Node가 Pod를 관리할 수 없습니다. kubectl exec 및 kubectl logs가 실패하고, Pod 상태 업데이트가 중단됩니다. Node 상태가 NotReady 또는 Unknown으로 전환되며, 영향받는 Node의 Pod에 접근할 수 없게 될 수 있습니다. Node가 구성 변경을 수신할 수 없고, 컨테이너 런타임 작업이 실패하며, Node가 사실상 기능하지 않게 됩니다. Node가 무기한 NotReady 또는 Unknown 상태로 표시되고, Kubelet 로그에 연결 타임아웃 오류가 나타나며, 영향받는 Node에서 실행 중인 애플리케이션에 오류가 발생하거나 접근이 불가능해질 수 있습니다. 영향받는 Node의 Pod가 접근 불가능해지거나 축출될 수 있습니다.

## 플레이북

1. Node <node-name>을 describe하여 다음을 확인합니다:
   - Conditions 섹션에서 Ready 상태 및 Kubelet 통신 상태 확인
   - Events 섹션에서 NodeNotReady, KubeletNotReady 이벤트와 타임스탬프 확인
   - 할당된 리소스 및 시스템 정보 확인

2. Node <node-name>의 이벤트를 타임스탬프 순으로 조회하여 'NodeNotReady', 'KubeletNotReady', 'NodeUnreachable'을 포함한 Kubelet 관련 문제의 순서를 확인합니다.

3. Kubelet이 Static Pod로 실행되는 경우 Kubelet Pod 상태를 확인하거나, Pod Exec 도구 또는 SSH(Node 접근 가능 시)를 통해 Node <node-name>의 Kubelet 서비스 상태를 확인하여 Kubelet 프로세스 상태를 검증합니다.

4. Pod Exec 도구 또는 SSH(Node 접근 가능 시)를 통해 Node <node-name>에서 Kubelet 로그를 조회하고, 'panic', 'fatal', 'connection refused', 'certificate', 'timeout'을 포함한 오류 패턴을 필터링하여 Kubelet 장애를 파악합니다.

5. Node <node-name>과 API 서버 엔드포인트 간의 네트워크 연결을 확인하여 연결 문제를 파악합니다.

6. Node <node-name>의 리소스 조건을 확인하여 Kubelet 동작에 영향을 줄 수 있는 MemoryPressure, DiskPressure, PIDPressure를 확인합니다.

## 진단

1. 플레이북 1-2단계의 Node 이벤트를 분석하여 Kubelet이 사용 불가능해진 시점을 파악합니다. "NodeNotReady", "KubeletNotReady" 또는 "NodeUnreachable" 사유의 이벤트가 Kubelet 장애의 타임라인을 보여줍니다. 이벤트 타임스탬프와 메시지를 기록하여 장애 패턴을 이해합니다.

2. Node 이벤트가 Kubelet의 상태 보고 중단을 나타내는 경우, 플레이북 3단계에서 Kubelet 서비스 상태를 확인합니다. Kubelet 프로세스가 실행 중인지, 크래시되었는지, 중지되었는지 판단하여 프로세스 장애와 통신 문제를 구분합니다.

3. Kubelet이 실행되지 않는 경우, 플레이북 4단계의 Kubelet 로그에서 오류 패턴을 확인합니다. "panic", "fatal", "OOM", "connection refused" 또는 "certificate" 오류를 찾아 Kubelet이 크래시되거나 시작에 실패한 이유를 파악합니다.

4. Kubelet 로그에서 인증서 오류가 나타나는 경우, 인증서 만료 또는 갱신 실패를 나타냅니다. 인증서 유효성을 확인하고 만료 타임스탬프를 Kubelet이 사용 불가능해진 시점과 비교합니다.

5. Node 이벤트가 네트워크 문제를 나타내는 경우, 플레이북 5단계에서 네트워크 연결을 확인합니다. Kubelet이 실행 중이지만 네트워크 파티셔닝이나 방화벽 규칙으로 인해 API 서버와 통신할 수 없을 수 있습니다.

6. Node 이벤트가 리소스 압박(MemoryPressure, DiskPressure, PIDPressure)을 나타내는 경우, 플레이북 6단계에서 Node 조건을 확인합니다. 리소스 고갈은 Kubelet이 OOM Killer에 의해 종료되거나 헬스 체크에 실패하게 할 수 있습니다.

7. Kubelet 로그에서 컨테이너 런타임 오류가 나타나는 경우, 컨테이너 런타임 상태를 확인합니다. Kubelet은 컨테이너 런타임에 의존하므로 런타임이 사용 불가능하거나 응답하지 않으면 정상적으로 기능할 수 없습니다.

**이벤트에서 근본 원인을 파악할 수 없는 경우**: 시스템 로그(journalctl, dmesg)에서 커널 수준 문제를 검토하고, 디스크 손상이나 파일시스템 오류를 확인하며, Node 하드웨어 상태를 검증하고, Kubelet이 수동으로 중지되었거나 Node 수준 보안 정책의 영향을 받았는지 확인합니다.
