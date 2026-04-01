---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/CannotAccessAPI-control-plane.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- cannotaccessapi
- control
- infrastructure
- k8s-ingress
- k8s-namespace
- k8s-node
- k8s-pod
- kubernetes
- plane
- security
---

---
title: Cannot Access API - API 접근 불가 - Control Plane
weight: 255
categories:
  - kubernetes
  - control-plane
---

# CannotAccessAPI-control-plane

## 의미

kubectl, CI/CD 시스템 또는 외부 Controller와 같은 외부 클라이언트가 Kubernetes API Server 엔드포인트에 TCP/TLS 연결을 설정할 수 없으며(KubeAPIDown 알림 트리거 가능), 이는 Control Plane 접근성 또는 노출 문제를 나타냅니다. API Server 연결 실패로 인해 클러스터 Control Plane에 대한 외부 접근이 차단됩니다.

## 영향

모든 kubectl 명령이 실패합니다. 클러스터 관리 작업을 수행할 수 없으며, Controller가 상태를 조정할 수 없고, 클러스터가 관리 불가능해집니다. 애플리케이션은 계속 실행될 수 있지만 업데이트하거나 스케일링할 수 없습니다. KubeAPIDown 알림이 발생할 수 있으며, 외부 네트워크에서 API Server에 접근할 수 없고, 연결 타임아웃 또는 연결 거부 오류가 발생합니다. 클러스터 관리 도구가 실패합니다.

## 플레이북

1. kube-system 네임스페이스에서 component=kube-apiserver 레이블을 가진 API Server Pod를 describe하여 상태, 재시작 횟수, 조건 및 오류 메시지를 포함한 상세 정보를 확인합니다.

2. kube-system 네임스페이스에서 타임스탬프 순으로 이벤트를 조회하여 API Server 연결 오류 또는 실패를 필터링합니다.

3. API Server 엔드포인트를 포함한 클러스터 정보를 조회하고, API 접근에 사용되는 정확한 URL과 IP/포트를 기록합니다.

4. 클러스터 내부 Pod에서 API Server 엔드포인트에 대한 TCP/TLS 연결을 검증하여 기본 연결성을 테스트합니다.

5. Control Plane 노드에서 API Server가 예상 포트와 인터페이스에서 수신 대기 중인지 확인하여 API Server 프로세스가 올바르게 바인딩되었는지 확인합니다.

6. Control Plane 노드 및 주변 네트워크(클라우드 방화벽, Security Group, NACL)에서 포트 6443의 인그레스 또는 이그레스를 차단할 수 있는 방화벽 및 Security Group 규칙을 확인합니다.

7. kube-system 및 기타 관련 네임스페이스에서 NetworkPolicy 리소스를 나열하고, 외부 클라이언트 또는 Ingress 게이트웨이에서 API Server로의 트래픽을 제한하는 정책이 있는지 검사합니다.

## 진단

1. 플레이북의 API Server Pod 이벤트를 분석하여 API Server가 실행 중이고 정상인지 식별합니다. 이벤트에서 Pod 실패, 재시작 또는 비정상 상태가 나타나면, 외부 접근 문제가 아닌 API Server 비가용성이 근본 원인입니다.

2. 이벤트에서 API Server가 정상임을 나타내면, 플레이북 4-5단계의 네트워크 연결성을 검증합니다. API Server가 실행 중이지만 외부 접근이 실패하면, 네트워크 경로 문제가 원인일 가능성이 높습니다.

3. 이벤트에서 NetworkPolicy 변경이 나타나면, 플레이북 7단계의 정책 수정을 검토합니다. 접근 실패 시작 전에 NetworkPolicy 이벤트가 발생했다면, 정책 변경이 외부 클라이언트 접근을 차단했을 수 있습니다.

4. 이벤트에서 방화벽 또는 Security Group 변경이 나타나면, 인프라 변경 타임스탬프와 실패 시작을 연관시킵니다. 접근 실패 이전 타임스탬프에서 방화벽 수정이 발생했다면, 네트워크 보안 변경이 연결을 차단한 것입니다.

5. 이벤트에서 Load Balancer 문제가 나타나면, Load Balancer 상태와 구성을 검증합니다. 접근 실패 타임스탬프에서 Load Balancer 이벤트가 구성 변경 또는 헬스 체크 실패를 보이면, Load Balancer 문제가 근본 원인입니다.

6. 이벤트에서 API Server 구성 변경(ConfigMap, Deployment)이 나타나면, 변경 타임스탬프와 실패 시작을 연관시킵니다. 접근 실패 전에 API Server 구성이 수정되었다면, 구성 변경이 바인딩 또는 TLS 설정에 영향을 미쳤을 수 있습니다.

7. 이벤트에서 유지보수 또는 업그레이드 활동이 나타나면, 활동 타임스탬프와 접근 실패 시작을 연관시킵니다. 실패 1시간 이내에 유지보수 이벤트가 발생했다면, 계획된 변경이 의도치 않게 외부 접근에 영향을 미쳤을 수 있습니다.

**연관 관계를 찾을 수 없는 경우**: 검색 범위를 확장하고(10분→30분, 1시간→2시간), 클러스터 이벤트에 기록되지 않은 방화벽 또는 Security Group 변경에 대해 클라우드 제공자 로그를 확인하고, Load Balancer 구성 이력을 검토하며, 네트워크 라우팅 변경을 검토하고, API Server 엔드포인트 또는 DNS 레코드가 수정되었는지 확인합니다. 네트워크 연결 문제는 Kubernetes 리소스에서 즉시 보이지 않는 인프라 수준의 원인이 있을 수 있습니다.
