---
category: infrastructure
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/01-Control-Plane/KubeClientErrors-control-plane.md)'
role: SRE / K8s Incident Response
origin: scoutflo
tags:
- capacity
- control
- infrastructure
- k8s-namespace
- k8s-pod
- k8s-service
- kubeclienterrors
- kubernetes
- performance
- plane
- sts
---

---
title: Kube Client Errors - 클라이언트 오류
weight: 20
---

# KubeClientErrors

## 의미

Kubernetes API Server 클라이언트가 지난 15분간 1% 이상의 오류율을 경험하고 있으며(KubeClientErrors 알림 트리거), 네트워크 문제, 인증 문제, 속도 제한 또는 API Server 오류로 인해 API 클라이언트 요청이 실패하고 있습니다. 클라이언트 로그에 연결 거부, 타임아웃, 속도 제한 또는 인증 실패 오류가 나타나고, API 클라이언트 메트릭에서 오류율이 1%를 초과하며, API 작업이 간헐적으로 실패합니다. 이는 워크로드와 Control Plane에 영향을 미치며, 안정적인 API 통신을 방해하는 클라이언트 측 또는 서버 측 문제를 나타냅니다. 일반적으로 네트워크 연결 문제, 인증서 만료, 속도 제한 또는 API Server 용량 문제가 원인이며, Kubernetes API를 사용하는 애플리케이션에서 오류가 발생할 수 있습니다.

## 영향

KubeClientErrors 알림이 발생합니다. 특정 Kubernetes 클라이언트가 오작동할 수 있으며, 서비스 저하가 발생합니다. API 작업이 간헐적으로 실패하고, Controller가 조정에 실패할 수 있습니다. Kubernetes API를 사용하는 애플리케이션에서 오류가 발생하고, 클라이언트 측 재시도가 소진될 수 있습니다. API 요청 실패가 발생하며, 클라이언트 오류율이 1% 임계값을 초과합니다. 영향받는 클라이언트의 클러스터 운영이 불안정해집니다.

## 플레이북

1. kube-system 네임스페이스에서 component=kube-apiserver 레이블을 가진 Pod를 describe하여 상태, 오류율 및 클라이언트 연결에 영향을 미치는 서버 측 문제를 포함한 상세 API Server Pod 정보를 확인합니다.

2. kube-system 네임스페이스에서 마지막 타임스탬프 순으로 이벤트를 나열하여 최근 Control Plane 이벤트를 조회하고, 클라이언트 오류, 인증 실패 또는 속도 제한 이벤트를 필터링합니다.

3. API 클라이언트 오류 메트릭을 조회하고 1%를 초과하는 높은 오류율을 경험하는 클라이언트를 식별하여 문제 범위를 판단합니다.

4. `<namespace>` 네임스페이스의 클라이언트 Pod `<pod-name>`을 조회하고 클라이언트 Pod와 API Server 엔드포인트 간의 네트워크 연결성을 확인하여 연결 문제를 검증합니다.

5. 오류를 경험하는 `<namespace>` 네임스페이스의 Pod `<pod-name>`에서 로그를 조회하고 'connection refused', 'timeout', 'rate limited', 'authentication failed', 'authorization failed'를 포함한 API 오류 패턴을 필터링하여 오류 원인을 식별합니다.

6. 오류를 경험하는 클라이언트의 클라이언트 인증서를 포함하는 Secret 리소스와 ServiceAccount 리소스를 조회하고 클라이언트 인증서와 서비스 계정 토큰 유효성을 검증하여 인증 문제를 식별합니다.

7. API Server 메트릭에서 오류율과 지연을 조회하여 오류가 클라이언트 측인지 서버 측인지 판단하고 근본 원인 위치를 식별합니다.

8. `<namespace>` 네임스페이스의 ResourceQuota 리소스와 FlowSchema 리소스를 조회하고 클라이언트 API 접근에 영향을 미칠 수 있는 리소스 할당량과 속도 제한 구성을 검증합니다.

## 진단

1. 플레이북의 클라이언트 오류 이벤트를 분석하여 오류 패턴과 영향받는 클라이언트를 식별합니다. 이벤트에서 연결 거부, 타임아웃 또는 인증 오류가 나타나면, 이벤트 타임스탬프를 사용하여 오류 시작 시점과 영향받는 클라이언트를 판단합니다.

2. 이벤트에서 API Server 문제(오류, 지연)가 나타나면, 플레이북 1단계의 API Server 상태를 검증합니다. 클라이언트 오류와 상관관계가 있는 타임스탬프에서 API Server 이벤트가 문제를 보이면, 서버 측 문제가 근본 원인입니다.

3. 이벤트에서 인증 또는 인증서 실패가 나타나면, 플레이북 6단계의 클라이언트 인증서와 서비스 계정 토큰 유효성을 검증합니다. 인증서 관련 이벤트에서 만료 또는 검증 실패가 나타나면, 인증 문제가 클라이언트 오류를 유발하고 있습니다.

4. 이벤트에서 속도 제한 또는 Flow Control 거부가 나타나면, 플레이북 8단계의 API Server Flow Control 메트릭을 검토합니다. 클라이언트 오류 타임스탬프에서 Flow Control 이벤트가 거부를 보이면, 속도 제한이 실패를 유발하고 있습니다.

5. 이벤트에서 네트워크 연결 문제가 나타나면, 플레이북 4단계의 클라이언트에서 API Server까지의 네트워크 경로를 검증합니다. 오류 타임스탬프에서 네트워크 이벤트가 실패 또는 정책 변경을 보이면, 네트워크 문제가 근본 원인입니다.

6. 이벤트에서 일관된 오류 패턴(간헐적이 아닌)이 나타나면, 문제는 구성 문제일 가능성이 높습니다. 오류가 동일한 비율로 지속적으로 발생하면, 클라이언트 구성, 자격 증명 또는 API Server 용량을 조사합니다.

7. 이벤트에서 간헐적 오류 패턴이 나타나면, 일시적 원인에 집중합니다. 오류가 특정 시간대 또는 작업과 상관관계가 있으면, 네트워크 불안정, API Server 부하 또는 리소스 경합이 원인일 수 있습니다.

**연관 관계를 찾을 수 없는 경우**: 네트워크 변경에 대해 시간 범위를 1시간으로 확장하고, 클라이언트 API 사용 패턴을 검토하며, API Server 용량 문제를 확인하고, 클라이언트 라이브러리 버전을 검증하며, 과거 클라이언트 오류 패턴을 검토합니다. 클라이언트 오류는 즉각적인 변경보다 네트워크 불안정, API Server 용량 제한 또는 클라이언트 잘못된 구성으로 인해 발생할 수 있습니다.
